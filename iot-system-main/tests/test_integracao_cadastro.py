
import unittest
import tempfile
import os
from unittest.mock import patch

import firebase_auth
import firebase_mock


class TestIntegracaoCadastro(unittest.TestCase):

    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)

        arquivo = os.path.join(self.pasta.name, "usuarios.json")
        self.patch_arquivo = patch.object(
            firebase_mock, "USUARIOS_FILE", arquivo
        )
        self.patch_modo = patch.object(
            firebase_auth, "MODO_OFFLINE", True
        )

        self.patch_arquivo.start()
        self.patch_modo.start()
        self.addCleanup(self.patch_arquivo.stop)
        self.addCleanup(self.patch_modo.stop)

        self.dados = {
            "nome_responsavel": "Maria Silva",
            "email": "maria@email.com",
            "senha": "123456",
            "telefone": "75999999999",
            "nome_crianca": "Joao",
            "apelido": "Joaozinho",
            "data_nascimento": "01/01/2018",
            "aceite_termos": True,
            "aceite_privacidade": True,
            "aceite_dados_crianca": True
        }

    def test_cadastro_e_login(self):
        cadastro = firebase_auth.cadastrar(self.dados)
        self.assertTrue(cadastro["ok"])

        usuario = firebase_mock.get_usuario(cadastro["uid"])
        self.assertEqual(usuario["telefone"], "75999999999")

        login = firebase_auth.login("maria@email.com", "123456")
        self.assertTrue(login["ok"])
        self.assertEqual(login["uid"], cadastro["uid"])

    def test_email_duplicado(self):
        firebase_auth.cadastrar(self.dados)
        resultado = firebase_auth.cadastrar(self.dados)

        self.assertFalse(resultado["ok"])
        self.assertEqual(resultado["erro"], "E-mail já cadastrado!")

    def test_senha_incorreta(self):
        firebase_auth.cadastrar(self.dados)
        resultado = firebase_auth.login(
            "maria@email.com", "senha_errada"
        )

        self.assertFalse(resultado["ok"])


if __name__ == "__main__":
    unittest.main()
