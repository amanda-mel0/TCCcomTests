import pygame
import random
import math
from ui_components import LegoButton
from screens.audio_manager import play_error, play_success
from screens.fase_concluida import PopupFaseConcluida, avancar_para_proxima_fase

WIDTH, HEIGHT = 1100, 700

LEGO_RED      = (196, 40,  27)
LEGO_YELLOW   = (245, 205,  47)
LEGO_GREEN    = ( 75, 151,  74)
LEGO_BLUE     = ( 13, 105, 171)
LEGO_ORANGE   = (254, 138,  24)
LEGO_WHITE    = (255, 255, 255)
LEGO_DARK     = ( 30,  30,  50)
BG_COLOR      = ( 30,  50,  90)

BALL_RADIUS = 52
SPEED       = 3.8

TARGET_OPTIONS = [
    ("azul", LEGO_BLUE),
    ("vermelha", LEGO_RED),
    ("verde", LEGO_GREEN),
    ("laranja", LEGO_ORANGE),
]

class Ball:
    def __init__(self, color, name, x, y, vx, vy):
        self.color  = color
        self.name   = name
        self.x      = float(x)
        self.y      = float(y)
        self.vx     = vx
        self.vy     = vy
        self.radius = BALL_RADIUS

    def update(self):
        self.x += self.vx
        self.y += self.vy
        r = self.radius
        if self.x - r < 0:
            self.x = float(r); self.vx = abs(self.vx)
        if self.x + r > WIDTH:
            self.x = float(WIDTH - r); self.vx = -abs(self.vx)
        if self.y - r < 80:
            self.y = float(80 + r); self.vy = abs(self.vy)
        if self.y + r > HEIGHT:
            self.y = float(HEIGHT - r); self.vy = -abs(self.vy)

    def draw(self, surf):
        r  = self.radius
        cx = int(self.x)
        cy = int(self.y)
        shadow = pygame.Surface((r*2+10, r*2+10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,60), (5, r//2+5, r*2, r))
        surf.blit(shadow, (cx - r, cy - r//2 + 4))
        pygame.draw.circle(surf, self.color, (cx, cy), r)
        shine_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(shine_surf, (255,255,255,90), (r - r//3, r - r//3), r//2)
        surf.blit(shine_surf, (cx - r, cy - r))
        darker = tuple(max(0, c - 60) for c in self.color)
        pygame.draw.circle(surf, darker, (cx, cy), r, 5)
        stud_r = r // 4
        stud_y = cy - r + stud_r + 4
        pygame.draw.circle(surf, tuple(min(255, c+40) for c in self.color), (cx, stud_y), stud_r)
        pygame.draw.circle(surf, darker, (cx, stud_y), stud_r, 3)

    def is_clicked(self, mx, my):
        return math.hypot(mx - self.x, my - self.y) <= self.radius


def spawn_balls(target_name=None, target_color=None):
    positions = [(250, 220), (820, 200), (220, 470), (780, 450)]
    random.shuffle(positions)
    if target_name is None or target_color is None:
        target_name, target_color = random.choice(TARGET_OPTIONS)

    options = [(target_name, target_color)]
    others = [opt for opt in TARGET_OPTIONS if opt[0] != target_name]
    random.shuffle(others)
    options.extend(others[:3])
    random.shuffle(options)

    balls = []
    for i, (name, color) in enumerate(options):
        x, y = positions[i]
        angle = random.uniform(0, math.pi * 2)
        spd = SPEED + random.uniform(-0.8, 0.8)
        vx = math.cos(angle) * spd
        vy = math.sin(angle) * spd
        balls.append(Ball(color, name, x, y, vx, vy))
    return balls

class Popup:
    def __init__(self, success, target_name=None):
        self.success     = success
        self.target_name = target_name
        self.timer       = 0
        self.duration    = 120
        self.alpha       = 0
        self.scale       = 0.4

    def update(self):
        self.timer += 1
        progress = self.timer / self.duration
        if progress < 0.15:
            self.alpha = int(255 * progress / 0.15)
            self.scale = 0.4 + 0.6 * (progress / 0.15)
        elif progress > 0.75:
            self.alpha = int(255 * (1 - (progress - 0.75) / 0.25))
        else:
            self.alpha = 255
            self.scale = 1.0

    def is_done(self):
        return self.timer >= self.duration

    def draw(self, surf, font_big, font_small):
        target_label = (self.target_name or "?").upper()
        if self.success:
            bg_color  = (50, 180, 60)
            line1     = "MUITO BEM!"
            line2     = f"VOCÊ ACHOU A BOLA {target_label}!"
        else:
            bg_color  = (200, 50, 40)
            line1     = "OPS!"
            line2     = f"PROCURE A BOLA {target_label}!"

        pw, ph = 520, 300
        bw = int(pw * self.scale)
        bh = int(ph * self.scale)
        bx = WIDTH//2 - bw//2
        by = HEIGHT//2 - bh//2

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(140, self.alpha//2)))
        surf.blit(overlay, (0, 0))

        box = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.rect(box, (*bg_color, self.alpha), (0, 0, bw, bh), border_radius=30)
        pygame.draw.rect(box, (255, 255, 255, self.alpha), (0, 0, bw, bh), 6, border_radius=30)
        for sx in range(40, bw - 20, 55):
            pygame.draw.circle(box, (*tuple(min(255,c+30) for c in bg_color), self.alpha), (sx, 18), 12)
            pygame.draw.circle(box, (255,255,255, self.alpha//3), (sx, 18), 12, 2)
        surf.blit(box, (bx, by))

        scale_f = max(0.4, self.scale)
        txt1 = font_big.render(line1, True, LEGO_WHITE)
        txt2 = font_small.render(line2, True, LEGO_WHITE)
        txt1 = pygame.transform.smoothscale(txt1, (int(txt1.get_width()*scale_f), int(txt1.get_height()*scale_f)))
        txt2 = pygame.transform.smoothscale(txt2, (int(txt2.get_width()*scale_f*0.85), int(txt2.get_height()*scale_f*0.85)))
        surf.blit(txt1, (WIDTH//2 - txt1.get_width()//2, by + bh//2 - txt1.get_height() - 10))
        surf.blit(txt2, (WIDTH//2 - txt2.get_width()//2, by + bh//2 + 10))


def beep(freq=440, duration=200, volume=0.5):
    try:
        sample_rate = 44100
        n_samples = int(sample_rate * duration / 1000)
        buf = bytearray(n_samples * 2)
        for i in range(n_samples):
            t = i / sample_rate
            val = int(32767 * volume * math.sin(2 * math.pi * freq * t))
            val = max(-32768, min(32767, val))
            buf[i*2]     = val & 0xFF
            buf[i*2 + 1] = (val >> 8) & 0xFF
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(volume)
        sound.play()
    except Exception:
        pass

class Fase2Screen:
    def __init__(self, surf, largura, altura, cores, estado):
        self.surf = surf
        self.W = largura
        self.H = altura
        self.cores = cores
        self.estado = estado
        self.tick = 0
        self.font_big   = pygame.font.SysFont("Arial Rounded MT Bold", 52, bold=True)
        self.font_med   = pygame.font.SysFont("Arial Rounded MT Bold", 52, bold=True)
        self.font_small = pygame.font.SysFont("Arial Rounded MT Bold", 40, bold=True)
        self.btn_voltar = LegoButton(40, self.H - 70, 280, 46,
                                    " VOLTAR AO MAPA", self.cores["cinza_med"], self.font_small, studs=0)
        self.popup  = None
        self.fase_concluida = None
        self.score  = 0
        self.misses = 0
        self.round = 1
        self.max_rounds = 5
        self.last_target = None
        self.current_target_name = None
        self.current_target_color = None
        self.sound_on = False
        self._choose_target()
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.sound_on = True
        except Exception:
            self.sound_on = False

    def _choose_target(self):
        options = [opt for opt in TARGET_OPTIONS if opt[0] != self.last_target]
        self.current_target_name, self.current_target_color = random.choice(options)
        self.last_target = self.current_target_name
        self.balls = spawn_balls(self.current_target_name, self.current_target_color)

    def handle_events(self, eventos):
        for ev in eventos:
            if self.btn_voltar.handle_event(ev):
                self.estado["tela_atual"] = "mapa"
                return
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.estado["tela_atual"] = "mapa"
                return
            if ev.type == pygame.MOUSEBUTTONDOWN and self.fase_concluida:
                if self.fase_concluida.handle_event(ev):
                    avancar_para_proxima_fase(self.estado)
                continue

            if ev.type == pygame.MOUSEBUTTONDOWN and self.popup is None and self.fase_concluida is None:
                mx,my = ev.pos
                for ball in self.balls:
                    if ball.is_clicked(mx, my):
                        if ball.name == self.current_target_name:
                            self.score += 1
                            self.popup = Popup(success=True, target_name=self.current_target_name)
                            play_success()
                        else:
                            self.misses += 1
                            self.popup = Popup(success=False, target_name=self.current_target_name)
                            play_error()
                        break

    def update(self):
        self.tick += 1

        if self.popup is None and self.fase_concluida is None:
            for ball in self.balls:
                ball.update()

        elif self.popup:
            self.popup.update()

            if self.popup.is_done():
                self.popup = None

                # Próxima rodada
                if self.round < self.max_rounds:
                    self.round += 1
                    self._choose_target()

                # Fim da fase
                else:
                    self.fase_concluida = PopupFaseConcluida(self.W, self.H, self.estado)

    def draw(self):
        self.surf.fill(BG_COLOR)
        for row in range(0, HEIGHT, 60):
            for col in range(0, WIDTH, 60):
                off = int(math.sin(self.tick * 0.02 + row * 0.05 + col * 0.03) * 2)
                pygame.draw.circle(self.surf, (40, 65, 110), (col + 30, row + 30 + off), 8)
                pygame.draw.circle(self.surf, (50, 80, 130), (col + 30, row + 30 + off), 8, 2)
        pygame.draw.rect(self.surf, LEGO_RED, (0, 0, WIDTH, 75))
        pygame.draw.rect(self.surf, LEGO_YELLOW, (0, 72, WIDTH, 6))
        for sx in range(35, WIDTH, 70):
            pygame.draw.circle(self.surf, (220, 50, 35), (sx, 30), 18)
            pygame.draw.circle(self.surf, (240, 80, 60), (sx, 30), 18, 3)
            pygame.draw.circle(self.surf, (255,200,190,120), (sx-5, 22), 7)
        target_label = (self.current_target_name or "?").upper()
        prompt_text = f"Clique na bola {target_label}!"
        shadow = self.font_big.render(prompt_text, True, (0,0,0))
        self.surf.blit(shadow, (WIDTH//2 - shadow.get_width()//2 + 2, 14))
        title = self.font_big.render(prompt_text, True, LEGO_YELLOW)
        self.surf.blit(title, (WIDTH//2 - title.get_width()//2, 12))
        round_txt = self.font_small.render(f"Rodada {self.round}/{self.max_rounds}", True, LEGO_WHITE)
        self.surf.blit(round_txt, (30, HEIGHT - 42))
        for ball in self.balls:
            ball.draw(self.surf)
        if self.popup:
            self.popup.draw(self.surf, self.font_big, self.font_small)
        if self.fase_concluida:
            self.fase_concluida.draw(self.surf)
        txt = self.font_small.render(f"Acertos: {self.score}   Erros: {self.misses}", True, LEGO_WHITE)
        self.surf.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT - 42))
        self.btn_voltar.draw(self.surf)
