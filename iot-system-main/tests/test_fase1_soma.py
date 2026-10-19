"""Fase 1 – Soma com blocos arrastáveis (screens/fase1_screen.py)."""
import random
import unittest

from tests.helpers import (CORES, LARGURA, ALTURA, iniciar_pygame, novo_estado,
                           clique, tecla, rodar_frames)
import pygame
from screens import fase1_screen as f1


class TestGerarPergunta(unittest.TestCase):
    def test_resposta_e_a_soma_de_a_e_b(self):
        for _ in range(300):
            a, b, resp, _ = f1.gerar_pergunta()
            self.assertEqual(resp, a + b)

    def test_operandos_entre_1_e_9(self):
        for _ in range(300):
            a, b, _, _ = f1.gerar_pergunta()
            self.assertTrue(1 <= a <= 9 and 1 <= b <= 9)

    def test_quatro_opcoes_distintas_com_a_resposta(self):
        for _ in range(300):
            _, _, resp, opcoes = f1.gerar_pergunta()
            self.assertEqual(len(opcoes), 4)
            self.assertEqual(len(set(opcoes)), 4)
            self.assertIn(resp, opcoes)

    def test_opcoes_sao_positivas(self):
        for _ in range(300):
            _, _, _, opcoes = f1.gerar_pergunta()
            self.assertTrue(all(o > 0 for o in opcoes))

    def test_distratores_proximos_da_resposta(self):
        for _ in range(300):
            _, _, resp, opcoes = f1.gerar_pergunta()
            self.assertTrue(all(abs(o - resp) <= 3 for o in opcoes))


class TestAnswerSlot(unittest.TestCase):
    def setUp(self):
        iniciar_pygame()
        self.slot = f1.AnswerSlot(500, 300)

    def test_comeca_vazio(self):
        self.assertFalse(self.slot.filled)

    def test_bloco_com_centro_dentro_sobrepoe(self):
        bloco = f1.DragBlock(5, f1.LEGO_RED, 500, 300)
        self.assertTrue(self.slot.overlaps(bloco))

    def test_bloco_longe_nao_sobrepoe(self):
        bloco = f1.DragBlock(5, f1.LEGO_RED, 50, 50)
        self.assertFalse(self.slot.overlaps(bloco))


class TestDragBlock(unittest.TestCase):
    def setUp(self):
        iniciar_pygame()
        self.bloco = f1.DragBlock(7, f1.LEGO_BLUE, 100, 200)

    def test_estado_inicial(self):
        self.assertEqual((self.bloco.x, self.bloco.y), (100, 200))
        self.assertFalse(self.bloco.dragging)
        self.assertFalse(self.bloco.placed)

    def test_hit_dentro_e_fora(self):
        self.assertTrue(self.bloco.hit(110, 210))
        self.assertFalse(self.bloco.hit(10, 10))

    def test_hit_nas_bordas(self):
        self.assertTrue(self.bloco.hit(100, 200))
        self.assertTrue(self.bloco.hit(100 + f1.BLOCK_W, 200 + f1.BLOCK_H))
        self.assertFalse(self.bloco.hit(100 + f1.BLOCK_W + 1, 200))

    def test_return_home_restaura_posicao_e_solta(self):
        self.bloco.x, self.bloco.y, self.bloco.dragging = 900, 600, True
        self.bloco.return_home()
        self.assertEqual((self.bloco.x, self.bloco.y), (100, 200))
        self.assertFalse(self.bloco.dragging)


class TestNewRound(unittest.TestCase):
    def setUp(self):
        iniciar_pygame()

    def test_cria_quatro_blocos_com_uma_resposta_correta(self):
        a, b, correta, blocos, slot = f1.new_round()
        self.assertEqual(len(blocos), 4)
        self.assertEqual([bl.number for bl in blocos].count(correta), 1)
        self.assertEqual(correta, a + b)

    def test_blocos_nao_se_sobrepoem(self):
        _, _, _, blocos, _ = f1.new_round()
        retangulos = [pygame.Rect(b.x, b.y, f1.BLOCK_W, f1.BLOCK_H) for b in blocos]
        for i in range(4):
            for j in range(i + 1, 4):
                self.assertFalse(retangulos[i].colliderect(retangulos[j]))

    def test_slot_comeca_vazio(self):
        *_, slot = f1.new_round()
        self.assertFalse(slot.filled)


class TestFase1Screen(unittest.TestCase):
    def setUp(self):
        self.surf = iniciar_pygame()
        self.estado = novo_estado(1)
        self.tela = f1.Fase1Screen(self.surf, LARGURA, ALTURA, CORES, self.estado)

    # ----- helpers
    def _arrastar(self, bloco, destino_xy):
        """Simula pressionar no bloco, mover e soltar em destino_xy."""
        cx, cy = int(bloco.x) + 5, int(bloco.y) + 5
        self.tela.handle_events([
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(cx, cy), button=1),
            pygame.event.Event(pygame.MOUSEMOTION, pos=destino_xy, rel=(0, 0), buttons=(1, 0, 0)),
            pygame.event.Event(pygame.MOUSEBUTTONUP, pos=destino_xy, button=1),
        ])

    def _bloco(self, correto):
        return next(b for b in self.tela.blocks if (b.number == self.tela.correct) == correto)

    def _destino_slot(self):
        return (self.tela.slot.x + 10, self.tela.slot.y + 10)

    # ----- testes
    def test_estado_inicial(self):
        self.assertEqual(self.tela.round, 1)
        self.assertEqual(self.tela.pontos, 0)
        self.assertEqual(self.tela.max_rounds, 5)
        self.assertIsNone(self.tela.popup_erro)
        self.assertIsNone(self.tela.tela_acerto)

    def test_arrastar_bloco_correto_para_o_slot_pontua(self):
        self._arrastar(self._bloco(True), self._destino_slot())
        self.assertEqual(self.tela.pontos, 1)
        self.assertTrue(self.tela.slot.filled)
        self.assertIsNotNone(self.tela.tela_acerto)

    def test_bloco_correto_fica_encaixado_no_slot(self):
        bloco = self._bloco(True)
        self._arrastar(bloco, self._destino_slot())
        self.assertTrue(bloco.placed)
        self.assertEqual((bloco.x, bloco.y), (self.tela.slot.x, self.tela.slot.y))

    def test_bloco_errado_no_slot_volta_para_casa_e_mostra_erro(self):
        bloco = self._bloco(False)
        casa = (bloco.home_x, bloco.home_y)
        self._arrastar(bloco, self._destino_slot())
        self.assertEqual((bloco.x, bloco.y), casa)
        self.assertEqual(self.tela.pontos, 0)
        self.assertIsNotNone(self.tela.popup_erro)
        self.assertFalse(self.tela.slot.filled)

    def test_soltar_fora_do_slot_volta_para_casa_sem_penalidade(self):
        bloco = self._bloco(True)
        casa = (bloco.home_x, bloco.home_y)
        self._arrastar(bloco, (20, 20))
        self.assertEqual((bloco.x, bloco.y), casa)
        self.assertIsNone(self.tela.popup_erro)
        self.assertEqual(self.tela.pontos, 0)

    def test_popup_de_erro_some_depois_de_um_tempo(self):
        self._arrastar(self._bloco(False), self._destino_slot())
        rodar_frames(self.tela, 150)
        self.assertIsNone(self.tela.popup_erro)

    def test_nao_arrasta_enquanto_popup_de_erro_esta_visivel(self):
        self._arrastar(self._bloco(False), self._destino_slot())
        bloco = self._bloco(True)
        self._arrastar(bloco, self._destino_slot())
        self.assertEqual(self.tela.pontos, 0)

    def test_clique_na_tela_de_acerto_durante_a_animacao_e_ignorado(self):
        self._arrastar(self._bloco(True), self._destino_slot())
        self.tela.handle_events(clique(self.tela.tela_acerto.btn_rect.center))
        self.assertEqual(self.tela.round, 1)
        self.assertIsNotNone(self.tela.tela_acerto)

    def test_clicar_na_tela_de_acerto_avanca_para_a_proxima_rodada(self):
        self._arrastar(self._bloco(True), self._destino_slot())
        rodar_frames(self.tela, 15)  # espera a animação de entrada terminar
        self.tela.handle_events(clique(self.tela.tela_acerto.btn_rect.center))
        self.assertEqual(self.tela.round, 2)
        self.assertIsNone(self.tela.tela_acerto)
        self.assertFalse(self.tela.slot.filled)

    def test_ultima_rodada_correta_abre_popup_de_fase_concluida(self):
        self.tela.round = self.tela.max_rounds
        self._arrastar(self._bloco(True), self._destino_slot())
        self.assertIsNotNone(self.tela.fase_concluida)
        self.assertIsNone(self.tela.tela_acerto)

    def test_esc_volta_ao_mapa(self):
        self.tela.handle_events([tecla(pygame.K_ESCAPE)])
        self.assertEqual(self.estado["tela_atual"], "mapa")

    def test_botao_voltar_leva_ao_mapa(self):
        self.tela.handle_events(clique(self.tela.btn_voltar.rect.center))
        self.assertEqual(self.estado["tela_atual"], "mapa")

    def test_draw_nao_levanta_excecao_em_nenhum_estado(self):
        self.tela.draw()
        self._arrastar(self._bloco(False), self._destino_slot())
        self.tela.draw()
        self.tela.popup_erro = None
        self._arrastar(self._bloco(True), self._destino_slot())
        self.tela.draw()


if __name__ == "__main__":
    unittest.main()
