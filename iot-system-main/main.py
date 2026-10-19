import pygame
import random
import sys
import os
from pathlib import Path
from screens.login_screen import LoginScreen
from screens.cadastro_screen import CadastroScreen
from screens.mapa_screen import MapaScreen
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
from screens.fase_concluida import TOTAL_FASES
from screens.perfil_screen import PerfilScreen
from screens.jogo_concluido import JogoConcluidoScreen


# ── Configurações gerais ──────────────────────────────────────────────────────
FPS = 30
TITULO = "Ler Brincando"
BASE_DIR = Path(__file__).resolve().parent
LOGICAL_WIDTH = 1100
LOGICAL_HEIGHT = 700

# ── Paleta LEGO ───────────────────────────────────────────────────────────────
CORES = {
    "vermelho":   (220, 38,  38),
    "azul":       (37,  99, 235),
    "verde":      (34, 197,  94),
    "amarelo":    (234,179,   8),
    "laranja":    (249,115,  22),
    "roxo":       (147, 51, 234),
    "branco":     (255,255, 255),
    "preto":      (15,  15,  15),
    "cinza_esc":  (30,  30,  40),
    "cinza_med":  (60,  60,  75),
    "ceu":        (56, 182, 255),
    "terra":      (139, 90,  43),
}



def _scale_mouse_pos(pos, display_size):
    _, _, scaled_w, scaled_h, offset_x, offset_y = _get_render_area(display_size)
    x = min(max(pos[0] - offset_x, 0), scaled_w)
    y = min(max(pos[1] - offset_y, 0), scaled_h)
    scale_x = LOGICAL_WIDTH / max(1, scaled_w)
    scale_y = LOGICAL_HEIGHT / max(1, scaled_h)
    return (int(x * scale_x), int(y * scale_y))


def _get_render_area(display_size):
    display_w, display_h = display_size
    scale = min(display_w / LOGICAL_WIDTH, display_h / LOGICAL_HEIGHT)
    scaled_w = max(1, int(LOGICAL_WIDTH * scale))
    scaled_h = max(1, int(LOGICAL_HEIGHT * scale))
    offset_x = (display_w - scaled_w) // 2
    offset_y = (display_h - scaled_h) // 2
    return scale, scale, scaled_w, scaled_h, offset_x, offset_y


def _scale_events(eventos, display_size):
    eventos_convertidos = []

    for ev in eventos:
        if ev.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            attrs = ev.dict.copy()
            if "pos" in attrs:
                attrs["pos"] = _scale_mouse_pos(attrs["pos"], display_size)
            if "rel" in attrs:
                scale_x, scale_y, _, _, _, _ = _get_render_area(display_size)
                attrs["rel"] = (
                    int(attrs["rel"][0] / max(0.001, scale_x)),
                    int(attrs["rel"][1] / max(0.001, scale_y)),
                )
            eventos_convertidos.append(pygame.event.Event(ev.type, attrs))
        elif ev.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
            touch_pos = (int(ev.x * LOGICAL_WIDTH), int(ev.y * LOGICAL_HEIGHT))
            if ev.type == pygame.FINGERMOTION:
                eventos_convertidos.append(
                    pygame.event.Event(pygame.MOUSEMOTION, {"pos": touch_pos, "rel": (0, 0), "buttons": (1, 0, 0)})
                )
            else:
                mouse_type = pygame.MOUSEBUTTONDOWN if ev.type == pygame.FINGERDOWN else pygame.MOUSEBUTTONUP
                eventos_convertidos.append(
                    pygame.event.Event(mouse_type, {"pos": touch_pos, "button": 1})
                )
        else:
            eventos_convertidos.append(ev)

    return eventos_convertidos


def _iniciar_musica():
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        musica_path = BASE_DIR / "assets" / "sons" / "musica_fundo.wav"
        if not musica_path.exists():
            return

        musica = pygame.mixer.Sound(str(musica_path))
        musica.play(-1)
    except pygame.error as exc:
        print(f"Audio desativado: {exc}")


def main():
    os.environ.setdefault("SDL_TOUCH_MOUSE_EVENTS", "0")
    pygame.init()

    info = pygame.display.Info()

    LARGURA = info.current_w
    ALTURA = info.current_h
    if LARGURA <= 0 or ALTURA <= 0:
        LARGURA, ALTURA = 800, 480
    
    pygame.display.set_caption(TITULO)
    tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
    canvas = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT)).convert()
    relogio = pygame.time.Clock()

    # Estado global compartilhado entre telas
    estado = {
        "usuario": None,   # dados do usuário logado
        "tela_atual": "login",
        "fase_atual": 1,
        "avatar_escolhido": "masculino",   # avatar padrão
    }

    telas = {
        "login":    LoginScreen(canvas, LOGICAL_WIDTH, LOGICAL_HEIGHT, CORES, estado),
        "cadastro": CadastroScreen(canvas, LOGICAL_WIDTH, LOGICAL_HEIGHT, CORES, estado),
        "perfil":   PerfilScreen(canvas, LOGICAL_WIDTH, LOGICAL_HEIGHT, CORES, estado),
        "mapa":     MapaScreen(canvas, LOGICAL_WIDTH, LOGICAL_HEIGHT, CORES, estado),
        "fase_1":   Fase1Screen(canvas, LOGICAL_WIDTH, LOGICAL_HEIGHT, CORES, estado),
        "fase_2":   Fase2Screen(canvas, LOGICAL_WIDTH, LOGICAL_HEIGHT, CORES, estado),
        "fase_3":   LogicaScreen(canvas, LOGICAL_WIDTH, LOGICAL_HEIGHT, CORES, estado),
        "fase_4":   Fase4Screen(canvas, LOGICAL_WIDTH, LOGICAL_HEIGHT, CORES, estado),
        "fase_5":   Fase5Screen(canvas, LOGICAL_WIDTH, LOGICAL_HEIGHT, CORES, estado),
        "fase_6":   Fase6Screen(canvas, LOGICAL_WIDTH, LOGICAL_HEIGHT, CORES, estado),
        "fase_7":   Fase7Screen(canvas, LOGICAL_WIDTH, LOGICAL_HEIGHT, CORES, estado),
        "fase_8":   Fase8Screen(canvas, LOGICAL_WIDTH, LOGICAL_HEIGHT, CORES, estado),
        "fase_9":   Fase9Screen(canvas, LOGICAL_WIDTH, LOGICAL_HEIGHT, CORES, estado),
        "fase_10":   Fase10Screen(canvas, LOGICAL_WIDTH, LOGICAL_HEIGHT, CORES, estado),
        "jogo_concluido": JogoConcluidoScreen(canvas, LOGICAL_WIDTH, LOGICAL_HEIGHT, CORES, estado),
    }
    _iniciar_musica()

    fases_cadastradas = [f"fase_{i}" for i in range(1, TOTAL_FASES + 1)]
    fases_faltando = [fase for fase in fases_cadastradas if fase not in telas]
    if fases_faltando:
        raise RuntimeError(f"Fases sem tela cadastrada: {', '.join(fases_faltando)}")

    rodando = True
    while rodando:
        eventos = pygame.event.get()
        for ev in eventos:
            if ev.type == pygame.QUIT:
                rodando = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()

        eventos_logicos = _scale_events(eventos, (LARGURA, ALTURA))

        tela_key = estado["tela_atual"]
        tela_obj = telas.get(tela_key)

        if tela_obj:
            tela_obj.handle_events(eventos_logicos)
            tela_obj.update()
            tela_obj.draw()

        _, _, scaled_w, scaled_h, offset_x, offset_y = _get_render_area((LARGURA, ALTURA))
        tela.fill((0, 0, 0))
        frame = pygame.transform.scale(canvas, (scaled_w, scaled_h))
        tela.blit(frame, (offset_x, offset_y))
        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
