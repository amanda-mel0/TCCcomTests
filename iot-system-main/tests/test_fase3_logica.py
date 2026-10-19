"""Fase 3 – Quiz de lógica com animais (screens/fase3_screen.py → LogicaScreen).

Cada animal gera 3 perguntas em sequência:
  pergunta1 = quantas letras tem o nome, pergunta2 = com que letra começa,
  pergunta3 = quantas patas tem.
"""
import random
import unittest

from tests.helpers import (CORES, LARGURA, ALTURA, iniciar_pygame, novo_estado,
                           clique, tecla, rodar_frames)
import pygame
from screens import fase3_screen as f3


def _correta(tela):
    item = tela.seq[tela.index]
    return {"pergunta1": str(len(item["nome"])),
            "pergunta2": item["nome"][0].upper(),
            "pergunta3": str(item["patas"])}[tela.state]


def _responder(tela, certo=True, botao=None):
    """Clica numa resposta certa (ou errada) da pergunta atual."""
    alvo = _correta(tela)
    if botao is None:
        botao = next(b for b in tela.buttons if (str(b.texto) == alvo) == certo)
    tela.handle_events(clique(botao.rect.center))


def _passar_feedback(tela):
    tela.feedback_t0 = pygame.time.get_ticks() - 1000
    tela.update()


class TestOpcoes(unittest.TestCase):
    def setUp(self):
        self.tela = f3.LogicaScreen(iniciar_pygame(), LARGURA, ALTURA, CORES, novo_estado(3))

    def test_opcoes_numericas_tres_distintas_com_a_correta(self):
        for correto in range(0, 12):
            for _ in range(40):
                opts = self.tela._num_options(correto)
                self.assertEqual(len(opts), 3)
                self.assertEqual(len(set(opts)), 3)
                self.assertIn(correto, opts)

    def test_opcoes_numericas_nunca_sao_negativas(self):
        for correto in range(0, 5):
            for _ in range(100):
                self.assertTrue(all(o >= 0 for o in self.tela._num_options(correto)))

    def test_opcoes_de_letras_quatro_distintas_minusculas_com_a_correta(self):
        for letra in "gcep":
            for _ in range(40):
                opts = self.tela._letter_options(letra)
                self.assertEqual(len(opts), 4)
                self.assertEqual(len(set(opts)), 4)
                self.assertIn(letra, opts)
                self.assertTrue(all(o.islower() and len(o) == 1 for o in opts))

    def test_opcoes_de_letras_aceita_correta_maiuscula(self):
        opts = self.tela._letter_options("G")
        self.assertEqual(len(set(opts)), 4)
        self.assertIn("g", opts)


class TestPrepararPerguntas(unittest.TestCase):
    def setUp(self):
        self.tela = f3.LogicaScreen(iniciar_pygame(), LARGURA, ALTURA, CORES, novo_estado(3))

    def test_reset_estado_inicial(self):
        t = self.tela
        self.assertEqual((t.index, t.pontos, t.state), (0, 0, "pergunta1"))
        self.assertEqual(len(t.seq), len(t.ITEMS))
        self.assertCountEqual([i["nome"] for i in t.seq], [i["nome"] for i in t.ITEMS])
        self.assertIsNone(t.fase_concluida)

    def test_pergunta1_tres_botoes_com_o_tamanho_do_nome(self):
        t = self.tela
        textos = [b.texto for b in t.buttons]
        self.assertEqual(len(textos), 3)
        self.assertIn(str(len(t.seq[0]["nome"])), textos)

    def test_pergunta2_quatro_botoes_com_a_inicial_em_maiuscula(self):
        t = self.tela
        t.state = "pergunta2"
        t.prepare_question()
        textos = [b.texto for b in t.buttons]
        self.assertEqual(len(textos), 4)
        self.assertIn(t.seq[0]["nome"][0].upper(), textos)

    def test_pergunta3_tres_botoes_com_o_numero_de_patas(self):
        t = self.tela
        t.state = "pergunta3"
        t.prepare_question()
        textos = [b.texto for b in t.buttons]
        self.assertEqual(len(textos), 3)
        self.assertIn(str(t.seq[0]["patas"]), textos)

    def test_sem_animais_restantes_nao_cria_botoes(self):
        self.tela.index = len(self.tela.seq)
        self.tela.prepare_question()
        self.assertEqual(self.tela.buttons, [])

    def test_reset_quiz_reinicia_tudo(self):
        t = self.tela
        t.pontos, t.index, t.state = 5, 2, "pergunta3"
        t.reset_quiz()
        self.assertEqual((t.pontos, t.index, t.state), (0, 0, "pergunta1"))


class TestResposta(unittest.TestCase):
    def setUp(self):
        self.estado = novo_estado(3)
        self.tela = f3.LogicaScreen(iniciar_pygame(), LARGURA, ALTURA, CORES, self.estado)

    def test_resposta_certa_pontua_e_mostra_popup_de_acerto(self):
        _responder(self.tela, certo=True)
        self.assertEqual(self.tela.pontos, 1)
        self.assertEqual(self.tela.feedback, "acerto")
        self.assertEqual(self.tela.state, "feedback")
        self.assertTrue(self.tela.popup.success)

    def test_resposta_errada_nao_pontua_e_mostra_popup_de_erro(self):
        _responder(self.tela, certo=False)
        self.assertEqual(self.tela.pontos, 0)
        self.assertEqual(self.tela.feedback, "erro")
        self.assertFalse(self.tela.popup.success)

    def test_cliques_sao_ignorados_durante_o_feedback(self):
        _responder(self.tela, certo=True)
        self.tela.handle_events(clique(self.tela.buttons[0].rect.center))
        self.assertEqual(self.tela.pontos, 1)

    def test_feedback_nao_avanca_antes_de_900ms(self):
        _responder(self.tela, certo=True)
        self.tela.update()
        self.assertEqual(self.tela.state, "feedback")

    def test_esc_e_botao_voltar_levam_ao_mapa(self):
        self.tela.handle_events([tecla(pygame.K_ESCAPE)])
        self.assertEqual(self.estado["tela_atual"], "mapa")
        self.estado["tela_atual"] = "fase_3"
        self.tela.handle_events(clique(self.tela.btn_voltar.rect.center))
        self.assertEqual(self.estado["tela_atual"], "mapa")

    def test_draw_em_todos_os_estados(self):
        self.tela.draw()
        _responder(self.tela, certo=False)
        self.tela.draw()


class TestSequenciaDeEtapas(unittest.TestCase):
    """Garante que as etapas seguem pergunta1 → pergunta2 → pergunta3 → próximo
    animal, não importa a ordem em que os botões foram sorteados.

    ⚠ Estes testes começam VERMELHOS no código atual (TDD): update() descobre
    qual etapa acabou de ser respondida olhando para o texto do PRIMEIRO botão,
    o que só funciona por sorte. Veja o relatório.
    """

    def setUp(self):
        self.estado = novo_estado(3)
        self.tela = f3.LogicaScreen(iniciar_pygame(), LARGURA, ALTURA, CORES, self.estado)

    def _botao_errado_primeiro(self):
        alvo = _correta(self.tela)
        self.tela.buttons.sort(key=lambda b: str(b.texto) == alvo)  # errados antes

    def test_pergunta1_com_botao_errado_na_frente_vai_para_pergunta2(self):
        self._botao_errado_primeiro()
        _responder(self.tela, certo=True)
        _passar_feedback(self.tela)
        self.assertEqual(self.tela.state, "pergunta2")
        self.assertEqual(self.tela.index, 0)

    def test_pergunta1_com_botao_certo_na_frente_vai_para_pergunta2(self):
        alvo = _correta(self.tela)
        self.tela.buttons.sort(key=lambda b: str(b.texto) != alvo)  # certo primeiro
        _responder(self.tela, certo=True)
        _passar_feedback(self.tela)
        self.assertEqual(self.tela.state, "pergunta2")

    def test_pergunta2_vai_para_pergunta3(self):
        self.tela.state = "pergunta2"
        self.tela.prepare_question()
        _responder(self.tela, certo=True)
        _passar_feedback(self.tela)
        self.assertEqual(self.tela.state, "pergunta3")

    def test_pergunta3_vai_para_o_proximo_animal(self):
        # "gato": 4 letras e 4 patas -> o botão "4" serve para as duas perguntas
        self.tela.seq[0] = {"nome": "gato", "patas": 4}
        self.tela.state = "pergunta3"
        self.tela.prepare_question()
        self.tela.buttons.sort(key=lambda b: str(b.texto) != "4")  # "4" na frente
        _responder(self.tela, certo=True)
        _passar_feedback(self.tela)
        self.assertEqual(self.tela.index, 1)
        self.assertEqual(self.tela.state, "pergunta1")

    def _jogar_tudo(self, semente):
        random.seed(semente)
        tela = f3.LogicaScreen(iniciar_pygame(), LARGURA, ALTURA, CORES, novo_estado(3))
        perguntas = 0
        for _ in range(60):  # limite de segurança contra laço infinito
            if tela.fase_concluida:
                break
            perguntas += 1
            _responder(tela, certo=True)
            _passar_feedback(tela)
        return tela, perguntas

    def test_jogo_completo_termina_com_fase_concluida(self):
        for semente in range(5):
            tela, _ = self._jogar_tudo(semente)
            with self.subTest(semente=semente):
                self.assertIsNotNone(tela.fase_concluida)

    def test_jogo_completo_faz_as_tres_perguntas_de_cada_animal(self):
        for semente in range(5):
            tela, perguntas = self._jogar_tudo(semente)
            with self.subTest(semente=semente):
                self.assertEqual(perguntas, 3 * len(tela.ITEMS))
                self.assertEqual(tela.pontos, 3 * len(tela.ITEMS))

    def test_botao_do_popup_de_fase_concluida_avanca_para_a_fase_4(self):
        self.estado["fase_atual"] = 3
        self.tela.fase_concluida = f3.PopupFaseConcluida(LARGURA, ALTURA, self.estado)
        self.tela.handle_events(clique(self.tela.fase_concluida.btn_rect.center))
        self.assertEqual(self.estado["fase_atual"], 4)
        self.assertEqual(self.estado["tela_atual"], "fase_4")


if __name__ == "__main__":
    unittest.main()
