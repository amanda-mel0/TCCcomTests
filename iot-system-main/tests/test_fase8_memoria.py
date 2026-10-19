"""Fase 8 – Memória de cores (screens/fase8_screen.py)."""
import unittest

from tests.helpers import (CORES, LARGURA, ALTURA, iniciar_pygame, novo_estado,
                           clique, tecla, rodar_frames)
import pygame
from screens import fase8_screen as f8


class TestGenerateRound(unittest.TestCase):
    def test_tres_cores_distintas(self):
        for _ in range(500):
            r = f8.generate_round()
            nomes = [c["name"] for c in r["colors"]]
            self.assertEqual(len(nomes), 3)
            self.assertEqual(len(set(nomes)), 3)

    def test_posicao_valida_e_pergunta_coerente(self):
        for _ in range(300):
            r = f8.generate_round()
            self.assertIn(r["pos"], (0, 1, 2))
            self.assertEqual(r["question"], f8.POSITION_QUESTIONS[r["pos"]])

    def test_resposta_e_a_cor_da_posicao_perguntada(self):
        for _ in range(300):
            r = f8.generate_round()
            self.assertEqual(r["answer"], r["colors"][r["pos"]])

    def test_tres_opcoes_distintas_com_a_resposta(self):
        for _ in range(500):
            r = f8.generate_round()
            nomes = [o["name"] for o in r["options"]]
            self.assertEqual(len(nomes), 3)
            self.assertEqual(len(set(nomes)), 3)
            self.assertIn(r["answer"], r["options"])

    def test_todas_as_cores_pertencem_a_paleta(self):
        for _ in range(200):
            r = f8.generate_round()
            for c in r["colors"] + r["options"]:
                self.assertIn(c, f8.COLORS)

    def test_as_tres_posicoes_sao_sorteadas(self):
        posicoes = {f8.generate_round()["pos"] for _ in range(300)}
        self.assertEqual(posicoes, {0, 1, 2})


class TestGS(unittest.TestCase):
    def test_estado_inicial(self):
        gs = f8.GS()
        self.assertEqual(len(gs.rounds), f8.TOTAL_ROUNDS)
        self.assertEqual((gs.r_index, gs.score, gs.phase), (0, 0, "show"))
        self.assertEqual(gs.timer, 180)
        self.assertEqual(gs.round(), gs.rounds[0])

    def test_reset_gera_novas_rodadas_e_zera(self):
        gs = f8.GS()
        gs.score, gs.r_index, gs.phase = 4, 4, "end"
        gs.reset()
        self.assertEqual((gs.score, gs.r_index, gs.phase), (0, 0, "show"))


class TestFase8Screen(unittest.TestCase):
    def setUp(self):
        self.surf = iniciar_pygame()
        self.estado = novo_estado(8)
        self.tela = f8.Fase8Screen(self.surf, LARGURA, ALTURA, CORES, self.estado)

    # --- helpers
    def _ate_a_pergunta(self):
        rodar_frames(self.tela, f8.SHOW_FRAMES)
        rodar_frames(self.tela, 60)
        self.assertEqual(self.tela.gs.phase, "question")

    def _clicar_opcao(self, correto):
        r = self.tela.gs.round()
        i = next(i for i, o in enumerate(r["options"]) if (o == r["answer"]) == correto)
        rect = pygame.Rect(self.tela.OPT_X, self.tela.OPT_YS[i], self.tela.OPT_W, self.tela.OPT_H)
        self.tela.handle_events(clique(rect.center))

    def _jogar_rodada(self, correto=True):
        self._ate_a_pergunta()
        self._clicar_opcao(correto)
        rodar_frames(self.tela, self.tela.FB_FRAMES)

    # --- testes
    def test_comeca_mostrando_as_cores(self):
        self.assertEqual(self.tela.gs.phase, "show")

    def test_cores_somem_apos_3_segundos(self):
        rodar_frames(self.tela, f8.SHOW_FRAMES - 1)
        self.assertEqual(self.tela.gs.phase, "show")
        rodar_frames(self.tela, 1)
        self.assertEqual(self.tela.gs.phase, "hidden")

    def test_depois_de_1_segundo_oculto_aparece_a_pergunta(self):
        rodar_frames(self.tela, f8.SHOW_FRAMES)
        rodar_frames(self.tela, 59)
        self.assertEqual(self.tela.gs.phase, "hidden")
        rodar_frames(self.tela, 1)
        self.assertEqual(self.tela.gs.phase, "question")

    def test_clique_nas_opcoes_antes_da_pergunta_e_ignorado(self):
        rect = pygame.Rect(self.tela.OPT_X, self.tela.OPT_YS[0], self.tela.OPT_W, self.tela.OPT_H)
        self.tela.handle_events(clique(rect.center))
        self.assertIsNone(self.tela.gs.feedback)
        self.assertEqual(self.tela.gs.phase, "show")

    def test_resposta_certa_pontua_e_vai_para_feedback(self):
        self._ate_a_pergunta()
        self._clicar_opcao(True)
        self.assertEqual(self.tela.gs.feedback, "correct")
        self.assertEqual(self.tela.gs.score, 1)
        self.assertEqual(self.tela.gs.phase, "feedback")

    def test_resposta_errada_nao_pontua(self):
        self._ate_a_pergunta()
        self._clicar_opcao(False)
        self.assertEqual(self.tela.gs.feedback, "wrong")
        self.assertEqual(self.tela.gs.score, 0)

    def test_segundo_clique_durante_o_feedback_e_ignorado(self):
        self._ate_a_pergunta()
        self._clicar_opcao(True)
        self._clicar_opcao(True)
        self.assertEqual(self.tela.gs.score, 1)

    def test_fim_do_feedback_inicia_a_proxima_rodada_mostrando_cores(self):
        self._jogar_rodada(True)
        self.assertEqual(self.tela.gs.r_index, 1)
        self.assertEqual(self.tela.gs.phase, "show")
        self.assertEqual(self.tela.gs.timer, self.tela.SHOW_FRAMES)
        self.assertIsNone(self.tela.gs.feedback)

    def test_cinco_rodadas_certas_terminam_a_fase_com_placar_5(self):
        for _ in range(f8.TOTAL_ROUNDS):
            self._jogar_rodada(True)
        self.assertEqual(self.tela.gs.phase, "end")
        self.assertEqual(self.tela.gs.score, 5)
        self.assertIsNotNone(self.tela.fase_concluida)

    def test_espaco_no_fim_reinicia(self):
        for _ in range(f8.TOTAL_ROUNDS):
            self._jogar_rodada(False)
        self.tela.fase_concluida = None
        self.tela.handle_events([tecla(pygame.K_SPACE)])
        self.assertEqual((self.tela.gs.phase, self.tela.gs.score, self.tela.gs.r_index),
                         ("show", 0, 0))

    def test_esc_e_voltar_levam_ao_mapa(self):
        self.tela.handle_events([tecla(pygame.K_ESCAPE)])
        self.assertEqual(self.estado["tela_atual"], "mapa")
        self.estado["tela_atual"] = "fase_8"
        self.tela.handle_events(clique(self.tela.btn_voltar.rect.center))
        self.assertEqual(self.estado["tela_atual"], "mapa")

    def test_botao_do_popup_final_avanca_para_a_fase_9(self):
        self.estado["fase_atual"] = 8
        self.tela.fase_concluida = f8.PopupFaseConcluida(LARGURA, ALTURA, self.estado)
        self.tela.handle_events(clique(self.tela.fase_concluida.btn_rect.center))
        self.assertEqual(self.estado["tela_atual"], "fase_9")

    def test_draw_em_todas_as_fases_do_jogo(self):
        self.tela.draw()                      # show
        rodar_frames(self.tela, f8.SHOW_FRAMES)
        self.tela.draw()                      # hidden
        rodar_frames(self.tela, 60)
        self.tela.draw()                      # question
        self._clicar_opcao(True)
        self.tela.draw()                      # feedback


if __name__ == "__main__":
    unittest.main()
