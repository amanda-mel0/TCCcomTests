"""Fase 6 – Contagem de blocos com foguete (screens/fase6_screen.py)."""
import unittest

from tests.helpers import (CORES, LARGURA, ALTURA, iniciar_pygame, novo_estado,
                           clique, tecla, esperar_popup, clicar_resposta)
import pygame
from screens import fase6_screen as f6


class TestFoguete(unittest.TestCase):
    def setUp(self):
        iniciar_pygame()
        self.f = f6.Foguete()

    def test_comeca_parado(self):
        self.assertEqual((self.f.progresso, self.f.alvo), (0.0, 0.0))
        self.assertFalse(self.f.completo())

    def test_avanca_acumula_e_limita_em_1(self):
        self.f.avanca(0.6)
        self.f.avanca(0.6)
        self.assertEqual(self.f.alvo, 1.0)

    def test_update_aproxima_do_alvo_sem_ultrapassar(self):
        self.f.avanca(0.5)
        for _ in range(300):
            self.f.update()
            self.assertLessEqual(self.f.progresso, 0.5 + 1e-9)
        self.assertAlmostEqual(self.f.progresso, 0.5, places=2)

    def test_completo_a_partir_de_97_por_cento(self):
        self.f.progresso = 0.969
        self.assertFalse(self.f.completo())
        self.f.progresso = 0.97
        self.assertTrue(self.f.completo())


class TestTorreBlocos(unittest.TestCase):
    def setUp(self):
        iniciar_pygame()

    def test_comeca_sem_blocos_visiveis(self):
        t = f6.TorreBlocos(5)
        self.assertEqual((t.quantidade, t.aparecidos), (5, 0))
        self.assertEqual(len(t.cores), 5)

    def test_blocos_aparecem_um_a_um_ate_a_quantidade(self):
        t = f6.TorreBlocos(3)
        for _ in range(8):
            t.update()
        self.assertEqual(t.aparecidos, 1)
        for _ in range(200):
            t.update()
        self.assertEqual(t.aparecidos, 3)

    def test_cores_pertencem_a_paleta(self):
        t = f6.TorreBlocos(8)
        self.assertTrue(all(c in f6.CORES_BLOCO for c in t.cores))

    def test_draw_nao_quebra_com_a_torre_cheia(self):
        t = f6.TorreBlocos(8)
        t.aparecidos = 8
        t.draw(pygame.Surface((LARGURA, ALTURA)))


class TestProblema(unittest.TestCase):
    def setUp(self):
        iniciar_pygame()
        self.p = f6.Problema()

    def test_quantidade_entre_2_e_8(self):
        for _ in range(500):
            self.p.regenera()
            self.assertTrue(2 <= self.p.quantidade <= 8)

    def test_quatro_opcoes_distintas_entre_1_e_12_com_a_quantidade(self):
        for _ in range(500):
            self.p.regenera()
            self.assertEqual(len(self.p.opcoes), 4)
            self.assertEqual(len(set(self.p.opcoes)), 4)
            self.assertIn(self.p.quantidade, self.p.opcoes)
            self.assertTrue(all(1 <= o <= 12 for o in self.p.opcoes))

    def test_historico_limitado_a_8(self):
        for _ in range(50):
            self.p.regenera()
        self.assertLessEqual(len(self.p.historico), 8)

    def test_evita_repetir_a_mesma_quantidade_em_sequencia(self):
        iguais = 0
        for _ in range(400):
            anterior = self.p.quantidade
            self.p.regenera()
            iguais += anterior == self.p.quantidade
        self.assertLess(iguais, 20)


class TestFase6Screen(unittest.TestCase):
    def setUp(self):
        self.surf = iniciar_pygame()
        self.estado = novo_estado(6)
        self.tela = f6.Fase6Screen(self.surf, LARGURA, ALTURA, CORES, self.estado)

    def _torre_pronta(self):
        self.tela.torre.aparecidos = self.tela.torre.quantidade

    def _acertar(self):
        self._torre_pronta()
        clicar_resposta(self.tela, "valor", self.tela.problema.quantidade, True)

    def _errar(self):
        self._torre_pronta()
        clicar_resposta(self.tela, "valor", self.tela.problema.quantidade, False)

    def test_torre_tem_a_quantidade_do_problema(self):
        self.assertEqual(self.tela.torre.quantidade, self.tela.problema.quantidade)

    def test_clique_e_ignorado_enquanto_a_torre_ainda_esta_aparecendo(self):
        self.tela.torre.aparecidos = 0
        clicar_resposta(self.tela, "valor", self.tela.problema.quantidade, True)
        self.assertEqual(self.tela.pontos, 0)
        self.assertIsNone(self.tela.popup)

    def test_acerto_da_10_pontos_e_avanca_o_foguete(self):
        self._acertar()
        self.assertEqual(self.tela.pontos, 10)
        self.assertAlmostEqual(self.tela.foguete.alvo, 0.20)
        self.assertTrue(self.tela.popup.acertou)

    def test_erro_zera_a_sequencia(self):
        self._acertar()
        esperar_popup(self.tela)
        self._errar()
        self.assertEqual(self.tela.acertos_consecutivos, 0)
        self.assertEqual(self.tela.pontos, 10)
        self.assertFalse(self.tela.popup.acertou)

    def test_nova_torre_e_novos_botoes_apos_o_popup(self):
        self._acertar()
        esperar_popup(self.tela)
        self.assertEqual(self.tela.torre.quantidade, self.tela.problema.quantidade)
        self.assertEqual(self.tela.torre.aparecidos, 0)
        self.assertCountEqual([b["valor"] for b in self.tela.botoes_resposta],
                              self.tela.problema.opcoes)

    def test_esc_e_voltar_levam_ao_mapa(self):
        self.tela.handle_events([tecla(pygame.K_ESCAPE)])
        self.assertEqual(self.estado["tela_atual"], "mapa")
        self.estado["tela_atual"] = "fase_6"
        self.tela.handle_events(clique(self.tela.btn_voltar.rect.center))
        self.assertEqual(self.estado["tela_atual"], "mapa")

    def test_chegar_ao_fim_abre_o_popup_de_fase_concluida(self):
        """⚠ VERMELHO no código atual: foguete.completo() é consultado logo após
        avanca(), antes da animação – a conclusão só vem no acerto seguinte."""
        for _ in range(4):
            self._acertar()
            esperar_popup(self.tela)
        for _ in range(100):
            self.tela.update()
        self.assertIsNotNone(self.tela.fase_concluida)

    def test_botao_do_popup_final_avanca_para_a_fase_7(self):
        self.estado["fase_atual"] = 6
        self.tela.fase_concluida = f6.PopupFaseConcluida(LARGURA, ALTURA, self.estado)
        self.tela.handle_events(clique(self.tela.fase_concluida.btn_rect.center))
        self.assertEqual(self.estado["tela_atual"], "fase_7")

    def test_draw_em_varios_estados(self):
        self.tela.draw()
        self._acertar()
        self.tela.draw()


if __name__ == "__main__":
    unittest.main()
