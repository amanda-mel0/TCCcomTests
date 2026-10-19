"""Fase 9 – Trenzinho de padrões de cores (screens/fase9_screen.py)."""
import unittest

from tests.helpers import (CORES, LARGURA, ALTURA, iniciar_pygame, novo_estado,
                           clique, tecla, esperar_popup, clicar_resposta)
import pygame
from screens import fase9_screen as f9


class TestPadroes(unittest.TestCase):
    def test_cores_aleatorias_distintas(self):
        for n in (2, 3):
            for _ in range(100):
                cores = f9._cores_aleatorias_distintas(n)
                self.assertEqual(len(cores), n)
                self.assertEqual(len(set(cores)), n)
                self.assertTrue(all(c in f9.CORES_BLOCO for c in cores))

    def test_padrao_abab(self):
        for _ in range(100):
            seq, resp = f9._padrao_abab()
            a, b = seq[0], seq[1]
            self.assertNotEqual(a, b)
            self.assertEqual(seq, [a, b, a, b, a])
            self.assertEqual(resp, b)

    def test_padrao_aab(self):
        for _ in range(100):
            seq, resp = f9._padrao_aab()
            a, b = seq[0], seq[2]
            self.assertNotEqual(a, b)
            self.assertEqual(seq, [a, a, b, a, a])
            self.assertEqual(resp, b)

    def test_padrao_abc(self):
        for _ in range(100):
            seq, resp = f9._padrao_abc()
            a, b, c = seq[0], seq[1], resp
            self.assertEqual(len({a, b, c}), 3)
            self.assertEqual(seq, [a, b, c, a, b])

    def test_padrao_abba_repete_o_bloco_abb(self):
        for _ in range(100):
            seq, resp = f9._padrao_abba()
            a, b = seq[0], seq[1]
            self.assertNotEqual(a, b)
            self.assertEqual(seq + [resp], [a, b, b, a, b, b])


class TestProblema(unittest.TestCase):
    def setUp(self):
        iniciar_pygame()
        self.p = f9.Problema()

    def test_sequencia_visivel_tem_5_cores_validas(self):
        for _ in range(300):
            self.p.regenera()
            self.assertEqual(len(self.p.sequencia), 5)
            self.assertTrue(all(c in f9.CORES_BLOCO for c in self.p.sequencia))

    def test_quatro_opcoes_distintas_com_a_resposta(self):
        for _ in range(300):
            self.p.regenera()
            self.assertEqual(len(self.p.opcoes), 4)
            self.assertEqual(len(set(self.p.opcoes)), 4)
            self.assertIn(self.p.resposta, self.p.opcoes)
            self.assertTrue(all(o in f9.CORES_BLOCO for o in self.p.opcoes))

    def test_historico_limitado_a_8(self):
        for _ in range(60):
            self.p.regenera()
        self.assertLessEqual(len(self.p.historico), 8)

    def test_todos_os_quatro_padroes_aparecem(self):
        formas = set()
        for _ in range(400):
            self.p.regenera()
            s = self.p.sequencia
            formas.add((s[0] == s[1], s[0] == s[2], len(set(s))))
        self.assertGreaterEqual(len(formas), 3)


class TestTrem(unittest.TestCase):
    def setUp(self):
        iniciar_pygame()
        self.t = f9.Trem()

    def test_avanca_limita_em_1_e_update_converge(self):
        self.t.avanca(0.7)
        self.t.avanca(0.7)
        self.assertEqual(self.t.alvo, 1.0)
        for _ in range(200):
            self.t.update()
        self.assertTrue(self.t.completo())

    def test_nao_completa_antes_de_97_por_cento(self):
        self.t.progresso = 0.96
        self.assertFalse(self.t.completo())

    def test_desenhar_bloco_com_e_sem_interrogacao(self):
        s = pygame.Surface((300, 300))
        f9.desenhar_bloco(s, 10, 10, f9.LEGO_RED)
        f9.desenhar_bloco(s, 10, 10, f9.LEGO_BLUE, mostrar_interrogacao=True,
                          font=pygame.font.SysFont("Arial", 40))


class TestFase9Screen(unittest.TestCase):
    def setUp(self):
        self.surf = iniciar_pygame()
        self.estado = novo_estado(9)
        self.tela = f9.Fase9Screen(self.surf, LARGURA, ALTURA, CORES, self.estado)

    def _acertar(self):
        clicar_resposta(self.tela, "cor_nome", self.tela.problema.resposta, True)

    def _errar(self):
        clicar_resposta(self.tela, "cor_nome", self.tela.problema.resposta, False)

    def test_estado_inicial(self):
        t = self.tela
        self.assertEqual((t.pontos, t.acertos_consecutivos), (0, 0))
        self.assertEqual(len(t.botoes_resposta), 4)

    def test_botoes_mostram_as_opcoes(self):
        self.assertCountEqual([b["cor_nome"] for b in self.tela.botoes_resposta],
                              self.tela.problema.opcoes)

    def test_acerto_pontua_e_avanca_o_trem(self):
        self._acertar()
        self.assertEqual(self.tela.pontos, 10)
        self.assertAlmostEqual(self.tela.trem.alvo, 0.20)
        self.assertTrue(self.tela.popup.acertou)

    def test_erro_zera_a_sequencia(self):
        self._acertar()
        esperar_popup(self.tela)
        self._errar()
        self.assertEqual(self.tela.acertos_consecutivos, 0)
        self.assertEqual(self.tela.pontos, 10)

    def test_clique_com_popup_aberto_e_ignorado(self):
        self._acertar()
        self._acertar()
        self.assertEqual(self.tela.pontos, 10)

    def test_novo_problema_apos_o_popup(self):
        self._errar()
        esperar_popup(self.tela)
        self.assertCountEqual([b["cor_nome"] for b in self.tela.botoes_resposta],
                              self.tela.problema.opcoes)

    def test_esc_e_voltar_levam_ao_mapa(self):
        self.tela.handle_events([tecla(pygame.K_ESCAPE)])
        self.assertEqual(self.estado["tela_atual"], "mapa")
        self.estado["tela_atual"] = "fase_9"
        self.tela.handle_events(clique(self.tela.btn_voltar.rect.center))
        self.assertEqual(self.estado["tela_atual"], "mapa")

    def test_chegar_ao_fim_abre_o_popup_de_fase_concluida(self):
        """⚠ VERMELHO no código atual: trem.completo() é consultado logo após
        avanca(), antes da animação – a conclusão só vem no acerto seguinte."""
        for _ in range(4):
            self._acertar()
            esperar_popup(self.tela)
        for _ in range(100):
            self.tela.update()
        self.assertIsNotNone(self.tela.fase_concluida)

    def test_botao_do_popup_final_avanca_para_a_fase_10(self):
        self.estado["fase_atual"] = 9
        self.tela.fase_concluida = f9.PopupFaseConcluida(LARGURA, ALTURA, self.estado)
        self.tela.handle_events(clique(self.tela.fase_concluida.btn_rect.center))
        self.assertEqual(self.estado["tela_atual"], "fase_10")

    def test_draw_em_varios_estados(self):
        self.tela.draw()
        self._acertar()
        self.tela.draw()


if __name__ == "__main__":
    unittest.main()
