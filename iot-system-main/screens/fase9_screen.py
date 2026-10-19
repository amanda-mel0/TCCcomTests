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

CORES_BLOCO = {
    "vermelho": LEGO_RED,
    "azul":     LEGO_BLUE,
    "verde":    LEGO_GREEN,
    "amarelo":  LEGO_YELLOW,
    "laranja":  LEGO_ORANGE,
    "roxo":     LEGO_PURPLE,
}

BLOCK_SIZE = 90
SEQ_Y = 320


class Trem:
    """Trenzinho LEGO que avança nos trilhos conforme a criança acerta"""
    def __init__(self):
        self.progresso = 0.0
        self.alvo = 0.0
        self.wobble = 0

    def avanca(self, incremento):
        self.alvo = min(1.0, self.alvo + incremento)

    def update(self):
        self.progresso += (self.alvo - self.progresso) * 0.08
        self.wobble += 0.1

    def completo(self):
        return self.progresso >= 0.97

    def draw(self, surf, w, h):
        trilho_y = h - 70
        margem = 60

        # Trilhos
        pygame.draw.rect(surf, (160, 130, 90), (margem, trilho_y, w - 2 * margem, 18), border_radius=4)
        for tx in range(margem, w - margem, 30):
            pygame.draw.rect(surf, (110, 85, 55), (tx, trilho_y - 4, 6, 26))
        pygame.draw.line(surf, (90, 90, 100), (margem, trilho_y + 2), (w - margem, trilho_y + 2), 3)
        pygame.draw.line(surf, (90, 90, 100), (margem, trilho_y + 14), (w - margem, trilho_y + 14), 3)

        # Bandeira final
        fx = w - margem
        pygame.draw.line(surf, LEGO_DARK, (fx, trilho_y - 70), (fx, trilho_y), 4)
        pygame.draw.polygon(surf, LEGO_YELLOW, [
            (fx, trilho_y - 70), (fx + 45, trilho_y - 52), (fx, trilho_y - 34)])

        # Posição do trem
        x = margem + 40 + self.progresso * (w - 2 * margem - 140)
        y = trilho_y - 8 + math.sin(self.wobble) * 1.5

        # Fumaça
        for i in range(3):
            sx = x - 35 - i * 12
            sy = y - 50 - i * 14 + math.sin(self.wobble + i) * 4
            raio = 10 + i * 4
            pygame.draw.circle(surf, (220, 220, 220), (int(sx), int(sy)), raio)

        # Corpo
        pygame.draw.rect(surf, LEGO_RED, (x - 10, y - 40, 80, 40), border_radius=8)
        pygame.draw.rect(surf, (140, 25, 15), (x - 10, y - 40, 80, 40), 3, border_radius=8)
        # Cabine
        pygame.draw.rect(surf, LEGO_YELLOW, (x - 30, y - 55, 35, 35), border_radius=6)
        pygame.draw.rect(surf, (180, 140, 20), (x - 30, y - 55, 35, 35), 2, border_radius=6)
        # Chaminé
        pygame.draw.rect(surf, LEGO_DARK, (x + 35, y - 65, 14, 25), border_radius=3)
        # Studs
        for sx in [x + 10, x + 40]:
            pygame.draw.circle(surf, LEGO_RED, (int(sx), int(y - 46)), 8)
            pygame.draw.circle(surf, (140, 25, 15), (int(sx), int(y - 46)), 8, 2)
        # Rodas
        for rx in [x - 2, x + 30, x + 60]:
            pygame.draw.circle(surf, LEGO_DARK, (int(rx), int(y + 5)), 9)
            pygame.draw.circle(surf, LEGO_BLUE, (int(rx), int(y + 5)), 6)


def desenhar_bloco(surf, x, y, cor, tamanho=BLOCK_SIZE, alpha=255, mostrar_interrogacao=False, font=None):
    """Desenha um bloco LEGO quadrado com studs no topo"""
    bloco_surf = pygame.Surface((tamanho + 10, tamanho + 24), pygame.SRCALPHA)

    if mostrar_interrogacao:
        cor_bloco = (220, 220, 230)
        cor_borda = (170, 170, 185)
    else:
        cor_bloco = cor
        cor_borda = tuple(max(0, c - 50) for c in cor)

    # Sombra
    pygame.draw.ellipse(bloco_surf, (0, 0, 0, 40), (5, tamanho + 14, tamanho, 12))

    # Corpo do bloco
    pygame.draw.rect(bloco_surf, cor_bloco, (5, 24, tamanho, tamanho), border_radius=10)
    pygame.draw.rect(bloco_surf, cor_borda, (5, 24, tamanho, tamanho), 4, border_radius=10)

    # Studs no topo
    stud_r = 12
    for sx in [5 + tamanho // 4, 5 + tamanho * 3 // 4]:
        pygame.draw.circle(bloco_surf, cor_bloco, (sx, 24), stud_r)
        pygame.draw.circle(bloco_surf, cor_borda, (sx, 24), stud_r, 2)

    if mostrar_interrogacao and font:
        txt = font.render("?", True, (140, 140, 160))
        bloco_surf.blit(txt, (
            5 + tamanho // 2 - txt.get_width() // 2,
            24 + tamanho // 2 - txt.get_height() // 2
        ))

    if alpha < 255:
        bloco_surf.set_alpha(alpha)

    surf.blit(bloco_surf, (x - tamanho // 2 - 5, y - tamanho // 2 - 24))


class Problema:
    """Problema de sequência lógica - 4 a 6 anos"""

    # Padrões pré-definidos (nomes das cores)
    PADROES = [
        # AB AB AB -> próximo é A
        lambda: _padrao_abab(),
        # AAB AAB -> próximo completa o padrão
        lambda: _padrao_aab(),
        # ABC ABC -> próximo é A
        lambda: _padrao_abc(),
        # Crescente em tamanho (sempre mesma cor, mas posições alternam 2 cores)
        lambda: _padrao_abba(),
    ]

    def __init__(self):
        self.historico = []
        self.regenera()

    def regenera(self):
        for _ in range(5):
            sequencia, resposta = random.choice(self.PADROES)()
            assinatura = tuple(sequencia) + (resposta,)
            if assinatura not in self.historico[-4:]:
                break

        self.sequencia = sequencia  # lista de nomes de cores (5 itens visíveis + 1 "?")
        self.resposta = resposta    # nome da cor correta
        self.historico.append(assinatura)
        if len(self.historico) > 8:
            self.historico.pop(0)

        # Gera 4 opções (cores)
        todas_cores = list(CORES_BLOCO.keys())
        opcoes_set = {self.resposta}
        candidatas = [c for c in todas_cores if c != self.resposta]
        random.shuffle(candidatas)
        for c in candidatas:
            if len(opcoes_set) >= 4:
                break
            opcoes_set.add(c)

        self.opcoes = list(opcoes_set)
        random.shuffle(self.opcoes)


def _cores_aleatorias_distintas(n):
    cores = list(CORES_BLOCO.keys())
    random.shuffle(cores)
    return cores[:n]


def _padrao_abab():
    a, b = _cores_aleatorias_distintas(2)
    seq = [a, b, a, b, a]
    resposta = b
    return seq, resposta


def _padrao_aab():
    a, b = _cores_aleatorias_distintas(2)
    seq = [a, a, b, a, a]
    resposta = b
    return seq, resposta


def _padrao_abc():
    a, b, c = _cores_aleatorias_distintas(3)
    seq = [a, b, c, a, b]
    resposta = c
    return seq, resposta


def _padrao_abba():
    a, b = _cores_aleatorias_distintas(2)
    seq = [a, b, b, a, b]
    resposta = b
    return seq, resposta


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


class Fase9Screen:
    """Jogo Sequência LEGO - completar padrões lógicos"""

    def __init__(self, surf, largura, altura, cores, estado, *args, **kwargs):
        self.surf = surf
        self.W = largura
        self.H = altura
        self.cores = cores
        self.estado = estado
        self.tick = 0
        self.fase_concluida = None

        self.font_huge = pygame.font.SysFont("Arial Rounded MT Bold", 96, bold=True)
        self.font_big = pygame.font.SysFont("Arial Rounded MT Bold", 56, bold=True)
        self.font_med = pygame.font.SysFont("Arial Rounded MT Bold", 40, bold=True)
        self.font_small = pygame.font.SysFont("Arial Rounded MT Bold", 24, bold=True)
        self.font_question = pygame.font.SysFont("Arial Rounded MT Bold", 40, bold=True)

        self.trem = Trem()
        self.problema = Problema()
        self.pontos = 0
        self.acertos_consecutivos = 0
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

        for i, nome_cor in enumerate(self.problema.opcoes):
            x = start_x + i * (botao_w + gap)
            y = 480
            self.botoes_resposta.append({
                "rect": pygame.Rect(x, y, botao_w, botao_h),
                "cor_nome": nome_cor,
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
                        if botao["cor_nome"] == self.problema.resposta:
                            self.pontos += 10
                            self.acertos_consecutivos += 1
                            self.trem.avanca(0.15 + 0.05 * min(self.acertos_consecutivos, 3))
                            self.popup = PopupRecompensa(acertou=True)
                        else:
                            self.acertos_consecutivos = 0
                            self.popup = PopupRecompensa(acertou=False)

                        self.regenerar_na_proxima = True
                        break


    def update(self):
        self.tick += 1
        self.trem.update()

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
        if self.popup is None and not self.fase_completa and self.trem.completo():
            self.fase_completa = True
            self.fase_concluida = PopupFaseConcluida(self.W, self.H, self.estado)

    def draw(self):
        # Fundo céu / chão
        pygame.draw.rect(self.surf, SKY_COLOR, (0, 0, self.W, self.H - 130))
        pygame.draw.rect(self.surf, GRASS_COLOR, (0, self.H - 130, self.W, 130))

        # Nuvens decorativas
        for cx, cy in [(300, 80), (700, 60), (500, 150)]:
            for dx, dy, r in [(-30, 0, 22), (0, -10, 28), (30, 0, 22), (0, 8, 24)]:
                pygame.draw.circle(self.surf, LEGO_WHITE, (cx + dx, cy + dy), r)

        # Trem na base
        self.trem.draw(self.surf, self.W, self.H)

        # Painel superior
        panel_h = 160
        pygame.draw.rect(self.surf, (40, 60, 100), (0, 0, self.W, panel_h))
        pygame.draw.rect(self.surf, LEGO_BLUE, (0, 0, self.W, panel_h), 5)

        # Pergunta
        quanto_txt = self.font_med.render("Qual bloco vem depois?", True, LEGO_WHITE)
        self.surf.blit(quanto_txt, (self.W // 2 - quanto_txt.get_width() // 2, 30))

        pergunta2_txt = self.font_small.render("Observe o padrão!", True, LEGO_YELLOW)
        self.surf.blit(pergunta2_txt, (self.W // 2 - pergunta2_txt.get_width() // 2, 95))

        # Pontos
        pts_txt = self.font_small.render(f"Pontos: {self.pontos}", True, LEGO_WHITE)
        self.surf.blit(pts_txt, (20, 120))

        # Sequência de blocos + interrogação
        total_itens = len(self.problema.sequencia) + 1
        gap = 30
        total_w = total_itens * BLOCK_SIZE + (total_itens - 1) * gap
        start_x = (self.W - total_w) // 2 + BLOCK_SIZE // 2

        # Plataforma sob os blocos
        plat_y = SEQ_Y + BLOCK_SIZE // 2 + 10
        pygame.draw.rect(self.surf, (220, 220, 230), (start_x - BLOCK_SIZE // 2 - 10, plat_y, total_w + 20, 14), border_radius=6)

        for i, nome_cor in enumerate(self.problema.sequencia):
            x = start_x + i * (BLOCK_SIZE + gap)
            desenhar_bloco(self.surf, x, SEQ_Y, CORES_BLOCO[nome_cor])

        # Bloco "?"
        x_pergunta = start_x + len(self.problema.sequencia) * (BLOCK_SIZE + gap)
        desenhar_bloco(self.surf, x_pergunta, SEQ_Y, None, mostrar_interrogacao=True, font=self.font_question)

        # Botões de resposta
        for botao in self.botoes_resposta:
            cor_base = CORES_BLOCO[botao["cor_nome"]]
            cor = cor_base if not botao["hover"] else tuple(min(255, c + 40) for c in cor_base)
            cor_borda = tuple(max(0, c - 50) for c in cor)

            shadow = pygame.Surface((botao["rect"].width + 6, botao["rect"].height + 6), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 60), (3, 3, botao["rect"].width, botao["rect"].height), border_radius=10)
            self.surf.blit(shadow, (botao["rect"].x - 2, botao["rect"].y + 2))

            pygame.draw.rect(self.surf, cor, botao["rect"], border_radius=10)
            pygame.draw.rect(self.surf, cor_borda, botao["rect"], 3, border_radius=10)

            pygame.draw.circle(self.surf, cor_borda, (botao["rect"].centerx - 20, botao["rect"].y + 10), 6)
            pygame.draw.circle(self.surf, cor_borda, (botao["rect"].centerx + 20, botao["rect"].y + 10), 6)

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

            vitoria_txt = self.font_big.render(" VOCÊ VENCEU! ", True, LEGO_WHITE)
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
