"""Utilitários compartilhados pelos testes dos jogos do Ler Brincando.

Os testes rodam sem janela e sem áudio (drivers "dummy" do SDL), então podem
ser executados em qualquer computador ou servidor de CI.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import pygame  # noqa: E402

LARGURA, ALTURA = 1100, 700

# Mesma paleta usada no main.py
CORES = {
    "vermelho": (220, 38, 38), "azul": (37, 99, 235), "verde": (34, 197, 94),
    "amarelo": (234, 179, 8), "laranja": (249, 115, 22), "roxo": (147, 51, 234),
    "branco": (255, 255, 255), "preto": (15, 15, 15), "cinza_esc": (30, 30, 40),
    "cinza_med": (60, 60, 75), "ceu": (56, 182, 255), "terra": (139, 90, 43),
}


def iniciar_pygame():
    """Inicializa o pygame uma única vez e devolve a superfície lógica do jogo."""
    if not pygame.get_init():
        pygame.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((LARGURA, ALTURA))
    return pygame.Surface((LARGURA, ALTURA))


def novo_estado(fase=1):
    """Estado global compartilhado entre as telas (igual ao do main.py)."""
    return {"usuario": None, "tela_atual": f"fase_{fase}",
            "fase_atual": fase, "avatar_escolhido": "masculino"}


def clique(pos):
    """Um clique completo do mouse (pressionar + soltar) na posição dada."""
    return [
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1),
        pygame.event.Event(pygame.MOUSEBUTTONUP, pos=pos, button=1),
    ]


def tecla(chave):
    return pygame.event.Event(pygame.KEYDOWN, key=chave)


def rodar_frames(tela, n):
    for _ in range(n):
        tela.update()


def esperar_popup(tela, limite=600):
    """Roda update() até o popup da tela sumir (ou estourar o limite)."""
    for _ in range(limite):
        if getattr(tela, "popup", None) is None:
            return
        tela.update()
    raise AssertionError("o popup não terminou dentro do limite de frames")


def clicar_resposta(tela, chave, correto, certo=True):
    """Clica no botão de resposta certo (ou num errado) das fases 4, 5, 6, 9 e 10.

    `chave` é a chave do dicionário do botão ("resposta", "letra", "valor"...)
    e `correto` é o valor que representa a resposta certa.
    """
    for botao in tela.botoes_resposta:
        if (botao[chave] == correto) == certo:
            tela.handle_events(clique(botao["rect"].center))
            return botao
    raise AssertionError("botão de resposta não encontrado")
