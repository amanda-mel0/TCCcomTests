"""Interação entre os módulos: todas as telas de jogo seguem o mesmo contrato
(handle_events / update / draw), conversam com o `estado` global e se encadeiam
da fase 1 até a tela final."""
import random
import re
import unittest
from unittest import mock

from tests.helpers import (CORES, LARGURA, ALTURA, RAIZ, iniciar_pygame,
                           novo_estado, clique, tecla)
import pygame
from screens.fase1_screen import Fase1Screen
from screens.fase2_screen import Fase2Screen
from screens.fase3_screen import LogicaScreen
from screens.fase4_screen import Fase4Screen
from screens.fase5_screen import Fase5Screen
from screens.fase6_screen import Fase6Screen
from screens.fase7_screen import Fase7Screen
from screens.fase8_screen import Fase8Screen
from screens.fase9_screen import Fase9Screen
from screens.fase10_screen import Fase10Screen
from screens.animal_screen import AnimalScreen
from screens.jogo_concluido import JogoConcluidoScreen
from screens.fase_concluida import TOTAL_FASES, PopupFaseConcluida

FASES = [Fase1Screen, Fase2Screen, LogicaScreen, Fase4Screen, Fase5Screen,
         Fase6Screen, Fase7Screen, Fase8Screen, Fase9Screen, Fase10Screen]


class TestContratoDasTelas(unittest.TestCase):
    def setUp(self):
        self.surf = iniciar_pygame()

    def _telas(self, extras=()):
        for i, classe in enumerate(list(FASES) + list(extras), start=1):
            estado = novo_estado(min(i, 10))
            yield classe.__name__, estado, classe(self.surf, LARGURA, ALTURA, CORES, estado)

    def test_dez_fases_cadastradas_no_main(self):
        with open(f"{RAIZ}/main.py", encoding="utf-8") as f:
            chaves = set(re.findall(r'"fase_(\d+)":', f.read()))
        self.assertEqual(chaves, {str(i) for i in range(1, TOTAL_FASES + 1)})

    def test_toda_tela_tem_handle_events_update_e_draw(self):
        for nome, _, tela in self._telas([AnimalScreen, JogoConcluidoScreen]):
            for metodo in ("handle_events", "update", "draw"):
                self.assertTrue(callable(getattr(tela, metodo, None)), f"{nome}.{metodo}")

    def test_nenhuma_tela_quebra_ao_rodar_alguns_quadros(self):
        for nome, _, tela in self._telas([AnimalScreen, JogoConcluidoScreen]):
            with self.subTest(tela=nome):
                for _ in range(10):
                    tela.handle_events([])
                    tela.update()
                    tela.draw()

    def test_esc_leva_ao_mapa_em_todas_as_fases(self):
        for nome, estado, tela in self._telas():
            with self.subTest(tela=nome):
                tela.handle_events([tecla(pygame.K_ESCAPE)])
                self.assertEqual(estado["tela_atual"], "mapa")

    def test_botao_voltar_leva_ao_mapa_em_todas_as_fases(self):
        for nome, estado, tela in self._telas():
            with self.subTest(tela=nome):
                tela.handle_events(clique(tela.btn_voltar.rect.center))
                self.assertEqual(estado["tela_atual"], "mapa")

    def test_voltar_ao_mapa_nao_altera_a_fase_atual(self):
        for nome, estado, tela in self._telas():
            with self.subTest(tela=nome):
                antes = estado["fase_atual"]
                tela.handle_events([tecla(pygame.K_ESCAPE)])
                self.assertEqual(estado["fase_atual"], antes)

    def test_cliques_aleatorios_nao_quebram_nenhuma_fase(self):
        """Teste de robustez: 250 quadros de cliques aleatórios em cada tela,
        com um relógio falso a ~30 FPS (como no jogo real, FPS = 30)."""
        rng = random.Random(42)
        relogio = {"ms": 0}
        with mock.patch("pygame.time.get_ticks", lambda: relogio["ms"]):
            for nome, estado, tela in self._telas([AnimalScreen]):
                with self.subTest(tela=nome):
                    for _ in range(250):
                        relogio["ms"] += 33
                        pos = (rng.randint(0, LARGURA), rng.randint(0, ALTURA))
                        eventos = [
                            pygame.event.Event(pygame.MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(0, 0, 0)),
                            *clique(pos),
                        ]
                        tela.handle_events(eventos)
                        tela.update()
                        tela.draw()


class TestEncadeamentoDeFases(unittest.TestCase):
    """O popup 'FASE CONCLUÍDA' de cada jogo leva à fase seguinte."""

    def test_popup_de_cada_fase_avanca_para_a_proxima(self):
        surf = iniciar_pygame()
        for n, classe in enumerate(FASES, start=1):
            estado = novo_estado(n)
            tela = classe(surf, LARGURA, ALTURA, CORES, estado)
            tela.fase_concluida = PopupFaseConcluida(LARGURA, ALTURA, estado)
            with self.subTest(fase=n):
                tela.handle_events(clique(tela.fase_concluida.btn_rect.center))
                esperado = f"fase_{n + 1}" if n < TOTAL_FASES else "jogo_concluido"
                self.assertEqual(estado["tela_atual"], esperado)

    def test_tela_final_desenha_com_estado_de_fim_de_jogo(self):
        surf = iniciar_pygame()
        estado = novo_estado(10)
        estado["usuario"] = {"nome_crianca": "Lucas", "apelido": "Luc"}
        tela = JogoConcluidoScreen(surf, LARGURA, ALTURA, CORES, estado)
        for _ in range(5):
            tela.update()
        tela.draw()


if __name__ == "__main__":
    unittest.main()
