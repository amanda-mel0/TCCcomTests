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

BLOCK_W = 70
BLOCK_H = 50
TORRE_X = WIDTH // 2
TORRE_BASE_Y = 560

CORES_BLOCO = [LEGO_RED, LEGO_YELLOW, LEGO_GREEN, LEGO_BLUE, LEGO_ORANGE, LEGO_PURPLE]


class Foguete:
    """Foguete que sobe conforme a criança acerta - barra de progresso lateral"""
    def __init__(self):
        self.progresso = 0.0  # 0 a 1
        self.alvo = 0.0
        self.wobble = 0

    def avanca(self, incremento):
        self.alvo = min(1.0, self.alvo + incremento)

    def update(self):
        self.progresso += (self.alvo - self.progresso) * 0.08
        self.wobble += 0.06

    def completo(self):
        return self.progresso >= 0.97

    def draw(self, surf):
        trilho_x = 60
        topo_y = 100
        base_y = 560

        # Trilho
        pygame.draw.rect(surf, (220, 220, 230), (trilho_x - 15, topo_y, 30, base_y - topo_y), border_radius=8)
        pygame.draw.rect(surf, LEGO_DARK, (trilho_x - 15, topo_y, 30, base_y - topo_y), 3, border_radius=8)
        for i in range(11):
            yy = topo_y + i * (base_y - topo_y) / 10
            pygame.draw.line(surf, LEGO_DARK, (trilho_x - 15, yy), (trilho_x + 15, yy), 2)

        # Bandeira topo
        pygame.draw.polygon(surf, LEGO_YELLOW, [
            (trilho_x, topo_y - 10),
            (trilho_x + 45, topo_y + 8),
            (trilho_x, topo_y + 26),
        ])
        pygame.draw.line(surf, LEGO_DARK, (trilho_x, topo_y - 10), (trilho_x, base_y + 10), 4)

        # Posição do foguete
        y = base_y - self.progresso * (base_y - topo_y)
        x = trilho_x + math.sin(self.wobble) * 6

        # Chamas
        flame_h = 24 + 6 * math.sin(self.wobble * 3)
        pygame.draw.polygon(surf, LEGO_ORANGE, [
            (x - 10, y + 25), (x + 10, y + 25), (x, y + 25 + flame_h)])
        pygame.draw.polygon(surf, LEGO_YELLOW, [
            (x - 5, y + 25), (x + 5, y + 25), (x, y + 25 + flame_h * 0.6)])

        # Corpo do foguete
        pygame.draw.rect(surf, LEGO_WHITE, (x - 15, y - 25, 30, 50), border_radius=10)
        pygame.draw.rect(surf, LEGO_DARK, (x - 15, y - 25, 30, 50), 2, border_radius=10)
        # Nariz
        pygame.draw.polygon(surf, LEGO_RED, [(x - 15, y - 25), (x + 15, y - 25), (x, y - 45)])
        # Janela
        pygame.draw.circle(surf, LEGO_BLUE, (int(x), int(y - 5)), 8)
        pygame.draw.circle(surf, LEGO_DARK, (int(x), int(y - 5)), 8, 2)
        # Aletas
        pygame.draw.polygon(surf, LEGO_RED, [(x - 15, y + 20), (x - 28, y + 35), (x - 15, y + 35)])
        pygame.draw.polygon(surf, LEGO_RED, [(x + 15, y + 20), (x + 28, y + 35), (x + 15, y + 35)])


class TorreBlocos:
    """Torre de blocos LEGO empilhados para contagem"""
    def __init__(self, quantidade):
        self.quantidade = quantidade
        self.aparecidos = 0  # quantos blocos já apareceram (animação)
        self.cores = [random.choice(CORES_BLOCO) for _ in range(quantidade)]
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer % 8 == 0 and self.aparecidos < self.quantidade:
            self.aparecidos += 1

    def draw(self, surf):
        for i in range(self.aparecidos):
            cor = self.cores[i]
            x = TORRE_X - BLOCK_W // 2
            y = TORRE_BASE_Y - (i + 1) * BLOCK_H

            # Sombra
            shadow = pygame.Surface((BLOCK_W + 8, 10), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 40), (0, 0, BLOCK_W + 8, 10))
            if i == 0:
                surf.blit(shadow, (x - 4, y + BLOCK_H - 4))

            # Bloco
            pygame.draw.rect(surf, cor, (x, y, BLOCK_W, BLOCK_H), border_radius=8)
            cor_borda = tuple(max(0, c - 50) for c in cor)
            pygame.draw.rect(surf, cor_borda, (x, y, BLOCK_W, BLOCK_H), 3, border_radius=8)

            # Studs LEGO
            for sx in [x + 18, x + BLOCK_W - 18]:
                pygame.draw.circle(surf, cor, (sx, y - 6), 9)
                pygame.draw.circle(surf, cor_borda, (sx, y - 6), 9, 2)


class Problema:
    """Problema de contagem - 4 a 6 anos"""

    def __init__(self):
        self.historico = []
        self.regenera()

    def regenera(self):
        for _ in range(5):
            quantidade = random.randint(2, 8)
            if quantidade not in self.historico[-4:]:
                break

        self.quantidade = quantidade
        self.historico.append(quantidade)
        if len(self.historico) > 8:
            self.historico.pop(0)

        # Gera 4 opções de resposta
        opcoes_set = {self.quantidade}
        while len(opcoes_set) < 4:
            delta = random.choice([-2, -1, 1, 2, 3])
            opcao = self.quantidade + delta
            if 1 <= opcao <= 12:
                opcoes_set.add(opcao)

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


class Fase6Screen:
    """Jogo Torre de Blocos - contagem de quantidades"""

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

        self.foguete = Foguete()
        self.problema = Problema()
        self.torre = TorreBlocos(self.problema.quantidade)
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

        for i, valor in enumerate(self.problema.opcoes):
            x = start_x + i * (botao_w + gap)
            y = 590
            cor = [LEGO_BLUE, LEGO_ORANGE, LEGO_PURPLE, LEGO_RED][i]
            self.botoes_resposta.append({
                "rect": pygame.Rect(x, y, botao_w, botao_h),
                "valor": valor,
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
                        if self.torre.aparecidos < self.torre.quantidade:
                            # Ainda animando - ignora clique
                            break

                        if botao["valor"] == self.problema.quantidade:
                            self.pontos += 10
                            self.acertos_consecutivos += 1
                            self.foguete.avanca(0.15 + 0.05 * min(self.acertos_consecutivos, 3))
                            self.popup = PopupRecompensa(acertou=True)
                        else:
                            self.acertos_consecutivos = 0
                            self.popup = PopupRecompensa(acertou=False)

                        self.regenerar_na_proxima = True
                        break


    def update(self):
        self.tick += 1
        self.foguete.update()
        self.torre.update()

        if self.popup:
            self.popup.update()
            if self.popup.finalizado() and self.regenerar_na_proxima:
                self.problema.regenera()
                self.torre = TorreBlocos(self.problema.quantidade)
                self._create_answer_buttons()
                self.regenerar_na_proxima = False
                self.popup = None

        self._verificar_conclusao()

    def _verificar_conclusao(self):
        """Abre o popup de fase concluída só depois que o personagem terminou
        a animação e o popup de acerto sumiu (antes ficava faltando um acerto)."""
        if self.popup is None and not self.fase_completa and self.foguete.completo():
            self.fase_completa = True
            self.fase_concluida = PopupFaseConcluida(self.W, self.H, self.estado)

    def draw(self):
        # Fundo céu / chão
        pygame.draw.rect(self.surf, SKY_COLOR, (0, 0, self.W, 600))
        pygame.draw.rect(self.surf, GRASS_COLOR, (0, 600, self.W, self.H - 600))

        # Nuvens decorativas
        for cx, cy in [(350, 90), (750, 70), (550, 160)]:
            for dx, dy, r in [(-30, 0, 22), (0, -10, 28), (30, 0, 22), (0, 8, 24)]:
                pygame.draw.circle(self.surf, LEGO_WHITE, (cx + dx, cy + dy), r)

        # Foguete (barra de progresso)
        self.foguete.draw(self.surf)

        # Plataforma da torre
        pygame.draw.ellipse(self.surf, (255, 255, 255, 100), (TORRE_X - 100, TORRE_BASE_Y - 5, 200, 30))
        for sx in range(TORRE_X - 90, TORRE_X + 91, 40):
            pygame.draw.circle(self.surf, LEGO_WHITE, (sx, TORRE_BASE_Y + 10), 6)

        # Torre de blocos
        self.torre.draw(self.surf)

        # Painel superior
        panel_h = 160
        pygame.draw.rect(self.surf, (40, 60, 100), (0, 0, self.W, panel_h))
        pygame.draw.rect(self.surf, LEGO_BLUE, (0, 0, self.W, panel_h), 5)

        # Pergunta
        quanto_txt = self.font_med.render("Quantos blocos tem a torre?", True, LEGO_WHITE)
        self.surf.blit(quanto_txt, (self.W // 2 - quanto_txt.get_width() // 2, 30))

        pergunta2_txt = self.font_small.render("Conte com cuidado!", True, LEGO_YELLOW)
        self.surf.blit(pergunta2_txt, (self.W // 2 - pergunta2_txt.get_width() // 2, 95))

        # Pontos
        pts_txt = self.font_small.render(f"Pontos: {self.pontos}", True, LEGO_WHITE)
        self.surf.blit(pts_txt, (20, 120))

        # Botões de resposta
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

            num_txt = self.font_big.render(str(botao["valor"]), True, LEGO_WHITE)
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
