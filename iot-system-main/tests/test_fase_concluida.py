"""Módulo compartilhado screens/fase_concluida.py: progressão entre as fases."""
import unittest

from tests.helpers import LARGURA, ALTURA, iniciar_pygame, clique
import pygame
from screens import fase_concluida as fc


class TestGetFaseAtual(unittest.TestCase):
    def test_padrao_e_1_quando_nao_ha_fase(self):
        self.assertEqual(fc.get_fase_atual({}), 1)

    def test_none_e_zero_viram_1(self):
        self.assertEqual(fc.get_fase_atual({"fase_atual": None}), 1)
        self.assertEqual(fc.get_fase_atual({"fase_atual": 0}), 1)

    def test_aceita_inteiro_e_texto(self):
        self.assertEqual(fc.get_fase_atual({"fase_atual": 4}), 4)
        self.assertEqual(fc.get_fase_atual({"fase_atual": "7"}), 7)


class TestAvancarParaProximaFase(unittest.TestCase):
    def test_total_de_fases_e_10(self):
        self.assertEqual(fc.TOTAL_FASES, 10)

    def test_da_fase_1_para_a_2(self):
        e = {"fase_atual": 1, "tela_atual": "fase_1"}
        fc.avancar_para_proxima_fase(e)
        self.assertEqual((e["fase_atual"], e["tela_atual"]), (2, "fase_2"))

    def test_cada_fase_leva_a_seguinte(self):
        for n in range(1, 10):
            e = {"fase_atual": n}
            fc.avancar_para_proxima_fase(e)
            self.assertEqual((e["fase_atual"], e["tela_atual"]), (n + 1, f"fase_{n + 1}"))

    def test_da_ultima_fase_vai_para_jogo_concluido_sem_passar_de_10(self):
        e = {"fase_atual": 10}
        fc.avancar_para_proxima_fase(e)
        self.assertEqual((e["fase_atual"], e["tela_atual"]), (10, "jogo_concluido"))

    def test_sem_fase_no_estado_comeca_da_1(self):
        e = {}
        fc.avancar_para_proxima_fase(e)
        self.assertEqual(e["tela_atual"], "fase_2")

    def test_respeita_total_de_fases_customizado(self):
        e = {"fase_atual": 3}
        fc.avancar_para_proxima_fase(e, total_fases=3)
        self.assertEqual(e["tela_atual"], "jogo_concluido")

    def test_percorrer_o_jogo_inteiro(self):
        e = {"fase_atual": 1}
        telas = []
        for _ in range(10):
            fc.avancar_para_proxima_fase(e)
            telas.append(e["tela_atual"])
        self.assertEqual(telas, [f"fase_{i}" for i in range(2, 11)] + ["jogo_concluido"])


class TestTextoDeConclusao(unittest.TestCase):
    def test_fase_intermediaria(self):
        self.assertEqual(fc.get_phase_completion_text({"fase_atual": 5}),
                         ("FASE CONCLUÍDA!", "Próxima fase desbloqueada!", "PRÓXIMA FASE"))

    def test_ultima_fase(self):
        self.assertEqual(fc.get_phase_completion_text({"fase_atual": 10}),
                         ("FASE CONCLUÍDA!", "Todas as fases foram concluídas!", "VER FINAL"))


class TestPopupFaseConcluida(unittest.TestCase):
    def setUp(self):
        self.surf = iniciar_pygame()
        self.estado = {"fase_atual": 2}
        self.popup = fc.PopupFaseConcluida(LARGURA, ALTURA, self.estado)

    def test_clique_no_botao_retorna_true(self):
        self.assertTrue(self.popup.handle_event(clique(self.popup.btn_rect.center)[0]))

    def test_clique_fora_do_botao_retorna_false(self):
        self.assertFalse(self.popup.handle_event(clique((5, 5))[0]))

    def test_soltar_o_mouse_nao_conta(self):
        self.assertFalse(self.popup.handle_event(clique(self.popup.btn_rect.center)[1]))

    def test_botao_fica_centralizado(self):
        self.assertEqual(self.popup.btn_rect.centerx, LARGURA // 2)

    def test_draw_nao_levanta_excecao(self):
        self.popup.draw(self.surf)

    def test_sem_estado_usa_dicionario_vazio(self):
        self.assertEqual(fc.PopupFaseConcluida(LARGURA, ALTURA).texto_botao, "PRÓXIMA FASE")


if __name__ == "__main__":
    unittest.main()
