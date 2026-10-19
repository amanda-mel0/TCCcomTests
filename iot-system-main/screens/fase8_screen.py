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
FPS = 60

# ---------- Paleta ----------
SKY_TOP       = ( 30, 144, 220)
SKY_BOT       = (100, 195, 255)
GRASS_DARK    = ( 55, 130,  50)
GRASS_MID     = ( 75, 160,  65)
GRASS_LIGHT   = ( 95, 185,  80)
PATH_COLOR    = (210, 185, 130)
PATH_EDGE     = (170, 145,  95)
LEGO_YELLOW   = (255, 205,   0)
LEGO_RED      = (196,  40,  27)
LEGO_BLUE     = ( 13,  94, 175)
LEGO_GREEN    = ( 75, 151,  74)
LEGO_ORANGE   = (254, 138,  24)
LEGO_PURPLE   = (130,  60, 180)
LEGO_WHITE    = (255, 255, 255)
LEGO_DARK     = ( 25,  25,  25)
CORRECT_GREEN = ( 34, 197,  94)
WRONG_RED     = (220,  38,  38)

# ---------- Fontes ----------
# (Serão instanciadas na classe Fase8Screen)

# ---------- Dados de cores ----------
# Cada cor: (nome, rgb, emoji-representação via círculo colorido)
COLORS = [
    {"name": "Vermelho", "rgb": LEGO_RED,    "hex": "#C4281B"},
    {"name": "Azul",     "rgb": LEGO_BLUE,   "hex": "#0D5EAF"},
    {"name": "Verde",    "rgb": LEGO_GREEN,  "hex": "#4B9750"},
    {"name": "Amarelo",  "rgb": LEGO_YELLOW, "hex": "#FFCD00"},
    {"name": "Laranja",  "rgb": LEGO_ORANGE, "hex": "#FE8A18"},
    {"name": "Roxo",     "rgb": LEGO_PURPLE, "hex": "#823CB4"},
]

# Perguntas possíveis por posição
POSITION_LABELS = ["esquerda", "meio", "direita"]
POSITION_QUESTIONS = [
    "Qual cor estava na ESQUERDA?",
    "Qual cor estava no MEIO?",
    "Qual cor estava na DIREITA?",
]

SHOW_SECONDS  = 3          # tempo mostrando as cores
SHOW_FRAMES   = FPS * SHOW_SECONDS
FB_FRAMES     = FPS * 2    # tempo do feedback
TOTAL_ROUNDS  = 5

# ============================================================
#  FUNDO PRÉ-RENDERIZADO
# ============================================================
def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

def draw_stud(surf, cx, cy, r=8, color=LEGO_YELLOW):
    dk = tuple(max(0, c-55) for c in color)
    pygame.draw.ellipse(surf, dk,    (cx-r, cy-r//2, r*2, r))
    pygame.draw.ellipse(surf, color, (cx-r, cy-r,    r*2, r*2))

def draw_sky(surf):
    for y in range(HEIGHT//2):
        t = y/(HEIGHT//2)
        c = lerp_color(SKY_TOP, SKY_BOT, t)
        pygame.draw.line(surf, c, (0,y), (WIDTH,y))

def draw_cloud(surf, x, y, scale=1.0):
    s = scale
    for ox,oy,r in [(0,0,22),(28,-8,18),(-22,-6,16),(50,0,14),(-40,4,12)]:
        pygame.draw.circle(surf,(255,255,255),(int(x+ox*s),int(y+oy*s)),int(r*s))
    for ox,oy,r in [(0,0,20),(28,-8,16),(-22,-6,14),(50,0,12),(-40,4,10)]:
        pygame.draw.circle(surf,(240,248,255),(int(x+ox*s),int(y+oy*s)),int(r*s))

def draw_grass(surf):
    pts = [(0,HEIGHT//2-20),(WIDTH,HEIGHT//2-10),(WIDTH,HEIGHT),(0,HEIGHT)]
    pygame.draw.polygon(surf, GRASS_MID, pts)
    for bx in range(0, WIDTH, 60):
        pygame.draw.ellipse(surf, GRASS_LIGHT, (bx, HEIGHT//2-30, 70, 30))
    pygame.draw.rect(surf, GRASS_DARK, (0, HEIGHT-80, WIDTH, 80))
    for gx in range(20, WIDTH, 80):
        for gy in range(HEIGHT//2+10, HEIGHT-70, 50):
            draw_stud(surf, gx, gy, r=6, color=GRASS_LIGHT)

def draw_path(surf):
    pts = []
    for i in range(60):
        t  = i/59
        px = int(t*WIDTH)
        py = int(HEIGHT//2+30+math.sin(t*math.pi*1.5)*40)
        pts.append((px,py))
    if len(pts)>=2:
        for k in range(len(pts)-1):
            pygame.draw.line(surf, PATH_EDGE, pts[k], pts[k+1], 20)
        for k in range(len(pts)-1):
            pygame.draw.line(surf, PATH_COLOR, pts[k], pts[k+1], 14)

def draw_deco_bricks(surf, W, H):
    bricks = [
        (10, H//2-50, 40, 20, LEGO_RED),
        (60, H//2-65, 30, 18, LEGO_YELLOW),
        (W-100, H//2-55, 45, 20, LEGO_BLUE),
        (W-50, H//2-72, 35, 18, LEGO_GREEN),
        (5, H-90, 50, 22, LEGO_ORANGE),
        (W-90, H-85, 55, 22, LEGO_RED),
        (W-40, H-62, 40, 20, LEGO_YELLOW),
    ]
    for bx,by,bw,bh,bc in bricks:
        dk = tuple(max(0,c-60) for c in bc)
        pygame.draw.rect(surf, dk, (bx+4,by+4,bw,bh), border_radius=6)
        pygame.draw.rect(surf, bc, (bx,by,bw,bh),     border_radius=6)
        pygame.draw.rect(surf, LEGO_DARK, (bx,by,bw,bh), 2, border_radius=6)
        for si in range(max(1,bw//20)):
            sx = bx + bw//(max(1,bw//20)*2) + si*(bw//max(1,bw//20))
            draw_stud(surf, sx, by+4, r=5, color=bc)

# ============================================================
#  HELPERS DE DESENHO (FUNÇÕES GLOBAIS)
# ============================================================

# ============================================================
#  GERAÇÃO DE ROUNDS
# ============================================================
def generate_round():
    """Escolhe 3 cores aleatórias distintas e uma posição para perguntar."""
    chosen = random.sample(COLORS, 3)
    pos    = random.randint(0, 2)   # 0=esq 1=meio 2=dir
    answer = chosen[pos]
    # opções: a cor certa + 2 distrações
    distractors = random.sample([c for c in COLORS if c != answer], 2)
    options = random.sample([answer] + distractors, 3)
    return {
        "colors":   chosen,       # lista de 3 cor-dicts (esq, meio, dir)
        "pos":      pos,
        "question": POSITION_QUESTIONS[pos],
        "answer":   answer,
        "options":  options,
    }

# ============================================================
#  ESTADO DO JOGO
# ============================================================
class GS:
    def __init__(self): self.reset()

    def reset(self):
        self.rounds    = [generate_round() for _ in range(TOTAL_ROUNDS)]
        self.r_index   = 0
        self.score     = 0
        self.phase     = "show"      # show | hidden | question | feedback | end
        self.timer     = int(60 * 3) # SHOW_FRAMES = FPS * 3
        self.selected  = -1
        self.feedback  = None
        self.fb_timer  = 0
        self.anim      = 0

    def round(self): return self.rounds[self.r_index]


class Fase8Screen:
    """Jogo de Memória de Cores LEGO"""

    def __init__(self, surf, largura, altura, cores, estado, *args, **kwargs):
        self.surf = surf
        self.W = largura
        self.H = altura
        self.cores = cores
        self.estado = estado
        self.tick = 0

        # Fontes
        self.font_big = pygame.font.Font(None, 72)
        self.font_med = pygame.font.Font(None, 50)
        self.font_small = pygame.font.Font(None, 32)
        self.font_score = pygame.font.Font(None, 44)
        self.font_fb = pygame.font.Font(None, 86)

        # Estado do jogo
        self.gs = GS()
        self.mx = 0
        self.my = 0
        self.fase_concluida = None

        # Constantes adaptadas para resolução 1100x700
        self.SHOW_FRAMES = 60 * 3  # 3 segundos
        self.FB_FRAMES = 60 * 2    # 2 segundos
        self.BALL_Y = 300
        self.BALL_R = 65
        self.BALL_XS = [250, 550, 850]
        self.OPT_W, self.OPT_H = 450, 78
        self.OPT_X = (self.W - self.OPT_W) // 2
        self.OPT_YS = [400, 490, 580]

        # Pré-renderizar fundo
        self._create_bg()

        # Botão voltar
        self.btn_voltar = LegoButton(
            40, self.H - 70, 200, 46,
            "VOLTAR", self.cores["cinza_med"],
            pygame.font.SysFont("Impact", 16), studs=0
        )

    def _create_bg(self):
        """Pré-renderiza o fundo"""
        self.bg_surf = pygame.Surface((self.W, self.H))
        self._draw_sky(self.bg_surf)
        self._draw_cloud(self.bg_surf, 200, 80, 1.2)
        self._draw_cloud(self.bg_surf, 550, 60, 0.9)
        self._draw_cloud(self.bg_surf, 900, 100, 1.1)
        self._draw_grass(self.bg_surf)
        self._draw_path(self.bg_surf)
        draw_deco_bricks(self.bg_surf, self.W, self.H)

    def _lerp_color(self, a, b, t):
        return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

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
                draw_stud(surf, gx, gy, r=6, color=GRASS_LIGHT)

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

    def _draw_lego_circle(self, surf, cx, cy, r, color):
        """Círculo LEGO com relevo e pino"""
        dk = tuple(max(0, c - 80) for c in color)
        pygame.draw.circle(surf, dk, (cx + 5, cy + 5), r)
        pygame.draw.circle(surf, color, (cx, cy), r)
        pygame.draw.circle(surf, LEGO_DARK, (cx, cy), r, 4)
        hl = tuple(min(255, c + 70) for c in color)
        pygame.draw.circle(surf, hl, (cx - r // 3, cy - r // 3), r // 4)
        draw_stud(surf, cx, cy, r=r // 5, color=color)

    def _draw_question_mark_circle(self, surf, cx, cy, r):
        """Círculo misterioso com '?'"""
        pygame.draw.circle(surf, (80, 80, 80), (cx + 5, cy + 5), r)
        pygame.draw.circle(surf, (160, 160, 160), (cx, cy), r)
        pygame.draw.circle(surf, LEGO_DARK, (cx, cy), r, 4)
        q = self.font_big.render("?", True, LEGO_DARK)
        surf.blit(q, (cx - q.get_width() // 2, cy - q.get_height() // 2))

    def _draw_header(self, surf, score, total):
        hbar = pygame.Rect(0, 0, self.W, 72)
        pygame.draw.rect(surf, LEGO_RED, hbar)
        pygame.draw.rect(surf, LEGO_DARK, hbar, 3)
        for i in range(20):
            draw_stud(surf, 20 + i * 55, 5, r=7, color=LEGO_RED)
        sc = self.font_score.render(f"{score}/{total}", True, LEGO_YELLOW)
        surf.blit(sc, (self.W - sc.get_width() - 20, 18))

    def _draw_panel(self, surf, rect, color=LEGO_WHITE, border=LEGO_DARK, studs=True):
        pygame.draw.rect(surf, tuple(max(0, c - 60) for c in color), rect.move(5, 5), border_radius=14)
        pygame.draw.rect(surf, color, rect, border_radius=14)
        pygame.draw.rect(surf, border, rect, 3, border_radius=14)
        if studs:
            n = rect.width // 40
            for i in range(n):
                draw_stud(surf, rect.x + 20 + i * 40, rect.y + 6, r=6, color=color)

    def _draw_text_centered(self, surf, text, font, color, cx, cy):
        s = font.render(text, True, color)
        surf.blit(s, (cx - s.get_width() // 2, cy - s.get_height() // 2))

    def _draw_countdown_bar(self, surf, frames_left, total_frames):
        bw = self.W - 120
        bx, by = 60, self.H - 50
        pygame.draw.rect(surf, (180, 180, 180), (bx, by, bw, 14), border_radius=7)
        t = max(0, frames_left / total_frames)
        fill_color = self._lerp_color(WRONG_RED, CORRECT_GREEN, t)
        pygame.draw.rect(surf, fill_color, (bx, by, int(bw * t), 14), border_radius=7)

    def _draw_option_button(self, surf, color_data, rect, hover=False, feedback=None):
        bg = LEGO_WHITE
        bord = LEGO_DARK
        if feedback == "correct":
            bg, bord = CORRECT_GREEN, (15, 120, 50)
        elif feedback == "wrong":
            bg, bord = WRONG_RED, (140, 10, 10)
        elif hover:
            bg = (225, 235, 255)

        pygame.draw.rect(surf, (100, 100, 100), rect.move(6, 6), border_radius=18)
        pygame.draw.rect(surf, bg, rect, border_radius=18)
        pygame.draw.rect(surf, bord, rect, 4, border_radius=18)
        for i in range(3):
            sx = rect.x + rect.width // 4 + i * (rect.width // 4)
            draw_stud(surf, sx, rect.y + 8, r=6, color=bg if bg != LEGO_WHITE else LEGO_YELLOW)

        r = rect.height // 2 - 20
        self._draw_lego_circle(surf, rect.x + rect.height // 2, rect.centery, r, color_data["rgb"])
        name = self.font_med.render(color_data["name"], True, LEGO_DARK)
        surf.blit(name, (rect.x + rect.height + 10, rect.centery - name.get_height() // 2))

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
                if self.gs.phase == "question":
                    for i, oy in enumerate(self.OPT_YS):
                        rect = pygame.Rect(self.OPT_X, oy, self.OPT_W, self.OPT_H)
                        if rect.collidepoint(self.mx, self.my):
                            self.gs.selected = i
                            opt = self.gs.round()["options"][i]
                            self.gs.feedback = "correct" if opt == self.gs.round()["answer"] else "wrong"
                            if self.gs.feedback == "correct":
                                self.gs.score += 1
                                play_success()
                            else:
                                play_error()
                            self.gs.phase = "feedback"
                            self.gs.fb_timer = self.FB_FRAMES
    def update(self):
        self.tick += 1
        self.gs.anim += 1

        # Transições de fase
        if self.gs.phase == "show":
            self.gs.timer -= 1
            if self.gs.timer <= 0:
                self.gs.phase = "hidden"
                self.gs.timer = 60  # 1s de "?"

        elif self.gs.phase == "hidden":
            self.gs.timer -= 1
            if self.gs.timer <= 0:
                self.gs.phase = "question"

        elif self.gs.phase == "feedback":
            self.gs.fb_timer -= 1
            if self.gs.fb_timer <= 0:
                self.gs.feedback = None
                self.gs.selected = -1
                self.gs.r_index += 1
                if self.gs.r_index >= TOTAL_ROUNDS:
                    self.gs.phase = "end"
                    self.fase_concluida = PopupFaseConcluida(self.W, self.H, self.estado)
                else:
                    self.gs.phase = "show"
                    self.gs.timer = self.SHOW_FRAMES

    def draw(self):
        self.surf.blit(self.bg_surf, (0, 0))
        self._draw_header(self.surf, self.gs.score, TOTAL_ROUNDS)

        if self.gs.phase in ("show", "hidden", "question", "feedback"):
            rnd = self.gs.round()

            # Painel de progresso
            prog_panel = pygame.Rect(250, 90, 600, 50)
            self._draw_panel(self.surf, prog_panel, color=LEGO_YELLOW, border=LEGO_DARK, studs=False)
            prog_txt = f"Rodada  {self.gs.r_index + 1}  de  {TOTAL_ROUNDS}"
            self._draw_text_centered(self.surf, prog_txt, self.font_small, LEGO_DARK,
                                      prog_panel.centerx, prog_panel.centery)

            # As 3 bolas
            if self.gs.phase == "show":
                self._draw_countdown_bar(self.surf, self.gs.timer, self.SHOW_FRAMES)
                inst_panel = pygame.Rect(150, 145, self.W - 300, 55)
                self._draw_panel(self.surf, inst_panel, color=LEGO_BLUE, border=LEGO_DARK, studs=False)
                self._draw_text_centered(self.surf, "Memorize as cores!", self.font_small,
                                         LEGO_WHITE, inst_panel.centerx, inst_panel.centery)
                for i, cx in enumerate(self.BALL_XS):
                    self._draw_lego_circle(self.surf, cx, self.BALL_Y, self.BALL_R, rnd["colors"][i]["rgb"])

            elif self.gs.phase == "hidden":
                inst_panel = pygame.Rect(200, 145, self.W - 400, 55)
                self._draw_panel(self.surf, inst_panel, color=(80, 80, 80), border=LEGO_DARK, studs=False)
                self._draw_text_centered(self.surf, "Agora lembre!", self.font_small,
                                         LEGO_WHITE, inst_panel.centerx, inst_panel.centery)
                for cx in self.BALL_XS:
                    self._draw_question_mark_circle(self.surf, cx, self.BALL_Y, self.BALL_R)

            elif self.gs.phase in ("question", "feedback"):
                for cx in self.BALL_XS:
                    self._draw_question_mark_circle(self.surf, cx, self.BALL_Y, self.BALL_R)

                q_panel = pygame.Rect(60, 145, self.W - 120, 60)
                self._draw_panel(self.surf, q_panel, color=LEGO_BLUE, border=LEGO_DARK, studs=False)
                self._draw_text_centered(self.surf, rnd["question"], self.font_small,
                                         LEGO_WHITE, q_panel.centerx, q_panel.centery)

                # Opções
                for i, oy in enumerate(self.OPT_YS):
                    rect = pygame.Rect(self.OPT_X, oy, self.OPT_W, self.OPT_H)
                    hover = rect.collidepoint(self.mx, self.my) and self.gs.phase == "question"
                    fb = None
                    if self.gs.phase == "feedback" and self.gs.selected == i:
                        fb = self.gs.feedback
                    self._draw_option_button(self.surf, rnd["options"][i], rect, hover=hover, feedback=fb)

                # Feedback central
                if self.gs.phase == "feedback":
                    if self.gs.feedback == "correct":
                        txt = self.font_fb.render("Correto!", True, CORRECT_GREEN)
                    else:
                        txt = self.font_fb.render("Errou!", True, WRONG_RED)
                    sh = self.font_fb.render("Correto!" if self.gs.feedback == "correct" else "Errou!",
                                            True, LEGO_DARK)
                    self.surf.blit(sh, (self.W // 2 - sh.get_width() // 2 + 3, 230))
                    self.surf.blit(txt, (self.W // 2 - txt.get_width() // 2, 227))

        elif self.gs.phase == "end" and not self.fase_concluida:
            ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            self.surf.blit(ov, (0, 0))

            panel = pygame.Rect(100, 120, self.W - 200, 420)
            self._draw_panel(self.surf, panel, color=LEGO_YELLOW, border=LEGO_DARK, studs=True)

            emoji = "" if self.gs.score == TOTAL_ROUNDS else ""
            msg, mc = (("Parabéns! Memória incrível! ", CORRECT_GREEN) if self.gs.score == TOTAL_ROUNDS else
                       ("Muito bem! Continue assim! ", LEGO_BLUE) if self.gs.score >= TOTAL_ROUNDS // 2 else
                       ("Tente de novo, vai conseguir! ", WRONG_RED))

            t1 = self.font_big.render(f"{emoji}  Fim de Fase!", True, LEGO_RED)
            t2 = self.font_med.render(f"Você acertou {self.gs.score} de {TOTAL_ROUNDS}!", True, LEGO_DARK)
            t3 = self.font_small.render(msg, True, mc)
            _, subtitle, button_text = get_phase_completion_text(self.estado)
            t4 = self.font_small.render(subtitle, True, LEGO_DARK)
            t5 = self.font_small.render(button_text, True, LEGO_DARK)

            self.surf.blit(t1, (panel.centerx - t1.get_width() // 2, panel.y + 30))
            self.surf.blit(t2, (panel.centerx - t2.get_width() // 2, panel.y + 120))
            self.surf.blit(t3, (panel.centerx - t3.get_width() // 2, panel.y + 190))
            self.surf.blit(t4, (panel.centerx - t4.get_width() // 2, panel.y + 250))
            self.surf.blit(t5, (panel.centerx - t5.get_width() // 2, panel.y + 310))

        self.btn_voltar.draw(self.surf)

        if self.fase_concluida:
            self.fase_concluida.draw(self.surf)
