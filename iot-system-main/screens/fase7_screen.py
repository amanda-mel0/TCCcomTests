import pygame
import random
import math
from ui_components import LegoButton
from screens.audio_manager import play_error, play_success
from screens.fase_concluida import (
    PopupFaseConcluida,
    avancar_para_proxima_fase,
    get_phase_completion_text,
)

WIDTH, HEIGHT = 1100, 700

# --- Paleta ---
SKY_TOP        = ( 30, 144, 220)
SKY_BOT        = (100, 195, 255)
GRASS_DARK     = ( 55, 130,  50)
GRASS_MID      = ( 75, 160,  65)
GRASS_LIGHT    = ( 95, 185,  80)
PATH_COLOR     = (210, 185, 130)
PATH_EDGE      = (170, 145,  95)

LEGO_YELLOW    = (255, 205,   0)
LEGO_RED       = (196,  40,  27)
LEGO_BLUE      = ( 13,  94, 175)
LEGO_GREEN     = ( 75, 151,  74)
LEGO_WHITE     = (255, 255, 255)
LEGO_DARK      = ( 25,  25,  25)
LEGO_ORANGE    = (254, 138,  24)
LEGO_PURPLE    = (130,  60, 180)
LEGO_STUD_DK   = (180, 145,   0)

CORRECT_GREEN  = ( 34, 197,  94)
WRONG_RED      = (220,  38,  38)
PANEL_BG       = (255, 240, 180)

# --- Perguntas ---
QUESTIONS = [
    {"question": "Qual é o TRIÂNGULO?",  "answer": "triangulo",
     "shapes": [{"name":"triangulo","color":LEGO_RED},{"name":"quadrado","color":LEGO_BLUE},
                {"name":"retangulo","color":LEGO_GREEN},{"name":"circulo","color":LEGO_ORANGE}]},
    {"question": "Qual é o QUADRADO?",   "answer": "quadrado",
     "shapes": [{"name":"circulo","color":LEGO_ORANGE},{"name":"quadrado","color":LEGO_BLUE},
                {"name":"triangulo","color":LEGO_RED},{"name":"retangulo","color":LEGO_GREEN}]},
    {"question": "Qual é o RETÂNGULO?",  "answer": "retangulo",
     "shapes": [{"name":"quadrado","color":LEGO_BLUE},{"name":"triangulo","color":LEGO_RED},
                {"name":"retangulo","color":LEGO_PURPLE},{"name":"circulo","color":LEGO_ORANGE}]},
    {"question": "Qual é o CÍRCULO?",    "answer": "circulo",
     "shapes": [{"name":"retangulo","color":LEGO_GREEN},{"name":"circulo","color":LEGO_ORANGE},
                {"name":"quadrado","color":LEGO_BLUE},{"name":"triangulo","color":LEGO_RED}]},
]

# --- Estado ---
class GS:
    def __init__(self): self.reset()
    def reset(self):
        self.questions = random.sample(QUESTIONS, len(QUESTIONS))
        self.q_index   = 0
        self.score     = 0
        self.feedback  = None
        self.fb_timer  = 0
        self.selected  = -1
        self.phase     = "playing"
        self.anim      = 0
        self.shuffle()
    def shuffle(self):
        q = self.questions[self.q_index]
        self.current_shapes = random.sample(q["shapes"], len(q["shapes"]))
    def current_q(self): return self.questions[self.q_index]





class Fase7Screen:
    """Jogo de Reconhecimento de Formas LEGO"""

    def __init__(self, surf, largura, altura, cores, estado, *args, **kwargs):
        self.surf = surf
        self.W = largura
        self.H = altura
        self.cores = cores
        self.estado = estado
        self.tick = 0

        # Fontes
        self.font_title = pygame.font.Font(None, 68)
        self.font_btn = pygame.font.Font(None, 48)
        self.font_score = pygame.font.Font(None, 44)
        self.font_small = pygame.font.Font(None, 30)
        self.fase_concluida = None

        # Estado do jogo
        self.gs = GS()
        self.mx = 0
        self.my = 0

        # Tamanhos dos botões adaptados para 1100x700
        self.BTN_W = 350
        self.BTN_H = 180
        self.GAP = 30
        self.START_X = (self.W - (self.BTN_W * 2 + self.GAP)) // 2
        self.START_Y = 200

        # Pré-renderizar fundo
        self._create_bg()

        # Botão voltar
        self.btn_voltar = LegoButton(
            40, self.H - 70, 200, 46,
            "VOLTAR", self.cores["cinza_med"],
            pygame.font.SysFont("Impact", 16), studs=0
        )

    def _create_bg(self):
        """Pré-renderiza o fundo da tela"""
        self.bg_surf = pygame.Surface((self.W, self.H))
        self._draw_sky(self.bg_surf)
        self._draw_cloud(self.bg_surf, 200, 80, 1.2)
        self._draw_cloud(self.bg_surf, 500, 60, 0.9)
        self._draw_cloud(self.bg_surf, 850, 100, 1.1)
        self._draw_grass(self.bg_surf)
        self._draw_path(self.bg_surf)
        self._draw_decorative_bricks(self.bg_surf)

    def _draw_sky(self, surf):
        for y in range(self.H // 2):
            t = y / (self.H // 2)
            c = self._lerp_color(SKY_TOP, SKY_BOT, t)
            pygame.draw.line(surf, c, (0, y), (self.W, y))

    def _draw_cloud(self, surf, x, y, scale=1.0):
        s = scale
        for ox, oy, r in [(0, 0, 22), (28, -8, 18), (-22, -6, 16), (50, 0, 14), (-40, 4, 12)]:
            pygame.draw.circle(surf, (255, 255, 255), (int(x + ox * s), int(y + oy * s)), int(r * s))
        for ox, oy, r in [(0, 0, 20), (28, -8, 16), (-22, -6, 14), (50, 0, 12), (-40, 4, 10)]:
            pygame.draw.circle(surf, (240, 248, 255), (int(x + ox * s), int(y + oy * s)), int(r * s))

    def _draw_grass(self, surf):
        pts = [(0, self.H // 2 - 20), (self.W, self.H // 2 - 10), (self.W, self.H), (0, self.H)]
        pygame.draw.polygon(surf, GRASS_MID, pts)
        for bx in range(0, self.W, 60):
            pygame.draw.ellipse(surf, GRASS_LIGHT, (bx, self.H // 2 - 30, 70, 30))
        pygame.draw.rect(surf, GRASS_DARK, (0, self.H - 80, self.W, 80))
        for gx in range(20, self.W, 80):
            for gy in range(self.H // 2 + 10, self.H - 70, 50):
                self._draw_stud(surf, gx, gy, r=6, color=GRASS_LIGHT)

    def _draw_path(self, surf):
        pts = []
        for i in range(60):
            t = i / 59
            px = int(t * self.W)
            py = int(self.H // 2 + 30 + math.sin(t * math.pi * 1.5) * 40)
            pts.append((px, py))
        if len(pts) >= 2:
            for k in range(len(pts) - 1):
                pygame.draw.line(surf, PATH_EDGE, pts[k], pts[k + 1], 20)
            for k in range(len(pts) - 1):
                pygame.draw.line(surf, PATH_COLOR, pts[k], pts[k + 1], 14)

    def _draw_decorative_bricks(self, surf):
        bricks = [
            (10, self.H // 2 - 50, 40, 20, LEGO_RED),
            (60, self.H // 2 - 65, 30, 18, LEGO_YELLOW),
            (self.W - 100, self.H // 2 - 55, 45, 20, LEGO_BLUE),
            (self.W - 50, self.H // 2 - 72, 35, 18, LEGO_GREEN),
            (5, self.H - 90, 50, 22, LEGO_ORANGE),
            (self.W - 90, self.H - 85, 55, 22, LEGO_RED),
            (self.W - 40, self.H - 62, 40, 20, LEGO_YELLOW),
        ]
        for bx, by, bw, bh, bc in bricks:
            self._draw_lego_brick(surf, bx, by, bw, bh, bc)

    def _lerp_color(self, a, b, t):
        return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

    def _draw_stud(self, surf, cx, cy, r=8, color=LEGO_YELLOW):
        dk = tuple(max(0, c - 55) for c in color)
        pygame.draw.ellipse(surf, dk, (cx - r, cy - r // 2, r * 2, r))
        pygame.draw.ellipse(surf, color, (cx - r, cy - r, r * 2, r * 2))

    def _draw_lego_brick(self, surf, x, y, w, h, color):
        dk = tuple(max(0, c - 60) for c in color)
        shadow_r = pygame.Rect(x + 4, y + 4, w, h)
        pygame.draw.rect(surf, dk, shadow_r, border_radius=6)
        r = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surf, color, r, border_radius=6)
        pygame.draw.rect(surf, LEGO_DARK, r, 2, border_radius=6)
        stud_count = max(1, w // 20)
        spacing = w // stud_count
        for si in range(stud_count):
            sx = x + spacing // 2 + si * spacing
            self._draw_stud(surf, sx, y + 4, r=6, color=color)

    def _draw_header(self, surf, score, total):
        hbar = pygame.Rect(0, 0, self.W, 72)
        pygame.draw.rect(surf, LEGO_RED, hbar)
        pygame.draw.rect(surf, LEGO_DARK, hbar, 3)
        for i in range(20):
            self._draw_stud(surf, 20 + i * 55, 5, r=7, color=LEGO_RED)
        sc = self.font_score.render(f"{score}/{total}", True, LEGO_YELLOW)
        surf.blit(sc, (self.W - sc.get_width() - 20, 18))

    def _draw_feedback_banner(self, surf, feedback):
        if feedback == "correct":
            bg_color = CORRECT_GREEN
            text = "CORRETO!"
        else:
            bg_color = WRONG_RED
            text = "TENTE NOVAMENTE!"

        banner_w = 420
        banner_h = 60
        x = self.W // 2 - banner_w // 2
        y = 80

        pygame.draw.rect(surf, (60, 60, 60), (x + 4, y + 4, banner_w, banner_h), border_radius=12)
        pygame.draw.rect(surf, bg_color, (x, y, banner_w, banner_h), border_radius=12)
        pygame.draw.rect(surf, LEGO_DARK, (x, y, banner_w, banner_h), 3, border_radius=12)

        for i in range(8):
            self._draw_stud(surf, x + 35 + i * 50, y + 5, r=6, color=bg_color)

        txt = self.font_btn.render(text, True, LEGO_WHITE)
        surf.blit(txt, (x + banner_w // 2 - txt.get_width() // 2, y + banner_h // 2 - txt.get_height() // 2 + 5))

    def _draw_question_panel(self, surf, text):
        px, py, pw, ph = 60, 120, self.W - 120, 70
        pygame.draw.rect(surf, (0, 0, 0, 80), (px + 5, py + 5, pw, ph), border_radius=12)
        pygame.draw.rect(surf, LEGO_BLUE, (px, py, pw, ph), border_radius=12)
        pygame.draw.rect(surf, LEGO_DARK, (px, py, pw, ph), 3, border_radius=12)
        for i in range(pw // 40):
            self._draw_stud(surf, px + 20 + i * 40, py + 5, r=6, color=LEGO_BLUE)
        q_surf = self.font_btn.render(text, True, LEGO_WHITE)
        surf.blit(q_surf, (px + pw // 2 - q_surf.get_width() // 2, py + ph // 2 - q_surf.get_height() // 2 + 6))

    def _draw_shape(self, surf, name, color, cx, cy, size=52):
        shadow = tuple(max(0, c - 80) for c in color)

        if name == "triangulo":
            pts = [(cx, cy - size), (cx - size, cy + int(size * .75)), (cx + size, cy + int(size * .75))]
            spts = [(x + 5, y + 5) for x, y in pts]
            pygame.draw.polygon(surf, shadow, spts)
            pygame.draw.polygon(surf, color, pts)
            pygame.draw.polygon(surf, LEGO_DARK, pts, 3)
            self._draw_stud(surf, cx, cy + int(size * .1), r=10, color=color)

        elif name == "quadrado":
            s = size
            pygame.draw.rect(surf, shadow, (cx - s + 5, cy - s + 5, s * 2, s * 2), border_radius=8)
            pygame.draw.rect(surf, color, (cx - s, cy - s, s * 2, s * 2), border_radius=8)
            pygame.draw.rect(surf, LEGO_DARK, (cx - s, cy - s, s * 2, s * 2), 3, border_radius=8)
            for dx in [-s // 2, s // 2]:
                for dy in [-s // 2, s // 2]:
                    self._draw_stud(surf, cx + dx, cy + dy, r=9, color=color)

        elif name == "retangulo":
            w, h = int(size * 1.65), int(size * .85)
            pygame.draw.rect(surf, shadow, (cx - w + 5, cy - h + 5, w * 2, h * 2), border_radius=8)
            pygame.draw.rect(surf, color, (cx - w, cy - h, w * 2, h * 2), border_radius=8)
            pygame.draw.rect(surf, LEGO_DARK, (cx - w, cy - h, w * 2, h * 2), 3, border_radius=8)
            for dx in [-w // 2, 0, w // 2]:
                self._draw_stud(surf, cx + dx, cy, r=9, color=color)

        elif name == "circulo":
            pygame.draw.circle(surf, shadow, (cx + 5, cy + 5), size)
            pygame.draw.circle(surf, color, (cx, cy), size)
            pygame.draw.circle(surf, LEGO_DARK, (cx, cy), size, 3)
            self._draw_stud(surf, cx, cy, r=11, color=color)

    def _draw_shape_button(self, surf, name, color, rect, hover=False, feedback=None):
        bg = (245, 245, 240)
        bord = LEGO_DARK

        if feedback == "correct":
            bg = CORRECT_GREEN
            bord = (15, 120, 50)
        elif feedback == "wrong":
            bg = WRONG_RED
            bord = (140, 10, 10)
        elif hover:
            bg = (225, 235, 255)

        pygame.draw.rect(surf, (100, 100, 100), rect.move(6, 6), border_radius=18)
        pygame.draw.rect(surf, bg, rect, border_radius=18)
        pygame.draw.rect(surf, bord, rect, 4, border_radius=18)

        for i in range(2):
            sx = rect.x + rect.width // 4 + i * (rect.width // 2)
            self._draw_stud(surf, sx, rect.y + 8, r=7, color=bg if bg != (245, 245, 240) else LEGO_YELLOW)

        cx = rect.centerx
        cy = rect.centery
        self._draw_shape(surf, name, color, cx, cy, size=50)

    def _draw_end_screen(self, surf, score, total):
        ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 140))
        surf.blit(ov, (0, 0))

        panel = pygame.Rect(100, 100, self.W - 200, 400)
        pygame.draw.rect(surf, LEGO_YELLOW, panel, border_radius=20)
        pygame.draw.rect(surf, LEGO_DARK, panel, 4, border_radius=20)
        for i in range(12):
            self._draw_stud(surf, panel.x + 30 + i * 60, panel.y + 6, r=8, color=LEGO_YELLOW)

        emoji = "" if score == total else ""
        t1 = self.font_title.render(f"{emoji}  Fim de Fase!", True, LEGO_RED)
        t2 = self.font_btn.render(f"Você acertou {score} de {total}!", True, LEGO_DARK)

        msg, mc = (("Parabéns! Incrível!", LEGO_GREEN) if score == total else
                   ("Muito bem! Continue!", LEGO_BLUE) if score >= total // 2 else
                   ("Tente de novo!", LEGO_RED))
        t3 = self.font_score.render(msg, True, mc)
        _, subtitle, button_text = get_phase_completion_text(self.estado)
        t4 = self.font_small.render(subtitle, True, LEGO_DARK)
        t5 = self.font_small.render(button_text, True, LEGO_DARK)

        surf.blit(t1, (panel.centerx - t1.get_width() // 2, panel.y + 30))
        surf.blit(t2, (panel.centerx - t2.get_width() // 2, panel.y + 110))
        surf.blit(t3, (panel.centerx - t3.get_width() // 2, panel.y + 170))
        surf.blit(t4, (panel.centerx - t4.get_width() // 2, panel.y + 250))
        surf.blit(t5, (panel.centerx - t5.get_width() // 2, panel.y + 300))

    def _get_rects(self):
        rects = []
        for row in range(2):
            for col in range(2):
                x = self.START_X + col * (self.BTN_W + self.GAP)
                y = self.START_Y + row * (self.BTN_H + self.GAP)
                rects.append(pygame.Rect(x, y, self.BTN_W, self.BTN_H))
        return rects

    def handle_events(self, eventos):
        for ev in eventos:
            if ev.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                self.mx, self.my = ev.pos

            if self.fase_concluida:
                if self.fase_concluida.handle_event(ev):
                    avancar_para_proxima_fase(self.estado)
                continue

            if self.btn_voltar.handle_event(ev):
                self.estado["tela_atual"] = "mapa"
                return

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.estado["tela_atual"] = "mapa"
                    return
                if ev.key == pygame.K_SPACE and self.gs.phase == "end":
                    self.gs.reset()

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if self.gs.phase == "playing" and self.gs.feedback is None:
                    for i, rect in enumerate(self._get_rects()):
                        if rect.collidepoint(self.mx, self.my):
                            self.gs.selected = i
                            shape = self.gs.current_shapes[i]
                            self.gs.feedback = "correct" if shape["name"] == self.gs.current_q()["answer"] else "wrong"
                            if self.gs.feedback == "correct":
                                self.gs.score += 1
                                play_success()
                            else:
                                play_error()
                            self.gs.fb_timer = 90

    def update(self):
        self.tick += 1
        self.gs.anim += 1

        if self.gs.feedback is not None:
            self.gs.fb_timer -= 1
            if self.gs.fb_timer <= 0:
                self.gs.feedback = None
                self.gs.selected = -1
                self.gs.q_index += 1
                if self.gs.q_index >= len(self.gs.questions):
                    self.gs.phase = "end"
                    self.fase_concluida = PopupFaseConcluida(self.W, self.H, self.estado)
                else:
                    self.gs.shuffle()

    def draw(self):
        if self.gs.phase == "playing":
            self.surf.blit(self.bg_surf, (0, 0))
            self._draw_header(self.surf, self.gs.score, len(self.gs.questions))

            if self.gs.feedback is not None:
                self._draw_feedback_banner(self.surf, self.gs.feedback)

            self._draw_question_panel(self.surf, self.gs.current_q()["question"])

            rects = self._get_rects()
            for i, (rect, shape) in enumerate(zip(rects, self.gs.current_shapes)):
                hov = rect.collidepoint(self.mx, self.my) and self.gs.feedback is None
                fb = self.gs.feedback if self.gs.selected == i else None
                self._draw_shape_button(self.surf, shape["name"], shape["color"], rect, hover=hov, feedback=fb)

            # Barra de progresso
            prog = self.gs.q_index / len(self.gs.questions)
            bar_rect = pygame.Rect(60, self.H - 50, self.W - 120, 12)
            pygame.draw.rect(self.surf, (200, 200, 200), bar_rect, border_radius=6)
            pygame.draw.rect(self.surf, LEGO_GREEN, pygame.Rect(60, self.H - 50, int((self.W - 120) * prog), 12), border_radius=6)
            pt = self.font_small.render(f"Pergunta {self.gs.q_index + 1} de {len(self.gs.questions)}", True, LEGO_WHITE)
            self.surf.blit(pt, (self.W // 2 - pt.get_width() // 2, self.H - 25))

            self.btn_voltar.draw(self.surf)

        elif self.gs.phase == "end":
            self.surf.blit(self.bg_surf, (0, 0))
            if self.fase_concluida:
                self.fase_concluida.draw(self.surf)
            else:
                self._draw_end_screen(self.surf, self.gs.score, len(self.gs.questions))
