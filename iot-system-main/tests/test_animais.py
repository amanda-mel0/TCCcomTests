"""Quiz de Animais.

Existem DUAS versões do mesmo jogo no projeto:
  * screens/animal_screen.py  -> AnimalScreen (classe, importável e testável)
  * jogos/animals/animal_quiz.py -> script solto (abre janela e entra em laço
    infinito ao ser importado). Para testá-lo sem executá-lo, extraímos só as
    funções puras via AST.
Além disso, jogos/matematica/fase1.py é outro script solto (soma 3 + 5).
"""
import ast
import os
import random
import unittest

from tests.helpers import (CORES, LARGURA, ALTURA, RAIZ, iniciar_pygame,
                           novo_estado, clique, tecla)
import pygame
from screens import animal_screen as an


def _carregar_funcoes(caminho_relativo, nomes):
    """Compila apenas as funções `nomes` de um script, sem executar o resto."""
    caminho = os.path.join(RAIZ, caminho_relativo)
    with open(caminho, encoding="utf-8") as f:
        arvore = ast.parse(f.read())
    corpo = [n for n in arvore.body if isinstance(n, ast.FunctionDef) and n.name in nomes]
    ns = {"random": random}
    exec(compile(ast.Module(body=corpo, type_ignores=[]), caminho, "exec"), ns)
    return ns


def _correta(tela):
    animal = tela.animal_seq[tela.index]
    return {"pergunta1": str(len(animal["nome"])),
            "pergunta2": animal["nome"][0].upper(),
            "pergunta3": str(animal["patas"])}[tela.state]


def _responder(tela, certo=True):
    alvo = _correta(tela)
    botao = next(b for b in tela.buttons if (str(b.text) == alvo) == certo)
    tela.handle_events(clique(botao.rect.center))


def _passar_feedback(tela):
    tela.feedback_t0 = pygame.time.get_ticks() - 1000
    tela.update()


class TestButton(unittest.TestCase):
    def test_collidepoint(self):
        b = an.Button((10, 10, 100, 50), "4")
        self.assertTrue(b.collidepoint((50, 30)))
        self.assertFalse(b.collidepoint((500, 500)))

    def test_guarda_o_texto(self):
        self.assertEqual(an.Button((0, 0, 10, 10), 7).text, 7)


class TestOpcoesAnimalScreen(unittest.TestCase):
    def setUp(self):
        self.tela = an.AnimalScreen(iniciar_pygame(), LARGURA, ALTURA, CORES, novo_estado(1))

    def test_opcoes_numericas(self):
        for correto in range(0, 12):
            for _ in range(30):
                opts = self.tela._num_options(correto)
                self.assertEqual(len(set(opts)), 3)
                self.assertIn(correto, opts)
                self.assertTrue(all(o >= 0 for o in opts))

    def test_opcoes_de_letras(self):
        for letra in "gcep":
            for _ in range(30):
                opts = self.tela._letter_options(letra)
                self.assertEqual(len(set(opts)), 4)
                self.assertIn(letra, opts)


class TestFluxoAnimalScreen(unittest.TestCase):
    def setUp(self):
        self.estado = novo_estado(1)
        self.tela = an.AnimalScreen(iniciar_pygame(), LARGURA, ALTURA, CORES, self.estado)

    def test_estado_inicial(self):
        t = self.tela
        self.assertEqual((t.index, t.pontos, t.state), (0, 0, "pergunta1"))
        self.assertCountEqual([a["nome"] for a in t.animal_seq],
                              [a["nome"] for a in t.ANIMAIS])
        self.assertEqual(len(t.buttons), 3)

    def test_botoes_de_cada_etapa(self):
        t = self.tela
        animal = t.animal_seq[0]
        self.assertIn(str(len(animal["nome"])), [str(b.text) for b in t.buttons])
        t.state = "pergunta2"
        t.prepare_question()
        self.assertEqual(len(t.buttons), 4)
        self.assertIn(animal["nome"][0].upper(), [b.text for b in t.buttons])
        t.state = "pergunta3"
        t.prepare_question()
        self.assertIn(str(animal["patas"]), [str(b.text) for b in t.buttons])

    def test_resposta_certa_pontua(self):
        _responder(self.tela, True)
        self.assertEqual((self.tela.pontos, self.tela.feedback, self.tela.state),
                         (1, "acerto", "feedback"))

    def test_resposta_errada_nao_pontua(self):
        _responder(self.tela, False)
        self.assertEqual((self.tela.pontos, self.tela.feedback), (0, "erro"))

    def test_clique_com_botao_direito_e_ignorado(self):
        b = self.tela.buttons[0]
        self.tela.handle_events([pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=b.rect.center, button=3)])
        self.assertEqual(self.tela.state, "pergunta1")

    def test_cliques_durante_o_feedback_sao_ignorados(self):
        _responder(self.tela, True)
        self.tela.handle_events(clique(self.tela.buttons[0].rect.center))
        self.assertEqual(self.tela.pontos, 1)

    def test_nao_avanca_antes_de_900ms(self):
        _responder(self.tela, True)
        self.tela.update()
        self.assertEqual(self.tela.state, "feedback")

    def test_esc_e_voltar_levam_ao_mapa(self):
        self.tela.handle_events([tecla(pygame.K_ESCAPE)])
        self.assertEqual(self.estado["tela_atual"], "mapa")
        self.estado["tela_atual"] = "animais"
        self.tela.handle_events(clique(self.tela.btn_voltar.rect.center))
        self.assertEqual(self.estado["tela_atual"], "mapa")

    def test_draw_em_estados_diferentes(self):
        self.tela.draw()
        _responder(self.tela, False)
        self.tela.draw()


class TestSequenciaDeEtapasAnimalScreen(unittest.TestCase):
    """⚠ VERMELHOS no código atual – mesmo defeito da Fase 3: update() deduz a
    etapa respondida olhando o texto do primeiro botão."""

    def setUp(self):
        self.estado = novo_estado(1)
        self.tela = an.AnimalScreen(iniciar_pygame(), LARGURA, ALTURA, CORES, self.estado)

    def test_pergunta1_com_botao_errado_na_frente_vai_para_pergunta2(self):
        alvo = _correta(self.tela)
        self.tela.buttons.sort(key=lambda b: str(b.text) == alvo)
        _responder(self.tela, True)
        _passar_feedback(self.tela)
        self.assertEqual(self.tela.state, "pergunta2")

    def test_pergunta2_vai_para_pergunta3(self):
        self.tela.state = "pergunta2"
        self.tela.prepare_question()
        _responder(self.tela, True)
        _passar_feedback(self.tela)
        self.assertEqual(self.tela.state, "pergunta3")

    def test_pergunta3_vai_para_o_proximo_animal(self):
        self.tela.animal_seq[0] = {"nome": "gato", "patas": 4}
        self.tela.state = "pergunta3"
        self.tela.prepare_question()
        self.tela.buttons.sort(key=lambda b: str(b.text) != "4")
        _responder(self.tela, True)
        _passar_feedback(self.tela)
        self.assertEqual((self.tela.index, self.tela.state), (1, "pergunta1"))

    def test_jogo_completo_faz_as_tres_perguntas_de_cada_animal(self):
        for semente in range(5):
            random.seed(semente)
            estado = novo_estado(1)
            tela = an.AnimalScreen(iniciar_pygame(), LARGURA, ALTURA, CORES, estado)
            perguntas = 0
            for _ in range(60):
                if estado["tela_atual"] == "mapa":
                    break
                perguntas += 1
                _responder(tela, True)
                _passar_feedback(tela)
            with self.subTest(semente=semente):
                self.assertEqual(estado["tela_atual"], "mapa")  # terminou
                self.assertEqual(perguntas, 3 * len(tela.ANIMAIS))
                self.assertEqual(tela.pontos, 3 * len(tela.ANIMAIS))


class TestScriptAnimalQuiz(unittest.TestCase):
    """Funções puras de jogos/animals/animal_quiz.py (extraídas via AST)."""

    @classmethod
    def setUpClass(cls):
        cls.ns = _carregar_funcoes("jogos/animals/animal_quiz.py",
                                   {"escolhe_opcoes_numero", "escolhe_opcoes_letra"})

    def test_opcoes_numericas(self):
        for correto in range(0, 10):
            for _ in range(30):
                opts = self.ns["escolhe_opcoes_numero"](correto)
                self.assertEqual(len(set(opts)), 3)
                self.assertIn(correto, opts)
                self.assertTrue(all(o >= 0 for o in opts))

    def test_opcoes_de_letras(self):
        for letra in "gcep":
            for _ in range(30):
                opts = self.ns["escolhe_opcoes_letra"](letra)
                self.assertEqual(len(set(opts)), 4)
                self.assertIn(letra, opts)



class TestScriptMatematica(unittest.TestCase):
    """gerar_pergunta() de jogos/matematica/fase1.py (extraída via AST)."""

    @classmethod
    def setUpClass(cls):
        cls.ns = _carregar_funcoes("jogos/matematica/fase1.py", {"gerar_pergunta"})

    def gerar(self):
        return self.ns["gerar_pergunta"]()

    def test_pergunta_e_resposta_sao_coerentes(self):
        pergunta, resposta, _ = self.gerar()
        a, b = [int(x) for x in pergunta.replace("= ?", "").split("+")]
        self.assertEqual(a + b, resposta)

    def test_tres_alternativas_distintas_com_a_resposta(self):
        for _ in range(100):
            _, resposta, alternativas = self.gerar()
            self.assertEqual(len(alternativas), 3)
            self.assertEqual(len(set(alternativas)), 3)
            self.assertIn(resposta, alternativas)

    def test_alternativas_positivas(self):
        for _ in range(100):
            self.assertTrue(all(a > 0 for a in self.gerar()[2]))


if __name__ == "__main__":
    unittest.main()
