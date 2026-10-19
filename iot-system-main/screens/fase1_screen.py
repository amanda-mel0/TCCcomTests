import pygame
import random
import math
from ui_components import LegoButton
from screens.audio_manager import play_error, play_success
from screens.fase_concluida import PopupFaseConcluida, avancar_para_proxima_fase

WIDTH, HEIGHT = 1100, 700

# ── Paleta ───────────────────────────────────────────────────────────────────
SKY_TOP    = ( 52, 175, 220)
SKY_BOT    = ( 90, 200, 240)
GRASS_TOP  = ( 80, 185,  70)
GRASS_BOT  = ( 50, 140,  40)
PANEL_BG   = ( 38,  42,  55)
PANEL_BDR  = ( 55,  60,  75)

LEGO_RED    = (196,  40,  27)
LEGO_YELLOW = (245, 205,  47)
LEGO_GREEN  = ( 75, 151,  74)
LEGO_BLUE   = ( 13, 105, 171)
LEGO_ORANGE = (254, 138,  24)
LEGO_PURPLE = (130,  60, 180)
LEGO_WHITE  = (255, 255, 255)
LEGO_DARK   = ( 30,  30,  50)

TAB_COLORS  = [LEGO_RED, LEGO_BLUE, LEGO_GREEN, LEGO_YELLOW, LEGO_ORANGE, LEGO_PURPLE]
BLOCK_COLORS= [LEGO_RED, LEGO_BLUE, LEGO_GREEN, LEGO_ORANGE, LEGO_YELLOW]

PANEL_X = 100
PANEL_Y = 130
PANEL_W = WIDTH - 200
PANEL_H = HEIGHT - 230
TAB_H   = 44
TAB_W   = PANEL_W // len(TAB_COLORS)

BLOCK_W = 120
BLOCK_H = 82
STUD_R  = 11

SLOT_X = PANEL_X + PANEL_W - BLOCK_W - 180
SLOT_Y = PANEL_Y + TAB_H + 180
EQ_Y   = PANEL_Y + TAB_H + 180
ANSWER_Y = PANEL_Y + TAB_H + 310  # era 210 — movido 100px para baixo


class Cloud:
    def __init__(self, x=None):
        self.x  = x if x is not None else random.randint(-200, WIDTH)
        self.y  = random.randint(20, 110)
        self.spd= random.uniform(0.3, 0.8)
        self.sc = random.uniform(0.7, 1.3)

    def update(self):
        self.x += self.spd
        if self.x > WIDTH + 250:
            self.x = -250
            self.y = random.randint(20, 110)

    def draw(self, surf):
        cx, cy = int(self.x), int(self.y)
        sc = self.sc
        for dx, dy, r in [(0,0,34),(28,0,28),(-28,0,24),(14,-16,22),(-10,-12,18)]:
            pygame.draw.circle(surf, (200,230,245), (cx+int(dx*sc)+2, cy+int(dy*sc)+3), int(r*sc))
        for dx, dy, r in [(0,0,34),(28,0,28),(-28,0,24),(14,-16,22),(-10,-12,18)]:
            pygame.draw.circle(surf, LEGO_WHITE, (cx+int(dx*sc), cy+int(dy*sc)), int(r*sc))


class Bubble:
    def __init__(self):
        self.reset(start=True)

    def reset(self, start=False):
        self.x   = random.randint(0, WIDTH)
        self.y   = random.randint(0, HEIGHT) if start else HEIGHT + 20
        self.r   = random.randint(7, 18)
        self.spd = random.uniform(0.5, 1.8)
        self.vx  = random.uniform(-0.5, 0.5)
        self.col = random.choice([LEGO_RED, LEGO_BLUE, LEGO_GREEN, LEGO_ORANGE,
                                  LEGO_PURPLE, LEGO_YELLOW, (180,60,60), (60,60,180)])

    def update(self):
        self.y  -= self.spd
        self.x  += self.vx
        if self.y < -30:
            self.reset()

    def draw(self, surf):
        pygame.draw.circle(surf, self.col, (int(self.x), int(self.y)), self.r)
        lighter = tuple(min(255, c+80) for c in self.col)
        pygame.draw.circle(surf, lighter, (int(self.x)-self.r//3, int(self.y)-self.r//3), self.r//3)
        pygame.draw.circle(surf, tuple(max(0,c-40) for c in self.col),
                           (int(self.x), int(self.y)), self.r, 2)


class AnswerSlot:
    def __init__(self, x, y):
        self.x = x; self.y = y
        self.filled = False
        self.pulse  = 0.0

    def overlaps(self, block):
        cx, cy = block.x+BLOCK_W//2, block.y+BLOCK_H//2
        return self.x < cx < self.x+BLOCK_W and self.y < cy < self.y+BLOCK_H

    def draw(self, surf, font_huge):
        self.pulse += 0.07
        glow = int(abs(math.sin(self.pulse))*50)
        col  = (min(255, 80+glow), min(255, 140+glow), min(255, 210+glow))
        pygame.draw.rect(surf, (50,55,70), (self.x, self.y, BLOCK_W, BLOCK_H), border_radius=10)
        pygame.draw.rect(surf, col,        (self.x, self.y, BLOCK_W, BLOCK_H), 3, border_radius=10)
        txt = font_huge.render("?", True, col)
        surf.blit(txt,(self.x+BLOCK_W//2-txt.get_width()//2,
                       self.y+BLOCK_H//2-txt.get_height()//2+4))


class DragBlock:
    def __init__(self, number, color, x, y):
        self.number   = number
        self.color    = color
        self.x        = float(x)
        self.y        = float(y)
        self.home_x   = float(x)
        self.home_y   = float(y)
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.wobble   = random.uniform(0, math.pi*2)
        self.placed   = False

    def hit(self, mx, my):
        return self.x <= mx <= self.x+BLOCK_W and self.y <= my <= self.y+BLOCK_H

    def return_home(self):
        self.x, self.y = self.home_x, self.home_y
        self.dragging  = False

    def draw(self, surf, font_big, font_med):
        self.wobble += 0.09
        ey = int(math.sin(self.wobble)*3) if not self.dragging and not self.placed else 0
        draw_lego_block(surf, self.color,
                        (int(self.x), int(self.y)+ey, BLOCK_W, BLOCK_H),
                        str(self.number), shadow=not self.dragging,
                        font_big=font_big, font_med=font_med)


class PopupErro:
    def __init__(self):
        play_error()
        self.timer = 0; self.duration = 100; self.scale = 0.3

    def update(self):
        self.timer += 1
        p = self.timer/self.duration
        if p < 0.2:
            self.scale = 0.3+0.7*(p/0.2)
        elif p > 0.7:
            self.scale = max(0.0,1.0-(p-0.7)/0.3)
        else:
            self.scale = 1.0

    def is_done(self):
        return self.timer >= self.duration

    def draw(self, surf, font_big):
        sc = max(0.1,self.scale)
        pw,ph = 420,200
        bw,bh = int(pw*sc),int(ph*sc)
        bx,by = WIDTH//2-bw//2, HEIGHT//2-bh//2

        ov = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        ov.fill((0,0,0,80)); surf.blit(ov,(0,0))

        pygame.draw.rect(surf,(200,50,40),(bx,by,bw,bh),border_radius=24)
        pygame.draw.rect(surf,LEGO_WHITE, (bx,by,bw,bh),4,border_radius=24)
        for sx in range(bx+35,bx+bw-20,50):
            pygame.draw.circle(surf,(220,70,60),(sx,by+16),9)
            pygame.draw.circle(surf,LEGO_WHITE, (sx,by+16),9,2)

        t1 = font_big.render("OPS! Tente outro bloco!", True, LEGO_WHITE)
        t1 = pygame.transform.smoothscale(t1,(int(t1.get_width()*sc),int(t1.get_height()*sc)))
        surf.blit(t1,(WIDTH//2-t1.get_width()//2, by+bh//2-t1.get_height()//2))


class TelaAcerto:
    BTN_W, BTN_H = 300, 68

    def __init__(self):
        play_success()
        self.scale   = 0.3
        self.animate = True
        self.timer   = 0
        self.btn_rect = pygame.Rect(WIDTH//2-self.BTN_W//2, HEIGHT//2+55, self.BTN_W, self.BTN_H)
        self.particles = [
            {"x":random.randint(0,WIDTH),"y":random.randint(-HEIGHT,0),
             "vx":random.uniform(-1.5,1.5),"vy":random.uniform(2,5),
             "color":random.choice([LEGO_RED,LEGO_YELLOW,LEGO_GREEN,LEGO_BLUE,LEGO_ORANGE,LEGO_PURPLE]),
             "size":random.randint(6,14),"rot":random.uniform(0,360),"rot_speed":random.uniform(-4,4)}
            for _ in range(60)
        ]

    def update(self):
        self.timer += 1
        if self.animate:
            self.scale = min(1.0, self.scale+0.07)
            if self.scale >= 1.0:
                self.animate = False
        for p in self.particles:
            p["x"] += p["vx"]; p["y"] += p["vy"]
            p["rot"] = (p["rot"]+p["rot_speed"])%360
            if p["y"] > HEIGHT+20:
                p["y"] = random.randint(-40,-10)
                p["x"] = random.randint(0,WIDTH)

    def check_click(self, mx, my):
        return (not self.animate) and self.btn_rect.collidepoint(mx,my)

    def draw(self, surf, font_big, font_small):
        ov = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        ov.fill((0,0,0,130)); surf.blit(ov,(0,0))

        for p in self.particles:
            s = pygame.Surface((p["size"],p["size"]//2),pygame.SRCALPHA)
            s.fill((*p["color"],210))
            rot = pygame.transform.rotate(s,p["rot"])
            surf.blit(rot,(int(p["x"]),int(p["y"])))

        sc = max(0.1,self.scale)
        pw,ph = 540,270
        bw,bh = int(pw*sc),int(ph*sc)
        bx,by = WIDTH//2-bw//2, HEIGHT//2-bh//2-20

        pygame.draw.rect(surf,(50,175,65),(bx,by,bw,bh),border_radius=26)
        pygame.draw.rect(surf,LEGO_WHITE, (bx,by,bw,bh),5,border_radius=26)
        for sx in range(bx+35,bx+bw-20,50):
            pygame.draw.circle(surf,(70,200,85),(sx,by+16),10)
            pygame.draw.circle(surf,LEGO_WHITE, (sx,by+16),10,2)

        t1 = font_big.render("MUITO BEM!", True, LEGO_WHITE)
        t1 = pygame.transform.smoothscale(t1,(int(t1.get_width()*sc),int(t1.get_height()*sc)))
        surf.blit(t1,(WIDTH//2-t1.get_width()//2, by+bh//2-t1.get_height()-6))

        if not self.animate:
            mx,my = pygame.mouse.get_pos()
            hover = self.btn_rect.collidepoint(mx,my)
            bcol  = LEGO_YELLOW if hover else (200,160,20)
            tcol  = LEGO_DARK   if hover else LEGO_WHITE

            sh = pygame.Surface((self.BTN_W+8,self.BTN_H+8),pygame.SRCALPHA)
            pygame.draw.rect(sh,(0,0,0,80),(4,4,self.BTN_W,self.BTN_H),border_radius=14)
            surf.blit(sh,(self.btn_rect.x-2,self.btn_rect.y+3))

            pygame.draw.rect(surf, bcol, self.btn_rect, border_radius=14)
            pygame.draw.rect(surf, LEGO_DARK, self.btn_rect, 3, border_radius=14)

            for sx in [self.btn_rect.x+32, self.btn_rect.x+self.BTN_W-32]:
                pygame.draw.circle(surf,tuple(min(255,c+30) for c in bcol),(sx,self.btn_rect.y+12),8)
                pygame.draw.circle(surf,LEGO_DARK,(sx,self.btn_rect.y+12),8,2)

            bt = font_small.render("Próximo desafio", True, tcol)
            surf.blit(bt,(self.btn_rect.centerx-bt.get_width()//2,
                          self.btn_rect.centery-bt.get_height()//2))


def draw_lego_block(surf, color, rect, label="", shadow=True, font_big=None, font_med=None):
    x, y, w, h = rect
    sr = STUD_R
    font_lbl = font_big or pygame.font.SysFont("Arial Rounded MT Bold", 44, bold=True)
    if shadow:
        sh = pygame.Surface((w+14, h+14), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0,0,0,70), (5,5,w,h), border_radius=10)
        surf.blit(sh, (x-2, y+4))

    darker  = tuple(max(0, c-55) for c in color)
    lighter = tuple(min(255, c+55) for c in color)
    deepest = tuple(max(0, c-90) for c in color)

    pygame.draw.rect(surf, color, (x, y, w, h), border_radius=10)
    d = 7
    pygame.draw.polygon(surf, darker, [
        (x+w, y+4),(x+w+d, y+4+d),(x+w+d, y+h+d),(x+w, y+h)])
    pygame.draw.polygon(surf, deepest, [
        (x, y+h),(x+d, y+h+d),(x+w+d, y+h+d),(x+w, y+h)])
    pygame.draw.rect(surf, lighter, (x,   y,   w, 4), border_radius=4)
    pygame.draw.rect(surf, lighter, (x,   y,   4, h), border_radius=4)
    pygame.draw.rect(surf, darker,  (x,   y,   w, h), 3, border_radius=10)

    for sx in [x+w//3, x+2*w//3]:
        sy = y - sr + 4
        sc2 = tuple(min(255,c+20) for c in color)
        pygame.draw.ellipse(surf, sc2,    (sx-sr, sy-sr//2, sr*2, sr))
        pygame.draw.ellipse(surf, darker, (sx-sr, sy-sr//2, sr*2, sr), 2)
        pygame.draw.rect(surf, sc2,       (sx-sr, sy, sr*2, sr//2+2))
        pygame.draw.rect(surf, darker,    (sx-sr, sy, sr*2, sr//2+2), 2)
        pygame.draw.ellipse(surf, tuple(min(255,c+90) for c in color),
                            (sx-sr+3, sy-sr//2+2, sr*2-6, sr//2))

    if label:
        txt = (font_big or pygame.font.SysFont("Arial Rounded MT Bold", 44, bold=True)).render(label, True, LEGO_WHITE)
        sh2 = (font_big or pygame.font.SysFont("Arial Rounded MT Bold", 44, bold=True)).render(label, True, darker)
        tx = x + w//2 - txt.get_width()//2
        ty = y + h//2 - txt.get_height()//2 + 2
        surf.blit(sh2, (tx+2, ty+2))
        surf.blit(txt, (tx, ty))


def draw_panel(surf):
    sh = pygame.Surface((PANEL_W+12, PANEL_H+12), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0,0,0,100), (6,6,PANEL_W,PANEL_H), border_radius=14)
    surf.blit(sh, (PANEL_X-3, PANEL_Y+6))
    pygame.draw.rect(surf, PANEL_BG, (PANEL_X, PANEL_Y, PANEL_W, PANEL_H), border_radius=12)
    pygame.draw.rect(surf, PANEL_BDR,(PANEL_X, PANEL_Y, PANEL_W, PANEL_H), 3, border_radius=12)
    for i, col in enumerate(TAB_COLORS):
        tx = PANEL_X + i*TAB_W
        ty = PANEL_Y - TAB_H + 8
        tw = TAB_W - 4
        darker  = tuple(max(0,c-50) for c in col)
        lighter = tuple(min(255,c+50) for c in col)
        pygame.draw.rect(surf, col,     (tx, ty, tw, TAB_H), border_radius=8)
        pygame.draw.rect(surf, lighter, (tx, ty, tw, 4),     border_radius=4)
        pygame.draw.rect(surf, darker,  (tx, ty, tw, TAB_H), 2, border_radius=8)
        sx = tx + tw//2
        sy = ty - 9
        pygame.draw.circle(surf, tuple(min(255,c+30) for c in col), (sx, sy), 10)
        pygame.draw.circle(surf, darker, (sx, sy), 10, 2)
        pygame.draw.circle(surf, lighter, (sx-3, sy-3), 4)
    bar_y = PANEL_Y + PANEL_H - 18
    pygame.draw.rect(surf, LEGO_GREEN, (PANEL_X, bar_y, PANEL_W, 18), border_radius=6)
    pygame.draw.rect(surf, (50,140,40),(PANEL_X, bar_y, PANEL_W, 18), 2, border_radius=6)


def draw_background(surf, tick):
    for y in range(HEIGHT - 80):
        t = y / (HEIGHT - 80)
        r = int(SKY_TOP[0] + (SKY_BOT[0]-SKY_TOP[0])*t)
        g = int(SKY_TOP[1] + (SKY_BOT[1]-SKY_TOP[1])*t)
        b = int(SKY_TOP[2] + (SKY_BOT[2]-SKY_TOP[2])*t)
        pygame.draw.line(surf, (r,g,b), (0,y), (WIDTH,y))
    grass_y = HEIGHT - 80
    pygame.draw.rect(surf, GRASS_TOP, (0, grass_y, WIDTH, 80))
    pygame.draw.rect(surf, GRASS_BOT, (0, grass_y+18, WIDTH, 62))
    for gx in range(0, WIDTH, 22):
        h2 = random.randint(8, 18) if tick == 0 else 12
        col = (90, 200, 75) if (gx//22)%2==0 else (70,175,60)
        pygame.draw.polygon(surf, col, [
            (gx, grass_y), (gx+11, grass_y-12), (gx+22, grass_y)])


def gerar_pergunta():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    resp = a + b
    erradas = set()
    while len(erradas) < 3:
        e = resp + random.choice([-3,-2,-1,1,2,3])
        if e != resp and e > 0 and e not in erradas:
            erradas.add(e)
    opcoes = [resp] + list(erradas)
    random.shuffle(opcoes)
    return a, b, resp, opcoes


def draw_equation(surf, a, b, font_huge):
    avail_cx = PANEL_X + (PANEL_W - BLOCK_W - 80) // 2
    eq_y     = EQ_Y
    ax = avail_cx - BLOCK_W - 90
    draw_lego_block(surf, LEGO_GREEN,  (ax, eq_y, BLOCK_W, BLOCK_H), str(a), font_big=font_huge)
    plus = font_huge.render("+", True, LEGO_YELLOW)
    surf.blit(plus, (ax+BLOCK_W+14, eq_y+BLOCK_H//2-plus.get_height()//2))
    bx = ax + BLOCK_W + 14 + plus.get_width() + 14
    draw_lego_block(surf, LEGO_ORANGE, (bx, eq_y, BLOCK_W, BLOCK_H), str(b), font_big=font_huge)
    eq = font_huge.render("=", True, LEGO_YELLOW)
    surf.blit(eq, (bx+BLOCK_W+14, eq_y+BLOCK_H//2-eq.get_height()//2))


def new_round():
    a, b, resp, opcoes = gerar_pergunta()
    cores = random.sample(BLOCK_COLORS, 4)
    total_w = 4*BLOCK_W + 3*20
    start_x = PANEL_X + (PANEL_W - total_w)//2
    blocks = []
    for i, num in enumerate(opcoes):
        bx = start_x + i*(BLOCK_W+20)
        blocks.append(DragBlock(num, cores[i], bx, ANSWER_Y))
    slot = AnswerSlot(SLOT_X, SLOT_Y)
    return a, b, resp, blocks, slot


class Fase1Screen:
    def __init__(self, surf, largura, altura, cores, estado):
        self.surf = surf
        self.W = largura
        self.H = altura
        self.cores = cores
        self.estado = estado
        self.tick = 0
        self.font_huge  = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_big   = pygame.font.SysFont("Arial", 44, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 52, bold=True)
        self.btn_voltar = LegoButton(40, self.H - 70, 200, 46,
                                    "VOLTAR AO MAPA", self.cores["cinza_med"], self.font_small, studs=0)
        self.clouds = [Cloud(random.randint(0, WIDTH)) for _ in range(7)]
        self.bubbles = [Bubble() for _ in range(28)]
        self.a, self.b, self.correct, self.blocks, self.slot = new_round()
        self.popup_erro = None
        self.tela_acerto = None
        self.fase_concluida = None
        self.drag_block = None
        self.pontos = 0
        self.round = 1
        self.max_rounds = 5

    def handle_events(self, eventos):
        for ev in eventos:
            if self.btn_voltar.handle_event(ev):
                self.estado["tela_atual"] = "mapa"
                return
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.estado["tela_atual"] = "mapa"
                return

            if ev.type == pygame.MOUSEBUTTONDOWN and self.tela_acerto:
                mx,my = ev.pos
                if self.tela_acerto.check_click(mx,my):
                    if self.round < self.max_rounds:
                        self.round += 1
                        self.start_next_round()
                    else:
                        self.estado["tela_atual"] = "mapa"
                continue

            if ev.type == pygame.MOUSEBUTTONDOWN and self.fase_concluida:
                if self.fase_concluida.handle_event(ev):
                    avancar_para_proxima_fase(self.estado)
                continue

            if self.popup_erro is None and self.tela_acerto is None and not self.fase_concluida:
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    mx,my = ev.pos
                    for blk in self.blocks:
                        if not blk.placed and blk.hit(mx,my):
                            self.drag_block = blk
                            blk.dragging = True
                            blk.offset_x = blk.x-mx
                            blk.offset_y = blk.y-my
                            break

                if ev.type == pygame.MOUSEMOTION and self.drag_block:
                    mx,my = ev.pos
                    self.drag_block.x = mx + self.drag_block.offset_x
                    self.drag_block.y = my + self.drag_block.offset_y

                if ev.type == pygame.MOUSEBUTTONUP and self.drag_block:
                    if self.slot.overlaps(self.drag_block):
                        if self.drag_block.number == self.correct:
                            self.drag_block.x = self.slot.x
                            self.drag_block.y = self.slot.y
                            self.drag_block.dragging = False
                            self.drag_block.placed = True
                            self.slot.filled = True
                            self.pontos += 1
                            if self.round < self.max_rounds:
                                self.tela_acerto = TelaAcerto()
                            else:
                                play_success()
                                self.fase_concluida = PopupFaseConcluida(self.W, self.H, self.estado)
                        else:
                            self.drag_block.return_home()
                            self.popup_erro = PopupErro()
                    else:
                        self.drag_block.return_home()
                    self.drag_block = None

    def update(self):
        self.tick += 1
        for p in self.clouds:
            p.update()
        for b2 in self.bubbles:
            b2.update()
        if self.popup_erro:
            self.popup_erro.update()
            if self.popup_erro.is_done():
                self.popup_erro = None
        if self.tela_acerto:
            self.tela_acerto.update()

    def start_next_round(self):
        self.a, self.b, self.correct, self.blocks, self.slot = new_round()
        self.popup_erro = None
        self.tela_acerto = None
        self.drag_block = None

    def draw(self):
        draw_background(self.surf, self.tick)
        for b2 in self.bubbles:
            if not (PANEL_X < b2.x < PANEL_X+PANEL_W and PANEL_Y < b2.y < PANEL_Y+PANEL_H):
                b2.draw(self.surf)
        for c in self.clouds:
            c.draw(self.surf)
        draw_panel(self.surf)
        tt = self.font_title.render("Matemática  -  Fase 1", True, LEGO_YELLOW)
        ts = self.font_title.render("Matemática  -  Fase 1", True, (0,0,0))
        self.surf.blit(ts, (WIDTH//2-tt.get_width()//2+2, PANEL_Y+TAB_H+14))
        self.surf.blit(tt, (WIDTH//2-tt.get_width()//2,   PANEL_Y+TAB_H+12))
        sep_y = PANEL_Y + TAB_H + 62
        pygame.draw.rect(self.surf, LEGO_GREEN, (PANEL_X+20, sep_y, PANEL_W-40, 4), border_radius=2)
        inst = self.font_small.render("Arraste o bloco com a resposta certa até o ?", True, (180,195,220))
        self.surf.blit(inst,(WIDTH//2-inst.get_width()//2, sep_y+8))
        draw_equation(self.surf, self.a, self.b, self.font_huge)
        if not self.slot.filled:
            self.slot.draw(self.surf, self.font_huge)
        for blk in self.blocks:
            if blk != self.drag_block:
                blk.draw(self.surf, self.font_big, self.font_med)
        if self.drag_block:
            self.drag_block.draw(self.surf, self.font_big, self.font_med)
        for blk in self.blocks:
            if blk.placed:
                draw_lego_block(self.surf, blk.color, (self.slot.x,self.slot.y,BLOCK_W,BLOCK_H), str(blk.number),
                                font_big=self.font_big, font_med=self.font_med)
        round_txt = self.font_med.render(f"Questão {self.round}/{self.max_rounds}", True, LEGO_YELLOW)
        round_shadow = self.font_med.render(f"Questão {self.round}/{self.max_rounds}", True, (0,0,0))
        self.surf.blit(round_shadow, (PANEL_X+22, PANEL_Y+TAB_H+PANEL_H-84))
        self.surf.blit(round_txt, (PANEL_X+20, PANEL_Y+TAB_H+PANEL_H-86))

        pts = self.font_med.render(f"Pontos: {self.pontos}", True, LEGO_YELLOW)
        ps2 = self.font_med.render(f"Pontos: {self.pontos}", True, (0,0,0))
        self.surf.blit(ps2,(PANEL_X+22, PANEL_Y+TAB_H+PANEL_H-52))
        self.surf.blit(pts,(PANEL_X+20, PANEL_Y+TAB_H+PANEL_H-54))
        if self.popup_erro:
            self.popup_erro.draw(self.surf, self.font_big)
        if self.tela_acerto:
            self.tela_acerto.draw(self.surf, self.font_big, self.font_small)
        if self.fase_concluida:
            self.fase_concluida.draw(self.surf)
        self.btn_voltar.draw(self.surf)