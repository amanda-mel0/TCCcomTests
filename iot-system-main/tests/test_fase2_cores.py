"""Fase 2 – Clique na bola da cor pedida (screens/fase2_screen.py)."""
import random
import unittest

from tests.helpers import (CORES, LARGURA, ALTURA, iniciar_pygame, novo_estado,
                           clique, tecla, rodar_frames, esperar_popup)
import pygame
from screens import fase2_screen as f2


class TestBall(unittest.TestCase):
    def test_update_move_a_bola(self):
        b = f2.Ball((1, 2, 3), "azul", 500, 400, 3, -2)
        b.update()
        self.assertEqual((b.x, b.y), (503, 398))

    def test_quica_na_parede_esquerda(self):
        b = f2.Ball((1, 2, 3), "azul", f2.BALL_RADIUS + 1, 400, -5, 0)
        b.update()
        self.assertGreater(b.vx, 0)
        self.assertGreaterEqual(b.x - b.radius, 0)

    def test_quica_na_parede_direita(self):
        b = f2.Ball((1, 2, 3), "azul", f2.WIDTH - f2.BALL_RADIUS - 1, 400, 5, 0)
        b.update()
        self.assertLess(b.vx, 0)
        self.assertLessEqual(b.x + b.radius, f2.WIDTH)

    def test_quica_no_teto_abaixo_da_barra_de_titulo(self):
        b = f2.Ball((1, 2, 3), "azul", 500, 80 + f2.BALL_RADIUS + 1, 0, -5)
        b.update()
        self.assertGreater(b.vy, 0)
        self.assertGreaterEqual(b.y - b.radius, 80)

    def test_quica_no_chao(self):
        b = f2.Ball((1, 2, 3), "azul", 500, f2.HEIGHT - f2.BALL_RADIUS - 1, 0, 5)
        b.update()
        self.assertLess(b.vy, 0)
        self.assertLessEqual(b.y + b.radius, f2.HEIGHT)

    def test_bola_nunca_sai_da_area_jogavel(self):
        random.seed(1)
        for b in f2.spawn_balls():
            for _ in range(2000):
                b.update()
                self.assertGreaterEqual(b.x - b.radius, 0)
                self.assertLessEqual(b.x + b.radius, f2.WIDTH)
                self.assertGreaterEqual(b.y - b.radius, 80)
                self.assertLessEqual(b.y + b.radius, f2.HEIGHT)

    def test_is_clicked_dentro_e_fora(self):
        b = f2.Ball((1, 2, 3), "azul", 500, 400, 0, 0)
        self.assertTrue(b.is_clicked(500, 400))
        self.assertTrue(b.is_clicked(500 + f2.BALL_RADIUS, 400))
        self.assertFalse(b.is_clicked(500 + f2.BALL_RADIUS + 1, 400))


class TestSpawnBalls(unittest.TestCase):
    def test_gera_quatro_bolas_de_cores_distintas(self):
        for _ in range(100):
            bolas = f2.spawn_balls()
            self.assertEqual(len(bolas), 4)
            self.assertEqual(len({b.name for b in bolas}), 4)

    def test_sempre_inclui_a_bola_alvo(self):
        for nome, cor in f2.TARGET_OPTIONS:
            for _ in range(30):
                nomes = [b.name for b in f2.spawn_balls(nome, cor)]
                self.assertEqual(nomes.count(nome), 1)

    def test_bola_alvo_tem_a_cor_correta(self):
        nome, cor = f2.TARGET_OPTIONS[1]
        bola = next(b for b in f2.spawn_balls(nome, cor) if b.name == nome)
        self.assertEqual(bola.color, cor)

    def test_bolas_comecam_em_posicoes_diferentes(self):
        pos = [(b.x, b.y) for b in f2.spawn_balls()]
        self.assertEqual(len(set(pos)), 4)

    def test_velocidade_inicial_dentro_do_esperado(self):
        for b in f2.spawn_balls():
            v = (b.vx ** 2 + b.vy ** 2) ** 0.5
            self.assertAlmostEqual(v, f2.SPEED, delta=0.81)


class TestFase2Screen(unittest.TestCase):
    def setUp(self):
        self.surf = iniciar_pygame()
        self.estado = novo_estado(2)
        self.tela = f2.Fase2Screen(self.surf, LARGURA, ALTURA, CORES, self.estado)

    def _clicar_bola(self, correta):
        for b in self.tela.balls:
            if (b.name == self.tela.current_target_name) == correta:
                self.tela.handle_events(clique((int(b.x), int(b.y))))
                return b
        self.fail("bola não encontrada")

    def test_estado_inicial(self):
        self.assertEqual((self.tela.score, self.tela.misses, self.tela.round), (0, 0, 1))
        self.assertIsNone(self.tela.popup)
        self.assertEqual(len(self.tela.balls), 4)

    def test_alvo_esta_entre_as_bolas_da_tela(self):
        self.assertIn(self.tela.current_target_name, [b.name for b in self.tela.balls])

    def test_clicar_na_bola_certa_soma_ponto_e_mostra_popup_de_sucesso(self):
        self._clicar_bola(True)
        self.assertEqual(self.tela.score, 1)
        self.assertEqual(self.tela.misses, 0)
        self.assertTrue(self.tela.popup.success)

    def test_clicar_na_bola_errada_conta_erro_e_nao_pontua(self):
        self._clicar_bola(False)
        self.assertEqual(self.tela.score, 0)
        self.assertEqual(self.tela.misses, 1)
        self.assertFalse(self.tela.popup.success)

    def test_clicar_no_vazio_nao_faz_nada(self):
        for b in self.tela.balls:  # tira todas as bolas do canto superior esquerdo
            b.x, b.y = 900, 600
        self.tela.handle_events(clique((10, 100)))
        self.assertIsNone(self.tela.popup)

    def test_bolas_param_enquanto_o_popup_esta_aberto(self):
        self._clicar_bola(True)
        antes = [(b.x, b.y) for b in self.tela.balls]
        self.tela.update()
        self.assertEqual(antes, [(b.x, b.y) for b in self.tela.balls])

    def test_novo_clique_e_ignorado_com_popup_aberto(self):
        self._clicar_bola(True)
        self.tela.handle_events(clique((int(self.tela.balls[0].x), int(self.tela.balls[0].y))))
        self.assertEqual(self.tela.score + self.tela.misses, 1)

    def test_depois_do_popup_comeca_nova_rodada(self):
        self._clicar_bola(True)
        esperar_popup(self.tela)
        self.assertEqual(self.tela.round, 2)
        self.assertEqual(len(self.tela.balls), 4)

    def test_alvo_nunca_repete_em_rodadas_seguidas(self):
        random.seed(7)
        for _ in range(50):
            anterior = self.tela.current_target_name
            self.tela._choose_target()
            self.assertNotEqual(self.tela.current_target_name, anterior)

    def test_apos_a_quinta_rodada_abre_popup_de_fase_concluida(self):
        for _ in range(self.tela.max_rounds):
            self._clicar_bola(True)
            esperar_popup(self.tela)
        self.assertIsNotNone(self.tela.fase_concluida)
        self.assertEqual(self.tela.score, 5)
        self.assertEqual(self.tela.round, 5)

    def test_esc_volta_ao_mapa(self):
        self.tela.handle_events([tecla(pygame.K_ESCAPE)])
        self.assertEqual(self.estado["tela_atual"], "mapa")

    def test_botao_voltar_leva_ao_mapa(self):
        self.tela.handle_events(clique(self.tela.btn_voltar.rect.center))
        self.assertEqual(self.estado["tela_atual"], "mapa")

    def test_draw_funciona_com_e_sem_popup(self):
        self.tela.draw()
        self._clicar_bola(False)
        self.tela.draw()


if __name__ == "__main__":
    unittest.main()
