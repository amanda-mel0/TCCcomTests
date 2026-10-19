
import unittest
from types import SimpleNamespace as Campo
from screens.cadastro_screen import CadastroScreen


class TestCadastro(unittest.TestCase):

    def setUp(self):
        self.tela = CadastroScreen.__new__(CadastroScreen)

        dados = {
            "inp_nome_resp": "Maria",
            "inp_email": "maria@email.com",
            "inp_senha": "123456",
            "inp_conf_senha": "123456",
            "inp_nome_cri": "Joao",
            "inp_apelido": "Joaozinho",
            "inp_nasc": "01/01/2018"
        }

        for nome, valor in dados.items():
            setattr(self.tela, nome, Campo(texto=valor, erro=False))

        for nome in ["chk_termos", "chk_privacidade", "chk_dados"]:
            setattr(self.tela, nome, Campo(marcado=True))

        self.tela.teclado = Campo(visible=False)
        self.tela.etapa = 0
        self.tela.scroll_y = 0
        self.tela.msg_erro = ""

    def test_nome_vazio(self):
        self.tela.inp_nome_resp.texto = ""
        self.tela._validar_etapa0()
        self.assertIn("Campo obrigatório", self.tela.msg_erro)

    def test_senhas_diferentes(self):
        self.tela.inp_conf_senha.texto = "654321"
        self.tela._validar_etapa0()
        self.assertEqual(self.tela.msg_erro, "As senhas não coincidem!")

    def test_senha_curta(self):
        self.tela.inp_senha.texto = "123"
        self.tela.inp_conf_senha.texto = "123"
        self.tela._validar_etapa0()
        self.assertIn("6 caracteres", self.tela.msg_erro)

    def test_termos(self):
        self.tela.chk_termos.marcado = False
        self.tela._validar_etapa0()
        self.assertIn("Termos de Uso", self.tela.msg_erro)

    def test_cadastro_valido(self):
        self.tela._validar_etapa0()
        self.assertEqual(self.tela.etapa, 1)


if __name__ == "__main__":
    unittest.main()
