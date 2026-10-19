
import unittest
import hashlib
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import firebase_auth
from screens.login_screen import LoginScreen


class TestLoginBanco(unittest.TestCase):

    def setUp(self):
        # Usuário simulado no banco de dados
        self.email = "teste@email.com"
        self.senha = "123456"

        senha_hash = hashlib.sha256(
            self.senha.encode()
        ).hexdigest()

        self.usuarios = {
            "usuario123": {
                "nome": "Usuario Teste",
                "email": self.email,
                "senha": senha_hash,
                "crianca": {
                    "apelido": "Joao",
                    "avatar": "Herói"
                }
            }
        }

        # Simula o banco de dados Firebase
        self.modo = patch.object(
            firebase_auth, "MODO_OFFLINE", False
        )
        self.inicializacao = patch.object(
            firebase_auth, "init_firebase"
        )
        self.banco = patch.object(
            firebase_auth, "db", create=True
        )

        self.modo.start()
        self.inicializacao.start()
        self.mock_db = self.banco.start()

        self.mock_db.reference.return_value.get.return_value = (
            self.usuarios
        )

        self.addCleanup(self.modo.stop)
        self.addCleanup(self.inicializacao.stop)
        self.addCleanup(self.banco.stop)

    def test_login_correto(self):
        resultado = firebase_auth.login(
            "teste@email.com",
            "123456"
        )

        self.assertTrue(resultado["ok"])
        self.assertEqual(resultado["uid"], "usuario123")
        self.assertEqual(resultado["nome"], "Usuario Teste")

    def test_senha_incorreta(self):
        resultado = firebase_auth.login(
            "teste@email.com",
            "senha_errada"
        )

        self.assertFalse(resultado["ok"])
        self.assertEqual(
            resultado["erro"],
            "E-mail ou senha incorretos!"
        )

    def test_email_nao_cadastrado(self):
        resultado = firebase_auth.login(
            "naoexiste@email.com",
            "123456"
        )

        self.assertFalse(resultado["ok"])

    def test_banco_vazio(self):
        self.mock_db.reference.return_value.get.return_value = {}

        resultado = firebase_auth.login(
            "teste@email.com",
            "123456"
        )

        self.assertFalse(resultado["ok"])


class TestTelaLogin(unittest.TestCase):

    def setUp(self):
        self.tela = LoginScreen.__new__(LoginScreen)

        self.tela.inp_email = SimpleNamespace(
            texto="", erro=False
        )
        self.tela.inp_senha = SimpleNamespace(
            texto="", erro=False
        )

        self.tela.msg_erro = ""
        self.tela.carregando = False

        self.tela.estado = {
            "tela_atual": "login"
        }

    def test_campos_vazios(self):
        self.tela._fazer_login()

        self.assertEqual(
            self.tela.msg_erro,
            "Preencha e-mail e senha!"
        )

    @patch("screens.login_screen.login")
    def test_redirecionamento_perfil(self, mock_login):
        mock_login.return_value = {
            "ok": True,
            "uid": "usuario123",
            "nome": "Usuario Teste"
        }

        self.tela.inp_email.texto = "teste@email.com"
        self.tela.inp_senha.texto = "123456"

        self.tela._fazer_login()

        self.assertEqual(
            self.tela.estado["tela_atual"],
            "perfil"
        )
        self.assertEqual(
            self.tela.estado["usuario"]["uid"],
            "usuario123"
        )

    @patch("screens.login_screen.login")
    def test_erro_na_tela(self, mock_login):
        mock_login.return_value = {
            "ok": False,
            "erro": "E-mail ou senha incorretos!"
        }

        self.tela.inp_email.texto = "teste@email.com"
        self.tela.inp_senha.texto = "errada"

        self.tela._fazer_login()

        self.assertEqual(
            self.tela.msg_erro,
            "E-mail ou senha incorretos!"
        )
        self.assertTrue(self.tela.inp_senha.erro)


if __name__ == "__main__":
    unittest.main()
