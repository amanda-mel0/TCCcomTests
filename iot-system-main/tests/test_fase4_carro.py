"""Fase 4 – Corrida Matemática (screens/fase4_screen.py)."""
import unittest

from tests.helpers import (CORES, LARGURA, ALTURA, iniciar_pygame, novo_estado,
                           clique, tecla, rodar_frames, esperar_popup,
                           clicar_resposta)
import pygame
from screens import fase4_screen as f4


class TestCarro(unittest.TestCase):
    def setUp(self):
        iniciar_pygame()
        self.carro = f4.Carro()

    def test_posicao_inicial_na_largada(self):
        self.assertEqual(self.carro.x, f4.CARRO_X_START)
        self.assertFalse(self.carro.chegou())

    def test_avanca_define_o_destino(self):
        self.carro.avanca(100)
        self.assertEqual(self.carro.target_x, f4.CARRO_X_START + 100)

    def test_avanca_nunca_passa_da_linha_de_chegada(self):
        self.carro.avanca(99999)
        self.assertEqual(self.carro.target_x, f4.FINISH_X)

    def test_update_chega_ao_destino_e_para(self):
        self.carro.avanca(300)
        for _ in range(60):
            self.carro.update()
        self.assertEqual(self.carro.x, f4.CARRO_X_START + 300)
        self.assertEqual(self.carro.speed, 0)

    def test_update_move_gradualmente_sem_pular_o_destino(self):
        self.carro.avanca(200)
        self.carro.update()
        self.assertGreater(self.carro.x, f4.CARRO_X_START)
        self.assertLess(self.carro.x, f4.CARRO_X_START + 200)

    def test_chegou_so_perto_da_linha_de_chegada(self):
        self.carro.x = f4.FINISH_X - 21
        self.assertFalse(self.carro.chegou())
        self.carro.x = f4.FINISH_X - 20
        self.assertTrue(self.carro.chegou())


class TestProblema(unittest.TestCase):
    def setUp(self):
        iniciar_pygame()
        self.p = f4.Problema()

    def test_texto_bate_com_a_resposta(self):
        for _ in range(500):
            self.p.regenera()
            self.assertEqual(eval(self.p.texto), self.p.resposta)

    def test_operacoes_sao_soma_ou_subtracao(self):
        for _ in range(200):
            self.p.regenera()
            self.assertRegex(self.p.texto, r"^\d+ [+-] \d+$")

    def test_resposta_sempre_positiva_e_pequena(self):
        for _ in range(500):
            self.p.regenera()
            self.assertTrue(1 <= self.p.resposta <= 10)

    def test_subtracao_nunca_da_negativo_nem_zero(self):
        for _ in range(500):
            self.p.regenera()
            if "-" in self.p.texto:
                self.assertGreater(self.p.a, self.p.b)

    def test_quatro_opcoes_distintas_positivas_com_a_resposta(self):
        for _ in range(500):
            self.p.regenera()
            self.assertEqual(len(self.p.opcoes), 4)
            self.assertEqual(len(set(self.p.opcoes)), 4)
            self.assertIn(self.p.resposta, self.p.opcoes)
            self.assertTrue(all(o > 0 for o in self.p.opcoes))

    def test_historico_limitado_a_15_itens(self):
        for _ in range(100):
            self.p.regenera()
        self.assertLessEqual(len(self.p.historico), 15)

    def test_evita_repetir_problema_recente(self):
        repetidos = 0
        for _ in range(300):
            anterior = f"{self.p.texto}={self.p.resposta}"
            self.p.regenera()
            repetidos += anterior == f"{self.p.texto}={self.p.resposta}"
        self.assertLess(repetidos, 30)  # a repetição seguida deve ser rara


class TestPopupRecompensa(unittest.TestCase):
    def setUp(self):
        iniciar_pygame()

    def test_so_ha_particulas_no_acerto(self):
        self.assertGreater(len(f4.PopupRecompensa(True).particles), 0)
        self.assertEqual(len(f4.PopupRecompensa(False).particles), 0)

    def test_finaliza_depois_da_duracao(self):
        p = f4.PopupRecompensa(True)
        for _ in range(p.duracao - 1):
            p.update()
        self.assertFalse(p.finalizado())
        p.update()
        self.assertTrue(p.finalizado())


class TestFase4Screen(unittest.TestCase):
    def setUp(self):
        self.surf = iniciar_pygame()
        self.estado = novo_estado(4)
        self.tela = f4.Fase4Screen(self.surf, LARGURA, ALTURA, CORES, self.estado)

    def _acertar(self):
        clicar_resposta(self.tela, "resposta", self.tela.problema.resposta, True)

    def _errar(self):
        clicar_resposta(self.tela, "resposta", self.tela.problema.resposta, False)

    def test_estado_inicial(self):
        t = self.tela
        self.assertEqual((t.pontos, t.acertos_consecutivos), (0, 0))
        self.assertIsNone(t.popup)
        self.assertEqual(len(t.botoes_resposta), 4)

    def test_botoes_cabem_na_tela_e_nao_se_sobrepoem(self):
        rects = [b["rect"] for b in self.tela.botoes_resposta]
        for r in rects:
            self.assertTrue(0 <= r.left and r.right <= LARGURA)
        for i in range(4):
            for j in range(i + 1, 4):
                self.assertFalse(rects[i].colliderect(rects[j]))

    def test_botoes_mostram_as_opcoes_do_problema(self):
        self.assertCountEqual([b["resposta"] for b in self.tela.botoes_resposta],
                              self.tela.problema.opcoes)

    def test_acerto_da_10_pontos_e_move_o_carro_100(self):
        self._acertar()
        self.assertEqual(self.tela.pontos, 10)
        self.assertEqual(self.tela.acertos_consecutivos, 1)
        self.assertEqual(self.tela.carro.target_x, f4.CARRO_X_START + 100)
        self.assertTrue(self.tela.popup.acertou)

    def test_acertos_consecutivos_aumentam_o_avanco(self):
        self._acertar()
        esperar_popup(self.tela)
        x1 = self.tela.carro.x
        self._acertar()
        self.assertEqual(self.tela.carro.target_x, x1 + 200)

    def test_erro_zera_a_sequencia_e_nao_move_o_carro(self):
        self._acertar()
        esperar_popup(self.tela)
        self._errar()
        self.assertEqual(self.tela.acertos_consecutivos, 0)
        self.assertEqual(self.tela.pontos, 10)
        self.assertFalse(self.tela.popup.acertou)
        self.assertEqual(self.tela.carro.target_x, f4.CARRO_X_START + 100)

    def test_clique_durante_popup_e_ignorado(self):
        self._acertar()
        self._acertar()
        self.assertEqual(self.tela.pontos, 10)

    def test_novo_problema_so_depois_do_popup(self):
        antigo = list(self.tela.problema.opcoes)
        self._acertar()
        self.tela.update()
        self.assertTrue(self.tela.regenerar_na_proxima)
        esperar_popup(self.tela)
        self.assertFalse(self.tela.regenerar_na_proxima)
        self.assertEqual(len(self.tela.botoes_resposta), 4)
        self.assertCountEqual([b["resposta"] for b in self.tela.botoes_resposta],
                              self.tela.problema.opcoes)

    def test_hover_acompanha_o_mouse(self):
        alvo = self.tela.botoes_resposta[1]["rect"].center
        self.tela.handle_events([pygame.event.Event(pygame.MOUSEMOTION, pos=alvo, rel=(0, 0), buttons=(0, 0, 0))])
        self.assertEqual([b["hover"] for b in self.tela.botoes_resposta], [False, True, False, False])

    def test_esc_e_voltar_levam_ao_mapa(self):
        self.tela.handle_events([tecla(pygame.K_ESCAPE)])
        self.assertEqual(self.estado["tela_atual"], "mapa")
        self.estado["tela_atual"] = "fase_4"
        self.tela.handle_events(clique(self.tela.btn_voltar.rect.center))
        self.assertEqual(self.estado["tela_atual"], "mapa")

    def test_quatro_acertos_seguidos_levam_o_carro_ate_a_chegada(self):
        for _ in range(4):
            self._acertar()
            esperar_popup(self.tela)
        self.assertTrue(self.tela.carro.chegou())

    def test_chegar_ao_fim_abre_o_popup_de_fase_concluida(self):
        """⚠ VERMELHO no código atual: o jogo checa carro.chegou() logo depois de
        avanca(), antes do carro andar – a conclusão só vem no acerto seguinte."""
        for _ in range(4):
            self._acertar()
            esperar_popup(self.tela)
        self.assertIsNotNone(self.tela.fase_concluida)

    def test_botao_do_popup_final_avanca_para_a_fase_5(self):
        self.estado["fase_atual"] = 4
        self.tela.fase_concluida = f4.PopupFaseConcluida(LARGURA, ALTURA, self.estado)
        self.tela.handle_events(clique(self.tela.fase_concluida.btn_rect.center))
        self.assertEqual(self.estado["tela_atual"], "fase_5")

    def test_draw_em_varios_estados(self):
        self.tela.draw()
        self._acertar()
        self.tela.draw()
        esperar_popup(self.tela)
        self._errar()
        self.tela.draw()


if __name__ == "__main__":
    unittest.main()
