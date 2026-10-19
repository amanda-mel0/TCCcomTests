"""Fase 10 – Complete a palavra com a sílaba que falta (screens/fase10_screen.py)."""
import unittest

from tests.helpers import (CORES, LARGURA, ALTURA, iniciar_pygame, novo_estado,
                           clique, tecla, esperar_popup, clicar_resposta)
import pygame
from screens import fase10_screen as f10

PALAVRAS = dict(f10.Problema.PALAVRAS)


class TestBancoDePalavras(unittest.TestCase):
    def test_silabas_formam_a_palavra(self):
        for palavra, silabas in f10.Problema.PALAVRAS:
            self.assertEqual("".join(silabas), palavra)

    def test_palavras_sem_repeticao(self):
        nomes = [p for p, _ in f10.Problema.PALAVRAS]
        self.assertEqual(len(nomes), len(set(nomes)))

    def test_palavras_de_no_maximo_duas_silabas(self):
        for _, silabas in f10.Problema.PALAVRAS:
            self.assertEqual(len(silabas), 2)


class TestProblema(unittest.TestCase):
    def setUp(self):
        iniciar_pygame()
        self.p = f10.Problema()

    def test_silaba_correta_e_a_da_posicao_da_lacuna(self):
        for _ in range(500):
            self.p.regenera()
            self.assertEqual(self.p.silaba_correta,
                             self.p.silabas_corretas[self.p.indice_lacuna])

    def test_palavra_e_silabas_sao_coerentes(self):
        for _ in range(300):
            self.p.regenera()
            self.assertEqual("".join(self.p.silabas_corretas), self.p.palavra)
            self.assertEqual(PALAVRAS[self.p.palavra], self.p.silabas_corretas)

    def test_indice_da_lacuna_valido_e_as_duas_posicoes_sao_sorteadas(self):
        indices = set()
        for _ in range(300):
            self.p.regenera()
            self.assertIn(self.p.indice_lacuna, range(len(self.p.silabas_corretas)))
            indices.add(self.p.indice_lacuna)
        self.assertEqual(indices, {0, 1})

    def test_quatro_opcoes_distintas_com_a_silaba_correta(self):
        for _ in range(500):
            self.p.regenera()
            self.assertEqual(len(self.p.opcoes), 4)
            self.assertEqual(len(set(self.p.opcoes)), 4)
            self.assertIn(self.p.silaba_correta, self.p.opcoes)

    def test_opcoes_vem_do_banco_de_silabas(self):
        todas = {s for _, ss in f10.Problema.PALAVRAS for s in ss}
        for _ in range(300):
            self.p.regenera()
            self.assertTrue(set(self.p.opcoes) <= todas)

    def test_so_uma_opcao_completa_uma_palavra_valida(self):
        """⚠ VERMELHO no código atual: por exemplo PATO com a lacuna no início aceita
        "GA" (GATO) e BOLA aceita "MA" (MALA) – duas respostas "certas"."""
        validas = set(PALAVRAS)
        for _ in range(1500):
            self.p.regenera()
            silabas = list(self.p.silabas_corretas)
            completam = []
            for op in self.p.opcoes:
                silabas[self.p.indice_lacuna] = op
                if "".join(silabas) in validas:
                    completam.append(op)
            self.assertEqual(
                completam, [self.p.silaba_correta],
                f"{self.p.palavra} (lacuna {self.p.indice_lacuna}) aceita {completam}")

    def test_historico_limitado_a_8(self):
        for _ in range(60):
            self.p.regenera()
        self.assertLessEqual(len(self.p.historico), 8)


class TestFoguinho(unittest.TestCase):
    def setUp(self):
        iniciar_pygame()
        self.f = f10.Foguinho()

    def test_avanca_limita_em_1_e_converge(self):
        self.f.avanca(0.8)
        self.f.avanca(0.8)
        self.assertEqual(self.f.alvo, 1.0)
        for _ in range(200):
            self.f.update()
        self.assertTrue(self.f.completo())

    def test_nao_completo_no_inicio(self):
        self.assertFalse(self.f.completo())


class TestFase10Screen(unittest.TestCase):
    def setUp(self):
        self.surf = iniciar_pygame()
        self.estado = novo_estado(10)
        self.tela = f10.Fase10Screen(self.surf, LARGURA, ALTURA, CORES, self.estado)

    def _acertar(self):
        clicar_resposta(self.tela, "silaba", self.tela.problema.silaba_correta, True)

    def _errar(self):
        clicar_resposta(self.tela, "silaba", self.tela.problema.silaba_correta, False)

    def test_botoes_mostram_as_opcoes(self):
        self.assertEqual(len(self.tela.botoes_resposta), 4)
        self.assertCountEqual([b["silaba"] for b in self.tela.botoes_resposta],
                              self.tela.problema.opcoes)

    def test_acerto_pontua_e_avanca_o_foguinho(self):
        self._acertar()
        self.assertEqual(self.tela.pontos, 10)
        self.assertAlmostEqual(self.tela.foguinho.alvo, 0.20)
        self.assertTrue(self.tela.popup.acertou)

    def test_erro_zera_a_sequencia_e_nao_pontua(self):
        self._acertar()
        esperar_popup(self.tela)
        self._errar()
        self.assertEqual(self.tela.acertos_consecutivos, 0)
        self.assertEqual(self.tela.pontos, 10)
        self.assertFalse(self.tela.popup.acertou)

    def test_clique_com_popup_aberto_e_ignorado(self):
        self._acertar()
        self._acertar()
        self.assertEqual(self.tela.pontos, 10)

    def test_novo_problema_apos_o_popup(self):
        self._errar()
        esperar_popup(self.tela)
        self.assertCountEqual([b["silaba"] for b in self.tela.botoes_resposta],
                              self.tela.problema.opcoes)

    def test_esc_e_voltar_levam_ao_mapa(self):
        self.tela.handle_events([tecla(pygame.K_ESCAPE)])
        self.assertEqual(self.estado["tela_atual"], "mapa")
        self.estado["tela_atual"] = "fase_10"
        self.tela.handle_events(clique(self.tela.btn_voltar.rect.center))
        self.assertEqual(self.estado["tela_atual"], "mapa")

    def test_chegar_ao_fim_abre_o_popup_de_fase_concluida(self):
        """⚠ VERMELHO no código atual: foguinho.completo() é consultado logo após
        avanca(), antes da animação – a conclusão só vem no acerto seguinte."""
        for _ in range(4):
            self._acertar()
            esperar_popup(self.tela)
        for _ in range(100):
            self.tela.update()
        self.assertIsNotNone(self.tela.fase_concluida)

    def test_na_ultima_fase_o_popup_leva_ao_jogo_concluido(self):
        self.estado["fase_atual"] = 10
        self.tela.fase_concluida = f10.PopupFaseConcluida(LARGURA, ALTURA, self.estado)
        self.assertEqual(self.tela.fase_concluida.texto_botao, "VER FINAL")
        self.tela.handle_events(clique(self.tela.fase_concluida.btn_rect.center))
        self.assertEqual(self.estado["tela_atual"], "jogo_concluido")

    def test_draw_em_varios_estados(self):
        self.tela.draw()
        self._acertar()
        self.tela.draw()


if __name__ == "__main__":
    unittest.main()
