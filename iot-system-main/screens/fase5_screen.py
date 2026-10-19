import pygame
import random
import math
from ui_components import LegoButton, draw_lego_brick
from screens.audio_manager import play_error, play_success
from screens.fase_concluida import (
    PopupFaseConcluida,
    avancar_para_proxima_fase,
    get_phase_completion_text,
)

WIDTH, HEIGHT = 1100, 700

# ── Cores LEGO ──────────────────────────────────────────────────────────
LEGO_RED      = (196, 40,  27)
LEGO_YELLOW   = (245, 205,  47)
LEGO_GREEN    = ( 75, 151,  74)
LEGO_BLUE     = ( 13, 105, 171)
LEGO_ORANGE   = (254, 138,  24)
LEGO_PURPLE   = (147, 51, 234)
LEGO_WHITE    = (255, 255, 255)
LEGO_DARK     = ( 30,  30,  50)
SKY_COLOR     = ( 56, 182, 255)
GRASS_COLOR   = (100, 180,  60)

# ── Constantes do jogo ──────────────────────────────────────────────────
TRILHA_X = 150
TRILHA_TOPO = 100
TRILHA_BASE = 560
BALAO_X = 950


class Balao:
    """Balão que sobe na trilha conforme a criança acerta"""
    def __init__(self):
        self.altura_relativa = 0.0  # 0 = base, 1 = topo
        self.altura_alvo = 0.0
        self.y = TRILHA_BASE
        self.wobble = 0

    def sobe(self, incremento):
        self.altura_alvo = min(1.0, self.altura_alvo + incremento)

    def update(self):
        self.altura_relativa += (self.altura_alvo - self.altura_relativa) * 0.08
        self.y = TRILHA_BASE - self.altura_relativa * (TRILHA_BASE - TRILHA_TOPO)
        self.wobble += 0.06

    def chegou(self):
        return self.altura_relativa >= 0.97

    def draw(self, surf):
        x = int(BALAO_X + math.sin(self.wobble) * 6)
        y = int(self.y)

        # Barbante
        pygame.draw.line(surf, LEGO_DARK, (x, y + 38), (x, y + 80), 2)

        # Cesto LEGO
        pygame.draw.rect(surf, LEGO_ORANGE, (x - 18, y + 38, 36, 26), border_radius=4)
        pygame.draw.rect(surf, (180, 100, 15), (x - 18, y + 38, 36, 26), 2, border_radius=4)
        pygame.draw.circle(surf, (180, 100, 15), (x - 10, y + 42), 4)
        pygame.draw.circle(surf, (180, 100, 15), (x + 10, y + 42), 4)

        # Sombra do balão
        shadow = pygame.Surface((90, 90), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 30), (5, 5, 80, 80))
        surf.blit(shadow, (x - 40, y - 35))

        # Balão (corpo arredondado)
        pygame.draw.ellipse(surf, LEGO_RED, (x - 40, y - 40, 80, 80))
        pygame.draw.ellipse(surf, (140, 25, 15), (x - 40, y - 40, 80, 80), 3)
        # Brilho
        pygame.draw.ellipse(surf, (255, 255, 255, 120), (x - 25, y - 28, 25, 22))
        # Stud LEGO no topo
        pygame.draw.circle(surf, LEGO_YELLOW, (x, y - 40), 8)
        pygame.draw.circle(surf, (200, 150, 20), (x, y - 40), 8, 2)
        # Bico embaixo
        pygame.draw.polygon(surf, LEGO_RED, [(x - 8, y + 35), (x + 8, y + 35), (x, y + 48)])


class Letra:
    """Desenho simples para representar a palavra (sem usar imagens externas)"""

    @staticmethod
    def desenhar(surf, nome, cx, cy, escala=1.0):
        """Desenha um ícone simples representando a palavra dada"""
        s = escala
        if nome == "gato":
            # Corpo
            pygame.draw.ellipse(surf, (200, 170, 120), (cx - 40*s, cy - 10*s, 80*s, 50*s))
            # Cabeça
            pygame.draw.circle(surf, (200, 170, 120), (int(cx + 35*s), int(cy - 15*s)), int(22*s))
            # Orelhas
            pygame.draw.polygon(surf, (200, 170, 120), [
                (cx + 18*s, cy - 30*s), (cx + 28*s, cy - 45*s), (cx + 35*s, cy - 25*s)])
            pygame.draw.polygon(surf, (200, 170, 120), [
                (cx + 45*s, cy - 30*s), (cx + 55*s, cy - 45*s), (cx + 50*s, cy - 22*s)])
            # Olhos
            pygame.draw.circle(surf, LEGO_DARK, (int(cx + 28*s), int(cy - 18*s)), int(3*s))
            pygame.draw.circle(surf, LEGO_DARK, (int(cx + 42*s), int(cy - 18*s)), int(3*s))
            # Rabo
            pygame.draw.arc(surf, (200, 170, 120), (cx - 60*s, cy - 30*s, 50*s, 50*s), 0.5, 3.0, int(8*s))

        elif nome == "bola":
            pygame.draw.circle(surf, LEGO_BLUE, (int(cx), int(cy)), int(45*s))
            pygame.draw.circle(surf, LEGO_DARK, (int(cx), int(cy)), int(45*s), 3)
            for ang in range(0, 360, 60):
                rad = math.radians(ang)
                x2 = cx + 45*s * math.cos(rad)
                y2 = cy + 45*s * math.sin(rad)
                pygame.draw.line(surf, LEGO_WHITE, (cx, cy), (x2, y2), int(3*s))

        elif nome == "casa":
            pygame.draw.rect(surf, (230, 220, 200), (cx - 45*s, cy - 5*s, 90*s, 55*s))
            pygame.draw.polygon(surf, LEGO_RED, [
                (cx - 55*s, cy - 5*s), (cx, cy - 50*s), (cx + 55*s, cy - 5*s)])
            pygame.draw.rect(surf, LEGO_BLUE, (cx - 12*s, cy + 15*s, 24*s, 35*s))
            pygame.draw.circle(surf, LEGO_YELLOW, (int(cx + 6*s), int(cy + 32*s)), int(3*s))

        elif nome == "sol":
            pygame.draw.circle(surf, LEGO_YELLOW, (int(cx), int(cy)), int(35*s))
            for ang in range(0, 360, 30):
                rad = math.radians(ang)
                x1 = cx + 40*s * math.cos(rad)
                y1 = cy + 40*s * math.sin(rad)
                x2 = cx + 55*s * math.cos(rad)
                y2 = cy + 55*s * math.sin(rad)
                pygame.draw.line(surf, LEGO_ORANGE, (x1, y1), (x2, y2), int(6*s))

        elif nome == "pato":
            pygame.draw.ellipse(surf, LEGO_YELLOW, (cx - 35*s, cy - 10*s, 70*s, 45*s))
            pygame.draw.circle(surf, LEGO_YELLOW, (int(cx + 25*s), int(cy - 20*s)), int(20*s))
            pygame.draw.polygon(surf, LEGO_ORANGE, [
                (cx + 40*s, cy - 20*s), (cx + 62*s, cy - 16*s), (cx + 40*s, cy - 12*s)])
            pygame.draw.circle(surf, LEGO_DARK, (int(cx + 28*s), int(cy - 24*s)), int(3*s))

        elif nome == "mesa":
            pygame.draw.rect(surf, (170, 120, 80), (cx - 50*s, cy - 10*s, 100*s, 12*s))
            pygame.draw.rect(surf, (140, 95, 60), (cx - 42*s, cy + 2*s, 8*s, 35*s))
            pygame.draw.rect(surf, (140, 95, 60), (cx + 34*s, cy + 2*s, 8*s, 35*s))

        elif nome == "fada":
            pygame.draw.circle(surf, (255, 220, 200), (int(cx), int(cy - 25*s)), int(15*s))
            pygame.draw.polygon(surf, LEGO_PURPLE, [
                (cx - 15*s, cy - 5*s), (cx + 15*s, cy - 5*s), (cx, cy + 35*s)])
            # Asas
            pygame.draw.ellipse(surf, (220, 240, 255), (cx - 45*s, cy - 25*s, 35*s, 25*s))
            pygame.draw.ellipse(surf, (220, 240, 255), (cx + 10*s, cy - 25*s, 35*s, 25*s))
            # Estrela na varinha
            pygame.draw.circle(surf, LEGO_YELLOW, (int(cx + 28*s), int(cy - 35*s)), int(6*s))

        elif nome == "vaca":
            pygame.draw.ellipse(surf, LEGO_WHITE, (cx - 45*s, cy - 10*s, 90*s, 50*s))
            pygame.draw.ellipse(surf, LEGO_DARK, (cx - 30*s, cy - 5*s, 25*s, 20*s))
            pygame.draw.ellipse(surf, LEGO_DARK, (cx + 5*s, cy + 10*s, 22*s, 18*s))
            pygame.draw.circle(surf, LEGO_WHITE, (int(cx + 40*s), int(cy - 18*s)), int(18*s))
            pygame.draw.polygon(surf, LEGO_WHITE, [
                (cx + 30*s, cy - 35*s), (cx + 38*s, cy - 48*s), (cx + 42*s, cy - 32*s)])
            pygame.draw.polygon(surf, LEGO_WHITE, [
                (cx + 48*s, cy - 35*s), (cx + 56*s, cy - 48*s), (cx + 54*s, cy - 32*s)])
            pygame.draw.circle(surf, LEGO_DARK, (int(cx + 35*s), int(cy - 20*s)), int(3*s))
            pygame.draw.circle(surf, LEGO_DARK, (int(cx + 48*s), int(cy - 20*s)), int(3*s))

        elif nome == "navio":
            pygame.draw.polygon(surf, (170, 110, 60), [
                (cx - 50*s, cy + 10*s), (cx + 50*s, cy + 10*s), (cx + 35*s, cy + 35*s), (cx - 35*s, cy + 35*s)])
            pygame.draw.line(surf, LEGO_DARK, (cx, cy + 10*s), (cx, cy - 50*s), int(4*s))
            pygame.draw.polygon(surf, LEGO_RED, [
                (cx, cy - 50*s), (cx, cy - 10*s), (cx + 35*s, cy - 10*s)])

        elif nome == "jacaré" or nome == "jacare":
            pygame.draw.ellipse(surf, LEGO_GREEN, (cx - 55*s, cy - 5*s, 110*s, 35*s))
            pygame.draw.polygon(surf, LEGO_GREEN, [
                (cx + 50*s, cy - 5*s), (cx + 80*s, cy + 5*s), (cx + 50*s, cy + 20*s)])
            for i in range(4):
                pygame.draw.polygon(surf, (50, 110, 50), [
                    (cx - 30*s + i*20*s, cy - 5*s),
                    (cx - 20*s + i*20*s, cy - 18*s),
                    (cx - 10*s + i*20*s, cy - 5*s)])
            pygame.draw.circle(surf, LEGO_WHITE, (int(cx - 45*s), int(cy - 2*s)), int(4*s))
            pygame.draw.circle(surf, LEGO_DARK, (int(cx - 45*s), int(cy - 2*s)), int(2*s))

        else:
            # Fallback: desenha um bloco LEGO genérico com a primeira letra
            pygame.draw.rect(surf, LEGO_BLUE, (cx - 40*s, cy - 30*s, 80*s, 60*s), border_radius=8)
            pygame.draw.circle(surf, LEGO_BLUE, (int(cx - 15*s), int(cy - 38*s)), int(8*s))
            pygame.draw.circle(surf, LEGO_BLUE, (int(cx + 15*s), int(cy - 38*s)), int(8*s))


class Problema:
    """Problema de identificação de letra inicial - 4 a 6 anos"""

    # Banco de palavras com sua letra inicial e desenho associado
    PALAVRAS = [
        ("GATO", "G", "gato"),
        ("BOLA", "B", "bola"),
        ("CASA", "C", "casa"),
        ("SOL", "S", "sol"),
        ("PATO", "P", "pato"),
        ("MESA", "M", "mesa"),
        ("FADA", "F", "fada"),
        ("VACA", "V", "vaca"),
        ("NAVIO", "N", "navio"),
        ("JACARÉ", "J", "jacare"),
    ]

    LETRAS_EXTRA = list("ABCDEFGIJLMNOPQRSTUVZ")

    def __init__(self):
        self.historico = []
        self.regenera()

    def regenera(self):
        for _ in range(5):
            palavra, letra, desenho = random.choice(self.PALAVRAS)
            if f"{palavra}" not in self.historico[-5:]:
                break

        self.palavra = palavra
        self.letra_correta = letra
        self.desenho = desenho
        self.historico.append(palavra)
        if len(self.historico) > 8:
            self.historico.pop(0)

        # Gera 4 opções de letras
        opcoes_set = {self.letra_correta}
        candidatas = [l for l in self.LETRAS_EXTRA if l != self.letra_correta]
        random.shuffle(candidatas)
        for l in candidatas:
            if len(opcoes_set) >= 4:
                break
            opcoes_set.add(l)

        self.opcoes = list(opcoes_set)
        random.shuffle(self.opcoes)


class PopupRecompensa:
    """Popup de acerto animado"""
    def __init__(self, acertou=True):
        play_success() if acertou else play_error()
        self.acertou = acertou
        self.timer = 0
        self.duracao = 80
        self.scale = 0.2
        self.particles = []

        if acertou:
            for _ in range(30):
                self.particles.append({
                    "x": WIDTH // 2 + random.randint(-100, 100),
                    "y": HEIGHT // 2 + random.randint(-100, 100),
                    "vx": random.uniform(-2, 2),
                    "vy": random.uniform(-3, -0.5),
                    "cor": random.choice([LEGO_RED, LEGO_YELLOW, LEGO_GREEN, LEGO_BLUE, LEGO_ORANGE]),
                    "tamanho": random.randint(8, 16),
                })

    def update(self):
        self.timer += 1
        p = self.timer / self.duracao

        if p < 0.25:
            self.scale = 0.2 + 0.8 * (p / 0.25)
        elif p > 0.75:
            self.scale = max(0, 1.0 - (p - 0.75) / 0.25)
        else:
            self.scale = 1.0

        for particle in self.particles:
            particle["y"] += particle["vy"]
            particle["vy"] += 0.15

    def finalizado(self):
        return self.timer >= self.duracao

    def draw(self, surf, font_big):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 40))
        surf.blit(overlay, (0, 0))

        for p in self.particles:
            if 0 <= p["y"] <= HEIGHT:
                pygame.draw.circle(surf, p["cor"], (int(p["x"]), int(p["y"])), p["tamanho"] // 2)

        box_w, box_h = 400, 150
        scale = max(0.1, self.scale)
        bw, bh = int(box_w * scale), int(box_h * scale)
        bx, by = WIDTH // 2 - bw // 2, HEIGHT // 2 - bh // 2 - 80

        cor_fundo = LEGO_GREEN if self.acertou else LEGO_RED
        cor_borda = (50, 140, 50) if self.acertou else (150, 20, 15)

        pygame.draw.rect(surf, cor_fundo, (bx, by, bw, bh), border_radius=16)
        pygame.draw.rect(surf, cor_borda, (bx, by, bw, bh), 4, border_radius=16)

        for sx in range(bx + 30, bx + bw - 20, 60):
            pygame.draw.circle(surf, cor_borda, (sx, by + 12), 8)
            pygame.draw.circle(surf, cor_fundo, (sx, by + 12), 8, 2)

        msg = "MUITO BEM!" if self.acertou else "TENTE NOVAMENTE"
        txt = font_big.render(msg, True, LEGO_WHITE)
        txt_scale = pygame.transform.smoothscale(txt, (int(txt.get_width() * scale), int(txt.get_height() * scale)))
        surf.blit(txt_scale, (bx + bw // 2 - txt_scale.get_width() // 2, by + bh // 2 - txt_scale.get_height() // 2))


class Fase5Screen:
    """Jogo Balão das Letras - identificar a letra inicial das palavras"""

    def __init__(self, surf, largura, altura, cores, estado, *args, **kwargs):
        self.surf = surf
        self.W = largura
        self.H = altura
        self.cores = cores
        self.estado = estado
        self.tick = 0

        self.font_huge = pygame.font.SysFont("Arial Rounded MT Bold", 96, bold=True)
        self.font_big = pygame.font.SysFont("Arial Rounded MT Bold", 56, bold=True)
        self.font_med = pygame.font.SysFont("Arial Rounded MT Bold", 40, bold=True)
        self.font_small = pygame.font.SysFont("Arial Rounded MT Bold", 24, bold=True)

        self.balao = Balao()
        self.problema = Problema()
        self.pontos = 0
        self.acertos_consecutivos = 0
        self.fase_concluida = None
        self.popup = None
        self.fase_completa = False
        self.regenerar_na_proxima = False

        self.btn_voltar = LegoButton(
            40, self.H - 70, 200, 46,
            "VOLTAR AO MAPA", self.cores["cinza_med"], self.font_small, studs=0
        )

        self.botoes_resposta = []
        self._create_answer_buttons()

    def _create_answer_buttons(self):
        self.botoes_resposta = []
        botao_w = 130
        botao_h = 110
        gap = 25
        total_w = 4 * botao_w + 3 * gap
        start_x = (self.W - total_w) // 2

        for i, letra in enumerate(self.problema.opcoes):
            x = start_x + i * (botao_w + gap)
            y = 460
            cor = [LEGO_BLUE, LEGO_ORANGE, LEGO_PURPLE, LEGO_RED][i]
            self.botoes_resposta.append({
                "rect": pygame.Rect(x, y, botao_w, botao_h),
                "letra": letra,
                "cor": cor,
                "hover": False,
            })

    def handle_events(self, eventos):
        for ev in eventos:
            if self.fase_concluida:
                if self.fase_concluida.handle_event(ev):
                    avancar_para_proxima_fase(self.estado)
                continue

            if self.btn_voltar.handle_event(ev):
                self.estado["tela_atual"] = "mapa"
                return

            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.estado["tela_atual"] = "mapa"
                return

            if ev.type == pygame.MOUSEMOTION:
                mx, my = ev.pos
                for botao in self.botoes_resposta:
                    botao["hover"] = botao["rect"].collidepoint(mx, my)

            if ev.type == pygame.MOUSEBUTTONDOWN and self.popup is None and not self.fase_completa:
                mx, my = ev.pos
                for botao in self.botoes_resposta:
                    if botao["rect"].collidepoint(mx, my):
                        if botao["letra"] == self.problema.letra_correta:
                            self.pontos += 10
                            self.acertos_consecutivos += 1
                            self.balao.sobe(0.15 + 0.05 * min(self.acertos_consecutivos, 3))
                            self.popup = PopupRecompensa(acertou=True)
                        else:
                            self.acertos_consecutivos = 0
                            self.popup = PopupRecompensa(acertou=False)

                        self.regenerar_na_proxima = True
                        break

    def update(self):
        self.tick += 1
        self.balao.update()

        if self.popup:
            self.popup.update()
            if self.popup.finalizado() and self.regenerar_na_proxima:
                self.problema.regenera()
                self._create_answer_buttons()
                self.regenerar_na_proxima = False
                self.popup = None

        self._verificar_conclusao()

    def _verificar_conclusao(self):
        """Abre o popup de fase concluída só depois que o personagem terminou
        a animação e o popup de acerto sumiu (antes ficava faltando um acerto)."""
        if self.popup is None and not self.fase_completa and self.balao.chegou():
            self.fase_completa = True
            self.fase_concluida = PopupFaseConcluida(self.W, self.H, self.estado)

    def draw(self):
        # Fundo céu / chão
        pygame.draw.rect(self.surf, SKY_COLOR, (0, 0, self.W, 600))
        pygame.draw.rect(self.surf, GRASS_COLOR, (0, 600, self.W, self.H - 600))

        # Nuvens decorativas
        for cx, cy in [(300, 80), (700, 60), (500, 150)]:
            for dx, dy, r in [(-30, 0, 22), (0, -10, 28), (30, 0, 22), (0, 8, 24)]:
                pygame.draw.circle(self.surf, LEGO_WHITE, (cx + dx, cy + dy), r)

        # Trilha vertical (régua de altura)
        pygame.draw.rect(self.surf, (220, 220, 230), (TRILHA_X - 15, TRILHA_TOPO, 30, TRILHA_BASE - TRILHA_TOPO), border_radius=8)
        pygame.draw.rect(self.surf, LEGO_DARK, (TRILHA_X - 15, TRILHA_TOPO, 30, TRILHA_BASE - TRILHA_TOPO), 3, border_radius=8)
        for i in range(11):
            yy = TRILHA_TOPO + i * (TRILHA_BASE - TRILHA_TOPO) / 10
            pygame.draw.line(self.surf, LEGO_DARK, (TRILHA_X - 15, yy), (TRILHA_X + 15, yy), 2)

        # Bandeira no topo da trilha
        pygame.draw.polygon(self.surf, LEGO_YELLOW, [
            (TRILHA_X, TRILHA_TOPO - 10),
            (TRILHA_X + 45, TRILHA_TOPO + 8),
            (TRILHA_X, TRILHA_TOPO + 26),
        ])
        pygame.draw.line(self.surf, LEGO_DARK, (TRILHA_X, TRILHA_TOPO - 10), (TRILHA_X, TRILHA_BASE + 10), 4)

        # Balão
        self.balao.draw(self.surf)

        # Painel superior
        panel_h = 160
        pygame.draw.rect(self.surf, (40, 60, 100), (0, 0, self.W, panel_h))
        pygame.draw.rect(self.surf, LEGO_BLUE, (0, 0, self.W, panel_h), 5)

        # "Qual a letra inicial?"
        quanto_txt = self.font_med.render("Qual é a primeira letra?", True, LEGO_WHITE)
        self.surf.blit(quanto_txt, (self.W // 2 - quanto_txt.get_width() // 2, 14))

        # Nome da palavra grande
        prob_txt = self.font_huge.render(self.problema.palavra, True, LEGO_YELLOW)
        self.surf.blit(prob_txt, (self.W // 2 - prob_txt.get_width() // 2, 65))

        # Pontos
        pts_txt = self.font_small.render(f"Pontos: {self.pontos}", True, LEGO_WHITE)
        self.surf.blit(pts_txt, (20, 120))

        # Desenho ilustrativo da palavra
        plataforma_x = self.W // 2
        plataforma_y = 320
        pygame.draw.ellipse(self.surf, (255, 255, 255, 100), (plataforma_x - 90, plataforma_y + 50, 180, 30))
        for sx in range(plataforma_x - 80, plataforma_x + 81, 40):
            pygame.draw.circle(self.surf, LEGO_WHITE, (sx, plataforma_y + 65), 6)
        Letra.desenhar(self.surf, self.problema.desenho, plataforma_x, plataforma_y, escala=1.3)

        # Botões de resposta (letras)
        for botao in self.botoes_resposta:
            cor = botao["cor"] if not botao["hover"] else tuple(min(255, c + 40) for c in botao["cor"])
            cor_borda = tuple(max(0, c - 50) for c in cor)

            shadow = pygame.Surface((botao["rect"].width + 6, botao["rect"].height + 6), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 60), (3, 3, botao["rect"].width, botao["rect"].height), border_radius=10)
            self.surf.blit(shadow, (botao["rect"].x - 2, botao["rect"].y + 2))

            pygame.draw.rect(self.surf, cor, botao["rect"], border_radius=10)
            pygame.draw.rect(self.surf, cor_borda, botao["rect"], 3, border_radius=10)

            pygame.draw.circle(self.surf, cor_borda, (botao["rect"].centerx - 20, botao["rect"].y + 10), 6)
            pygame.draw.circle(self.surf, cor_borda, (botao["rect"].centerx + 20, botao["rect"].y + 10), 6)

            num_txt = self.font_big.render(botao["letra"], True, LEGO_WHITE)
            self.surf.blit(num_txt, (botao["rect"].centerx - num_txt.get_width() // 2,
                                     botao["rect"].centery - num_txt.get_height() // 2))

        if self.popup:
            self.popup.draw(self.surf, self.font_big)

        if self.fase_completa and not self.fase_concluida:
            overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.surf.blit(overlay, (0, 0))

            box_w, box_h = 500, 250
            bx, by = self.W // 2 - box_w // 2, self.H // 2 - box_h // 2 - 50

            pygame.draw.rect(self.surf, LEGO_GREEN, (bx, by, box_w, box_h), border_radius=20)
            pygame.draw.rect(self.surf, (50, 140, 50), (bx, by, box_w, box_h), 5, border_radius=20)

            for sx in range(bx + 40, bx + box_w - 20, 80):
                pygame.draw.circle(self.surf, (50, 140, 50), (sx, by + 20), 10)

            vitoria_txt = self.font_big.render("VOCÊ VENCEU!", True, LEGO_WHITE)
            self.surf.blit(vitoria_txt, (bx + box_w // 2 - vitoria_txt.get_width() // 2, by + 40))

            pontos_txt = self.font_med.render(f"Pontos: {self.pontos}", True, LEGO_YELLOW)
            self.surf.blit(pontos_txt, (bx + box_w // 2 - pontos_txt.get_width() // 2, by + 120))
            _, subtitle, button_text = get_phase_completion_text(self.estado)
            subtitle_txt = self.font_small.render(subtitle, True, LEGO_WHITE)
            self.surf.blit(subtitle_txt, (bx + box_w // 2 - subtitle_txt.get_width() // 2, by + 160))
            t4 = self.font_small.render(button_text, True, LEGO_WHITE)
            self.surf.blit(t4, (bx + box_w // 2 - t4.get_width() // 2, by + 200))

        self.btn_voltar.draw(self.surf)

        if self.fase_concluida:
            self.fase_concluida.draw(self.surf)

        esc_txt = self.font_small.render("ESC = voltar ao mapa", True, (100, 120, 150))
        self.surf.blit(esc_txt, (self.W - esc_txt.get_width() - 16, self.H - 28))
