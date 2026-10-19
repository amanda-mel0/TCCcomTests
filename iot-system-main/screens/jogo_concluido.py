import math
import random

import pygame

from screens.audio_manager import play_game_complete
from ui_components import LegoButton, draw_lego_brick


LEGO_YELLOW = (245, 205, 47)
LEGO_RED = (196, 40, 27)
LEGO_BLUE = (13, 105, 171)
LEGO_GREEN = (75, 151, 74)
LEGO_ORANGE = (254, 138, 24)
LEGO_PURPLE = (130, 60, 180)
LEGO_WHITE = (255, 255, 255)
LEGO_DARK = (30, 30, 50)
SKY_TOP = (70, 180, 235)
SKY_BOTTOM = (135, 215, 245)
GOLD_LIGHT = (255, 238, 120)
GOLD_DARK = (210, 145, 18)


class Confetti:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        self.reset(start=True)

    def reset(self, start=False):
        self.x = random.randint(0, self.largura)
        self.y = random.randint(-self.altura, 0) if start else random.randint(-80, -10)
        self.vx = random.uniform(-0.8, 0.8)
        self.vy = random.uniform(1.8, 4.2)
        self.size = random.randint(8, 16)
        self.rot = random.uniform(0, math.pi * 2)
        self.rot_speed = random.uniform(-0.12, 0.12)
        self.color = random.choice([LEGO_YELLOW, LEGO_RED, LEGO_BLUE, LEGO_GREEN, LEGO_ORANGE, LEGO_PURPLE])

    def update(self):
        self.x += self.vx + math.sin(self.rot) * 0.35
        self.y += self.vy
        self.rot += self.rot_speed
        if self.y > self.altura + 20:
            self.reset()

    def draw(self, surf):
        w = self.size
        h = max(4, self.size // 2)
        piece = pygame.Surface((w, h), pygame.SRCALPHA)
        piece.fill((*self.color, 230))
        rotated = pygame.transform.rotate(piece, math.degrees(self.rot))
        surf.blit(rotated, (int(self.x), int(self.y)))


class Sparkle:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        self.reset()

    def reset(self):
        self.x = random.randint(80, self.largura - 80)
        self.y = random.randint(45, self.altura - 170)
        self.size = random.randint(5, 13)
        self.phase = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(0.05, 0.1)
        self.color = random.choice([LEGO_YELLOW, LEGO_WHITE, LEGO_ORANGE])

    def update(self):
        self.phase += self.speed
        if self.phase > math.pi * 2:
            self.reset()

    def draw(self, surf):
        pulse = (math.sin(self.phase) + 1) / 2
        alpha = int(70 + pulse * 185)
        length = int(self.size + pulse * self.size)
        cx, cy = int(self.x), int(self.y)
        color = (*self.color, alpha)

        layer = pygame.Surface((length * 2 + 6, length * 2 + 6), pygame.SRCALPHA)
        center = layer.get_width() // 2
        pygame.draw.line(layer, color, (center - length, center), (center + length, center), 3)
        pygame.draw.line(layer, color, (center, center - length), (center, center + length), 3)
        pygame.draw.circle(layer, color, (center, center), max(2, length // 4))
        surf.blit(layer, (cx - center, cy - center))


class FloatingBrick:
    def __init__(self, largura, altura, index):
        self.largura = largura
        self.altura = altura
        self.index = index
        self.w = random.randint(58, 92)
        self.h = random.randint(28, 40)
        self.x = random.randint(-80, largura + 80)
        self.y = random.randint(145, altura - 150)
        self.speed = random.uniform(0.35, 0.85)
        self.wave = random.uniform(16, 32)
        self.phase = random.uniform(0, math.pi * 2)
        self.color = random.choice([LEGO_RED, LEGO_BLUE, LEGO_GREEN, LEGO_ORANGE, LEGO_PURPLE])

    def update(self):
        self.x += self.speed
        self.phase += 0.035
        if self.x > self.largura + 100:
            self.x = -120
            self.y = random.randint(145, self.altura - 150)

    def draw(self, surf):
        y = int(self.y + math.sin(self.phase) * self.wave)
        draw_lego_brick(surf, self.color, (int(self.x), y, self.w, self.h), studs=2, raio_borda=8)


class JogoConcluidoScreen:
    def __init__(self, surf, largura, altura, cores, estado):
        self.surf = surf
        self.W = largura
        self.H = altura
        self.cores = cores
        self.estado = estado
        self.tick = 0

        self.font_title = pygame.font.SysFont("Verdana", 68, bold=True)
        self.font_big = pygame.font.SysFont("Verdana", 40, bold=True)
        self.font_med = pygame.font.SysFont("Verdana", 28, bold=True)
        self.font_small = pygame.font.SysFont("Verdana", 23, bold=True)

        self.btn_mapa = LegoButton(
            self.W // 2 - 150,
            self.H - 105,
            300,
            58,
            "VOLTAR AO MAPA",
            self.cores["verde"],
            self.font_small,
            studs=0,
        )
        self.confetti = [Confetti(self.W, self.H) for _ in range(125)]
        self.sparkles = [Sparkle(self.W, self.H) for _ in range(30)]
        self.bricks = [FloatingBrick(self.W, self.H, i) for i in range(10)]
        self.audio_tocado = False

    def handle_events(self, eventos):
        for ev in eventos:
            if self.btn_mapa.handle_event(ev):
                self.estado["tela_atual"] = "mapa"
                self.estado["fase_atual"] = 10
                return
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self.estado["tela_atual"] = "mapa"
                self.estado["fase_atual"] = 10
                return

    def update(self):
        if not self.audio_tocado:
            play_game_complete()
            self.audio_tocado = True

        self.tick += 1
        for c in self.confetti:
            c.update()
        for s in self.sparkles:
            s.update()
        for b in self.bricks:
            b.update()

    def draw(self):
        self._draw_background()
        for b in self.bricks:
            b.draw(self.surf)
        self._draw_sunburst()
        for s in self.sparkles:
            s.draw(self.surf)
        for c in self.confetti:
            c.draw(self.surf)
        self._draw_certificate()
        self.btn_mapa.draw(self.surf)

    def _draw_background(self):
        for y in range(self.H):
            t = y / max(1, self.H)
            r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t)
            g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t)
            b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t)
            pygame.draw.line(self.surf, (r, g, b), (0, y), (self.W, y))

        pygame.draw.rect(self.surf, (80, 180, 80), (0, self.H - 95, self.W, 95))
        pygame.draw.rect(self.surf, (60, 150, 60), (0, self.H - 70, self.W, 70))

        for x in range(-80, self.W + 120, 180):
            y = 95 + int(math.sin(self.tick * 0.02 + x) * 8)
            self._draw_cloud(x, y)

        self._draw_stage()

    def _draw_sunburst(self):
        cx, cy = self.W // 2, self.H // 2 - 50
        rays = 18
        radius = 560
        for i in range(rays):
            angle = (self.tick * 0.012) + i * (math.pi * 2 / rays)
            next_angle = angle + math.pi * 2 / (rays * 2.6)
            p1 = (cx, cy)
            p2 = (cx + math.cos(angle) * radius, cy + math.sin(angle) * radius)
            p3 = (cx + math.cos(next_angle) * radius, cy + math.sin(next_angle) * radius)
            ray = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            pygame.draw.polygon(ray, (255, 255, 255, 24), [p1, p2, p3])
            self.surf.blit(ray, (0, 0))

    def _draw_cloud(self, x, y):
        for dx, dy, r in [(-38, 4, 24), (-12, -10, 34), (20, -4, 28), (46, 8, 22)]:
            pygame.draw.circle(self.surf, LEGO_WHITE, (x + dx, y + dy), r)

    def _draw_stage(self):
        pygame.draw.ellipse(self.surf, (30, 90, 55), (240, self.H - 145, self.W - 480, 72))
        for i, color in enumerate([LEGO_RED, LEGO_BLUE, LEGO_YELLOW, LEGO_GREEN, LEGO_ORANGE, LEGO_PURPLE]):
            x = 70 + i * 162
            y = self.H - 96 + int(math.sin(self.tick * 0.08 + i) * 5)
            draw_lego_brick(self.surf, color, (x, y, 118, 48), studs=3, raio_borda=9)

    def _draw_outlined_text(self, text, font, center, fill, outline=LEGO_DARK, width=3):
        base = font.render(text, True, fill)
        shadow = font.render(text, True, (0, 0, 0))
        rect = base.get_rect(center=center)
        shadow_rect = shadow.get_rect(center=(center[0] + 4, center[1] + 5))
        self.surf.blit(shadow, shadow_rect)

        for ox in range(-width, width + 1):
            for oy in range(-width, width + 1):
                if ox == 0 and oy == 0:
                    continue
                if ox * ox + oy * oy <= width * width:
                    outline_surf = font.render(text, True, outline)
                    self.surf.blit(outline_surf, outline_surf.get_rect(center=(center[0] + ox, center[1] + oy)))

        self.surf.blit(base, rect)

    def _draw_certificate(self):
        card_w = min(805, self.W - 90)
        card_h = 435
        x = self.W // 2 - card_w // 2
        y = self.H // 2 - card_h // 2 - 25
        bob = int(math.sin(self.tick * 0.055) * 5)
        y += bob

        pygame.draw.rect(self.surf, (0, 0, 0, 70), (x + 10, y + 12, card_w, card_h), border_radius=24)
        pygame.draw.rect(self.surf, LEGO_YELLOW, (x, y, card_w, card_h), border_radius=24)
        pygame.draw.rect(self.surf, LEGO_DARK, (x, y, card_w, card_h), 6, border_radius=24)
        pygame.draw.rect(self.surf, (255, 235, 120), (x + 24, y + 24, card_w - 48, card_h - 48), border_radius=16)
        pygame.draw.rect(self.surf, LEGO_BLUE, (x + 24, y + 24, card_w - 48, card_h - 48), 4, border_radius=16)

        for sx in range(x + 70, x + card_w - 50, 80):
            pygame.draw.circle(self.surf, (255, 225, 80), (sx, y + 25), 14)
            pygame.draw.circle(self.surf, LEGO_DARK, (sx, y + 25), 14, 2)

        self._draw_trophy(self.W // 2, y + 102)

        pulse = 1 + math.sin(self.tick * 0.08) * 0.035
        title = self.font_title.render("PARABÉNS!", True, LEGO_BLUE)
        title = pygame.transform.smoothscale(
            title,
            (int(title.get_width() * pulse), int(title.get_height() * pulse)),
        )
        title_center = (self.W // 2, y + 186)
        for ox, oy in [(-4, 0), (4, 0), (0, -4), (0, 4), (-3, -3), (3, 3), (-3, 3), (3, -3)]:
            outline = pygame.transform.smoothscale(
                self.font_title.render("PARABÉNS!", True, LEGO_WHITE),
                (title.get_width(), title.get_height()),
            )
            self.surf.blit(outline, outline.get_rect(center=(title_center[0] + ox, title_center[1] + oy)))
        self.surf.blit(title, title.get_rect(center=title_center))

        self._draw_outlined_text("VOCÊ COMPLETOU", self.font_big, (self.W // 2, y + 254), LEGO_RED, width=2)
        self._draw_outlined_text("TODAS AS FASES!", self.font_big, (self.W // 2, y + 313), LEGO_BLUE, width=2)

        ribbon_rect = pygame.Rect(self.W // 2 - 300, y + 350, 600, 54)
        pygame.draw.rect(self.surf, LEGO_GREEN, ribbon_rect, border_radius=12)
        pygame.draw.rect(self.surf, (35, 115, 55), ribbon_rect, 4, border_radius=12)
        note = self.font_med.render("Pequeno construtor da leitura", True, LEGO_WHITE)
        self.surf.blit(note, note.get_rect(center=ribbon_rect.center))

    def _draw_trophy(self, cx, cy):
        lift = int(math.sin(self.tick * 0.09) * 7)
        cy += lift
        glow = pygame.Surface((190, 170), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 240, 80, 90), (95, 88), 78)
        pygame.draw.circle(glow, (255, 255, 255, 45), (95, 88), 52)
        self.surf.blit(glow, (cx - 95, cy - 95))

        pygame.draw.rect(self.surf, GOLD_LIGHT, (cx - 38, cy - 38, 76, 76), border_radius=12)
        pygame.draw.rect(self.surf, GOLD_DARK, (cx - 38, cy - 38, 76, 76), 5, border_radius=12)
        pygame.draw.arc(self.surf, GOLD_LIGHT, (cx - 82, cy - 28, 55, 60), math.pi * 0.5, math.pi * 1.55, 9)
        pygame.draw.arc(self.surf, GOLD_LIGHT, (cx + 27, cy - 28, 55, 60), math.pi * 1.45, math.pi * 2.5, 9)
        pygame.draw.arc(self.surf, GOLD_DARK, (cx - 82, cy - 28, 55, 60), math.pi * 0.5, math.pi * 1.55, 3)
        pygame.draw.arc(self.surf, GOLD_DARK, (cx + 27, cy - 28, 55, 60), math.pi * 1.45, math.pi * 2.5, 3)
        pygame.draw.rect(self.surf, LEGO_DARK, (cx - 13, cy + 38, 26, 35), border_radius=4)
        pygame.draw.rect(self.surf, LEGO_BLUE, (cx - 58, cy + 70, 116, 22), border_radius=6)
        pygame.draw.rect(self.surf, LEGO_DARK, (cx - 58, cy + 70, 116, 22), 3, border_radius=6)
        star = self.font_big.render("*", True, LEGO_WHITE)
        self.surf.blit(star, star.get_rect(center=(cx, cy)))
