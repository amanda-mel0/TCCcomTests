"""Fase 5 – Balão das Letras: letra inicial da palavra (screens/fase5_screen.py)."""
import unittest

from tests.helpers import (CORES, LARGURA, ALTURA, iniciar_pygame, novo_estado,
                           clique, tecla, esperar_popup, clicar_resposta)
import pygame
from screens import fase5_screen as f5


class TestBalao(unittest.TestCase):
    def setUp(self):
        iniciar_pygame()
        self.balao = f5.Balao()

    def test_comeca_na_base(self):
        self.assertEqual(self.balao.altura_relativa, 0.0)
        self.assertEqual(self.balao.y, f5.TRILHA_BASE)
        self.assertFalse(self.balao.chegou())

    def test_sobe_acumula_e_limita_em_1(self):
        self.balao.sobe(0.4)
        self.balao.sobe(0.4)
        self.assertAlmostEqual(self.balao.altura_alvo, 0.8)
        self.balao.sobe(0.9)
        self.assertEqual(self.balao.altura_alvo, 1.0)

    def test_update_aproxima_suavemente_do_alvo(self):
        self.balao.sobe(0.5)
        self.balao.update()
        self.assertGreater(self.balao.altura_relativa, 0)
        self.assertLess(self.balao.altura_relativa, 0.5)
        for _ in range(200):
            self.balao.update()
        self.assertAlmostEqual(self.balao.altura_relativa, 0.5, places=2)

    def test_y_fica_entre_o_topo_e_a_base_da_trilha(self):
        self.balao.sobe(1.0)
        for _ in range(300):
            self.balao.update()
            self.assertTrue(f5.TRILHA_TOPO <= self.balao.y <= f5.TRILHA_BASE)

    def test_chegou_quando_altura_passa_de_97_por_cento(self):
        self.balao.altura_relativa = 0.96
        self.assertFalse(self.balao.chegou())
        self.balao.altura_relativa = 0.97
        self.assertTrue(self.balao.chegou())


class TestProblema(unittest.TestCase):
    def setUp(self):
        iniciar_pygame()
        self.p = f5.Problema()

    def test_letra_correta_e_a_inicial_da_palavra(self):
        for palavra, letra, _ in f5.Problema.PALAVRAS:
            self.assertEqual(palavra[0], letra)

    def test_banco_de_palavras_sem_repeticao(self):
        palavras = [p[0] for p in f5.Problema.PALAVRAS]
        self.assertEqual(len(palavras), len(set(palavras)))

    def test_quatro_opcoes_distintas_com_a_letra_correta(self):
        for _ in range(500):
            self.p.regenera()
            self.assertEqual(len(self.p.opcoes), 4)
            self.assertEqual(len(set(self.p.opcoes)), 4)
            self.assertIn(self.p.letra_correta, self.p.opcoes)

    def test_opcoes_sao_letras_maiusculas(self):
        for _ in range(200):
            self.p.regenera()
            self.assertTrue(all(len(o) == 1 and o.isupper() for o in self.p.opcoes))

    def test_distratores_nao_sao_inicial_de_outra_palavra_igual(self):
        """Só UMA opção pode ser a inicial correta da palavra mostrada."""
        for _ in range(300):
            self.p.regenera()
            corretas = [o for o in self.p.opcoes if self.p.palavra.startswith(o)]
            self.assertEqual(corretas, [self.p.letra_correta])

    def test_nao_repete_palavra_em_sequencia_curta(self):
        iguais = 0
        for _ in range(300):
            anterior = self.p.palavra
            self.p.regenera()
            iguais += anterior == self.p.palavra
        self.assertLess(iguais, 10)

    def test_historico_limitado_a_8(self):
        for _ in range(50):
            self.p.regenera()
        self.assertLessEqual(len(self.p.historico), 8)

    def test_toda_palavra_tem_desenho_ou_fallback_sem_erro(self):
        superficie = pygame.Surface((300, 300))
        for _, _, desenho in f5.Problema.PALAVRAS:
            f5.Letra.desenhar(superficie, desenho, 150, 150)


class TestFase5Screen(unittest.TestCase):
    def setUp(self):
        self.surf = iniciar_pygame()
        self.estado = novo_estado(5)
        self.tela = f5.Fase5Screen(self.surf, LARGURA, ALTURA, CORES, self.estado)

    def _acertar(self):
        clicar_resposta(self.tela, "letra", self.tela.problema.letra_correta, True)

    def _errar(self):
        clicar_resposta(self.tela, "letra", self.tela.problema.letra_correta, False)

    def test_estado_inicial(self):
        t = self.tela
        self.assertEqual((t.pontos, t.acertos_consecutivos), (0, 0))
        self.assertEqual(len(t.botoes_resposta), 4)
        self.assertIsNone(t.popup)

    def test_botoes_mostram_as_opcoes(self):
        self.assertCountEqual([b["letra"] for b in self.tela.botoes_resposta],
                              self.tela.problema.opcoes)

    def test_acerto_da_10_pontos_e_sobe_o_balao_20_por_cento(self):
        self._acertar()
        self.assertEqual(self.tela.pontos, 10)
        self.assertAlmostEqual(self.tela.balao.altura_alvo, 0.20)
        self.assertTrue(self.tela.popup.acertou)

    def test_bonus_de_sequencia_ate_3_acertos(self):
        esperados = [0.20, 0.25, 0.30]
        alvo = 0.0
        for inc in esperados[:3]:
            self._acertar()
            alvo += inc
            self.assertAlmostEqual(self.tela.balao.altura_alvo, alvo)
            esperar_popup(self.tela)

    def test_erro_zera_sequencia_e_nao_sobe(self):
        self._acertar()
        esperar_popup(self.tela)
        self._errar()
        self.assertEqual(self.tela.acertos_consecutivos, 0)
        self.assertEqual(self.tela.pontos, 10)
        self.assertAlmostEqual(self.tela.balao.altura_alvo, 0.20)
        self.assertFalse(self.tela.popup.acertou)

    def test_clique_com_popup_aberto_e_ignorado(self):
        self._acertar()
        self._acertar()
        self.assertEqual(self.tela.pontos, 10)

    def test_nova_palavra_depois_do_popup(self):
        self._errar()
        esperar_popup(self.tela)
        self.assertFalse(self.tela.regenerar_na_proxima)
        self.assertCountEqual([b["letra"] for b in self.tela.botoes_resposta],
                              self.tela.problema.opcoes)

    def test_esc_e_voltar_levam_ao_mapa(self):
        self.tela.handle_events([tecla(pygame.K_ESCAPE)])
        self.assertEqual(self.estado["tela_atual"], "mapa")
        self.estado["tela_atual"] = "fase_5"
        self.tela.handle_events(clique(self.tela.btn_voltar.rect.center))
        self.assertEqual(self.estado["tela_atual"], "mapa")

    def test_quatro_acertos_seguidos_levam_o_balao_ao_topo(self):
        for _ in range(4):
            self._acertar()
            esperar_popup(self.tela)
        for _ in range(100):
            self.tela.update()
        self.assertTrue(self.tela.balao.chegou())

    def test_chegar_ao_topo_abre_o_popup_de_fase_concluida(self):
        """⚠ VERMELHO no código atual: balao.chegou() é consultado logo após sobe(),
        antes da animação, então a conclusão só vem no acerto seguinte."""
        for _ in range(4):
            self._acertar()
            esperar_popup(self.tela)
        for _ in range(100):
            self.tela.update()
        self.assertIsNotNone(self.tela.fase_concluida)

    def test_botao_do_popup_final_avanca_para_a_fase_6(self):
        self.estado["fase_atual"] = 5
        self.tela.fase_concluida = f5.PopupFaseConcluida(LARGURA, ALTURA, self.estado)
        self.tela.handle_events(clique(self.tela.fase_concluida.btn_rect.center))
        self.assertEqual(self.estado["tela_atual"], "fase_6")

    def test_draw_em_varios_estados(self):
        self.tela.draw()
        self._acertar()
        self.tela.draw()


if __name__ == "__main__":
    unittest.main()
