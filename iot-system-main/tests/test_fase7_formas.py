"""Fase 7 – Quiz de formas geométricas (screens/fase7_screen.py)."""
import unittest

from tests.helpers import (CORES, LARGURA, ALTURA, iniciar_pygame, novo_estado,
                           clique, tecla, rodar_frames)
import pygame
from screens import fase7_screen as f7


class TestBancoDeQuestoes(unittest.TestCase):
    def test_quatro_questoes(self):
        self.assertEqual(len(f7.QUESTIONS), 4)

    def test_cada_questao_tem_quatro_formas_distintas(self):
        for q in f7.QUESTIONS:
            nomes = [s["name"] for s in q["shapes"]]
            self.assertEqual(len(nomes), 4)
            self.assertEqual(len(set(nomes)), 4)

    def test_resposta_esta_exatamente_uma_vez_entre_as_formas(self):
        for q in f7.QUESTIONS:
            nomes = [s["name"] for s in q["shapes"]]
            self.assertEqual(nomes.count(q["answer"]), 1)

    def test_pergunta_cita_a_forma_da_resposta(self):
        sem_acento = str.maketrans("ÂÃÁÉÍÓÔÚÇ", "AAAEIOOUC")
        for q in f7.QUESTIONS:
            texto = q["question"].upper().translate(sem_acento)
            self.assertIn(q["answer"].upper(), texto)

    def test_cada_forma_e_pedida_uma_unica_vez(self):
        respostas = [q["answer"] for q in f7.QUESTIONS]
        self.assertEqual(len(set(respostas)), 4)


class TestGS(unittest.TestCase):
    def setUp(self):
        self.gs = f7.GS()

    def test_estado_inicial(self):
        self.assertEqual((self.gs.q_index, self.gs.score, self.gs.phase),
                         (0, 0, "playing"))
        self.assertIsNone(self.gs.feedback)
        self.assertEqual(self.gs.selected, -1)

    def test_embaralha_sem_perder_nem_repetir_questoes(self):
        self.assertCountEqual([q["answer"] for q in self.gs.questions],
                              [q["answer"] for q in f7.QUESTIONS])

    def test_shuffle_mantem_as_mesmas_quatro_formas(self):
        self.gs.shuffle()
        self.assertCountEqual([s["name"] for s in self.gs.current_shapes],
                              [s["name"] for s in self.gs.current_q()["shapes"]])

    def test_reset_zera_placar_e_fase(self):
        self.gs.score, self.gs.q_index, self.gs.phase = 3, 3, "end"
        self.gs.reset()
        self.assertEqual((self.gs.score, self.gs.q_index, self.gs.phase), (0, 0, "playing"))


class TestFase7Screen(unittest.TestCase):
    def setUp(self):
        self.surf = iniciar_pygame()
        self.estado = novo_estado(7)
        self.tela = f7.Fase7Screen(self.surf, LARGURA, ALTURA, CORES, self.estado)

    def _indice(self, correto):
        gs = self.tela.gs
        resposta = gs.current_q()["answer"]
        return next(i for i, s in enumerate(gs.current_shapes)
                    if (s["name"] == resposta) == correto)

    def _clicar(self, correto):
        rect = self.tela._get_rects()[self._indice(correto)]
        self.tela.handle_events(clique(rect.center))

    def _esperar_feedback(self):
        rodar_frames(self.tela, 95)

    def test_grade_2x2_sem_sobreposicao(self):
        rects = self.tela._get_rects()
        self.assertEqual(len(rects), 4)
        for i in range(4):
            for j in range(i + 1, 4):
                self.assertFalse(rects[i].colliderect(rects[j]))

    def test_clicar_na_forma_certa_pontua(self):
        self._clicar(True)
        self.assertEqual(self.tela.gs.feedback, "correct")
        self.assertEqual(self.tela.gs.score, 1)

    def test_clicar_na_forma_errada_nao_pontua(self):
        self._clicar(False)
        self.assertEqual(self.tela.gs.feedback, "wrong")
        self.assertEqual(self.tela.gs.score, 0)

    def test_clique_em_outro_lugar_nao_responde(self):
        self.tela.handle_events(clique((5, 5)))
        self.assertIsNone(self.tela.gs.feedback)

    def test_segundo_clique_durante_o_feedback_e_ignorado(self):
        self._clicar(True)
        self._clicar(True)
        self.assertEqual(self.tela.gs.score, 1)

    def test_depois_do_feedback_vai_para_a_proxima_questao(self):
        self._clicar(True)
        self._esperar_feedback()
        self.assertEqual(self.tela.gs.q_index, 1)
        self.assertIsNone(self.tela.gs.feedback)
        self.assertEqual(self.tela.gs.selected, -1)

    def test_quatro_acertos_terminam_a_fase(self):
        for _ in range(4):
            self._clicar(True)
            self._esperar_feedback()
        self.assertEqual(self.tela.gs.phase, "end")
        self.assertEqual(self.tela.gs.score, 4)
        self.assertIsNotNone(self.tela.fase_concluida)

    def test_errar_tudo_tambem_termina_com_placar_zero(self):
        for _ in range(4):
            self._clicar(False)
            self._esperar_feedback()
        self.assertEqual(self.tela.gs.phase, "end")
        self.assertEqual(self.tela.gs.score, 0)

    def test_espaco_no_fim_reinicia_o_quiz(self):
        for _ in range(4):
            self._clicar(True)
            self._esperar_feedback()
        self.tela.fase_concluida = None  # popup fechado
        self.tela.handle_events([tecla(pygame.K_SPACE)])
        self.assertEqual((self.tela.gs.phase, self.tela.gs.score, self.tela.gs.q_index),
                         ("playing", 0, 0))

    def test_espaco_no_meio_do_jogo_nao_reinicia(self):
        self._clicar(True)
        self._esperar_feedback()
        self.tela.handle_events([tecla(pygame.K_SPACE)])
        self.assertEqual(self.tela.gs.q_index, 1)

    def test_esc_e_voltar_levam_ao_mapa(self):
        self.tela.handle_events([tecla(pygame.K_ESCAPE)])
        self.assertEqual(self.estado["tela_atual"], "mapa")
        self.estado["tela_atual"] = "fase_7"
        self.tela.handle_events(clique(self.tela.btn_voltar.rect.center))
        self.assertEqual(self.estado["tela_atual"], "mapa")

    def test_botao_do_popup_final_avanca_para_a_fase_8(self):
        self.estado["fase_atual"] = 7
        self.tela.fase_concluida = f7.PopupFaseConcluida(LARGURA, ALTURA, self.estado)
        self.tela.handle_events(clique(self.tela.fase_concluida.btn_rect.center))
        self.assertEqual(self.estado["tela_atual"], "fase_8")

    def test_draw_em_todos_os_estados(self):
        self.tela.draw()
        self._clicar(True)
        self.tela.draw()
        self._esperar_feedback()
        for _ in range(3):
            self._clicar(True)
            self._esperar_feedback()
        self.tela.draw()  # tela final


if __name__ == "__main__":
    unittest.main()
