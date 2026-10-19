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

CORES_BLOCO = [LEGO_RED, LEGO_BLUE, LEGO_GREEN, LEGO_ORANGE, LEGO_PURPLE]

BLOCK_W = 150
BLOCK_H = 100
SLOT_Y = 280


class Foguinho:
    """Personagem mascote que sobe uma escada conforme a criança acerta"""
    def __init__(self):
        self.progresso = 0.0
        self.alvo = 0.0
        self.wobble = 0

    def avanca(self, incremento):
        self.alvo = min(1.0, self.alvo + incremento)

    def update(self):
        self.progresso += (self.alvo - self.progresso) * 0.08
        self.wobble += 0.08

    def completo(self):
        return self.progresso >= 0.97

    def draw(self, surf, w, h):
        base_x = 80
        topo_y = 120
        base_y = h - 140

        # Escada
        n_degraus = 6
        for i in range(n_degraus + 1):
            t = i / n_degraus
            y = base_y - t * (base_y - topo_y)
            x = base_x - t * 0  # escada vertical simples
            pygame.draw.rect(surf, (200, 160, 110), (x - 35, y, 70, 12), border_radius=4)
            pygame.draw.rect(surf, (150, 110, 70), (x - 35, y, 70, 12), 2, border_radius=4)

        pygame.draw.rect(surf, (150, 110, 70), (base_x - 38, topo_y - 10, 6, base_y - topo_y + 20))
        pygame.draw.rect(surf, (150, 110, 70), (base_x + 32, topo_y - 10, 6, base_y - topo_y + 20))

        # Bandeira topo
        pygame.draw.line(surf, LEGO_DARK, (base_x, topo_y - 10), (base_x, topo_y - 70), 4)
        pygame.draw.polygon(surf, LEGO_YELLOW, [
            (base_x, topo_y - 70), (base_x + 45, topo_y - 52), (base_x, topo_y - 34)])

        # Posição do personagem
        y = base_y - self.progresso * (base_y - topo_y)
        x = base_x + math.sin(self.wobble) * 4

        # Sombra
        pygame.draw.ellipse(surf, (0, 0, 0, 40), (x - 22, y + 18, 44, 12))

        # Corpo (figura LEGO simples)
        pygame.draw.rect(surf, LEGO_ORANGE, (x - 16, y - 25, 32, 35), border_radius=6)  # tronco
        pygame.draw.circle(surf, (255, 220, 180), (int(x), int(y - 38)), 16)  # cabeça
        # Chapéu
        pygame.draw.rect(surf, LEGO_BLUE, (x - 18, y - 52, 36, 10), border_radius=3)
        pygame.draw.circle(surf, LEGO_BLUE, (int(x), int(y - 56)), 6)
        # Olhos
        pygame.draw.circle(surf, LEGO_DARK, (int(x - 5), int(y - 38)), 2)
        pygame.draw.circle(surf, LEGO_DARK, (int(x + 5), int(y - 38)), 2)
        # Sorriso
        pygame.draw.arc(surf, LEGO_DARK, (x - 7, y - 38, 14, 12), math.pi * 0.1, math.pi * 0.9, 2)
        # Braços
        pygame.draw.line(surf, (255, 220, 180), (x - 16, y - 15), (x - 26, y), 5)
        pygame.draw.line(surf, (255, 220, 180), (x + 16, y - 15), (x + 26, y), 5)
        # Pernas
        pygame.draw.rect(surf, LEGO_DARK, (x - 12, y + 8, 10, 18), border_radius=2)
        pygame.draw.rect(surf, LEGO_DARK, (x + 2, y + 8, 10, 18), border_radius=2)


def desenhar_bloco_silaba(surf, x, y, texto, cor, font, w=BLOCK_W, h=BLOCK_H, hover=False, alpha=255):
    """Desenha um bloco LEGO retangular com uma sílaba escrita"""
    bloco_surf = pygame.Surface((w + 10, h + 24), pygame.SRCALPHA)

    cor_final = tuple(min(255, c + 35) for c in cor) if hover else cor
    cor_borda = tuple(max(0, c - 50) for c in cor_final)

    # Sombra
    pygame.draw.ellipse(bloco_surf, (0, 0, 0, 40), (5, h + 14, w, 12))

    # Corpo do bloco
    pygame.draw.rect(bloco_surf, cor_final, (5, 24, w, h), border_radius=12)
    pygame.draw.rect(bloco_surf, cor_borda, (5, 24, w, h), 4, border_radius=12)

    # Studs no topo
    stud_r = 13
    for sx in [5 + w // 4, 5 + w // 2, 5 + w * 3 // 4]:
        pygame.draw.circle(bloco_surf, cor_final, (sx, 24), stud_r)
        pygame.draw.circle(bloco_surf, cor_borda, (sx, 24), stud_r, 2)

    # Texto da sílaba
    txt = font.render(texto, True, LEGO_WHITE)
    bloco_surf.blit(txt, (
        5 + w // 2 - txt.get_width() // 2,
        24 + h // 2 - txt.get_height() // 2
    ))

    if alpha < 255:
        bloco_surf.set_alpha(alpha)

    surf.blit(bloco_surf, (x - w // 2 - 5, y - h // 2 - 24))


def desenhar_slot_vazio(surf, x, y, w=BLOCK_W, h=BLOCK_H, preenchido_texto=None, cor=None, font=None):
    """Desenha um espaço (slot) onde a sílaba deve ser encaixada"""
    if preenchido_texto is not None and cor is not None:
        desenhar_bloco_silaba(surf, x, y, preenchido_texto, cor, font, w, h)
        return

    # Slot vazio - contorno pontilhado
    rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
    slot_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(slot_surf, (255, 255, 255, 60), (0, 0, w, h), border_radius=12)
    surf.blit(slot_surf, rect.topleft)

    # Borda pontilhada simples (vários segmentos)
    n_dash = 14
    perim_pts = []
    for i in range(n_dash):
        t = i / n_dash
        if t < 0.25:
            px = rect.left + (t / 0.25) * rect.width
            py = rect.top
        elif t < 0.5:
            px = rect.right
            py = rect.top + ((t - 0.25) / 0.25) * rect.height
        elif t < 0.75:
            px = rect.right - ((t - 0.5) / 0.25) * rect.width
            py = rect.bottom
        else:
            px = rect.left
            py = rect.bottom - ((t - 0.75) / 0.25) * rect.height
        perim_pts.append((px, py))

    for i in range(0, len(perim_pts) - 1, 2):
        pygame.draw.line(surf, LEGO_WHITE, perim_pts[i], perim_pts[i + 1], 4)


class Problema:
    """Problema de montar palavra com sílabas - 4 a 6 anos"""

    PALAVRAS = [
        ("BOLA", ["BO", "LA"]),
        ("GATO", ["GA", "TO"]),
        ("CASA", ["CA", "SA"]),
        ("PATO", ["PA", "TO"]),
        ("DEDO", ["DE", "DO"]),
        ("VACA", ["VA", "CA"]),
        ("SAPO", ["SA", "PO"]),
        ("FADA", ["FA", "DA"]),
        ("MALA", ["MA", "LA"]),
        ("LUA", ["LU", "A"]),
    ]

    def __init__(self):
        self.historico = []
        self.regenera()

    def regenera(self):
        for _ in range(5):
            palavra, silabas = random.choice(self.PALAVRAS)
            if palavra not in self.historico[-5:]:
                break

        self.palavra = palavra
        self.silabas_corretas = silabas
        self.historico.append(palavra)
        if len(self.historico) > 8:
            self.historico.pop(0)

        n_lacunas = len(silabas)

        # Sorteia qual posição ficará com lacuna (1 lacuna por vez para 4-6 anos)
        self.indice_lacuna = random.randint(0, n_lacunas - 1)

        # Sílaba correta que falta
        self.silaba_correta = silabas[self.indice_lacuna]

        # Gera opções de sílabas (1 correta + 3 distratoras de outras palavras).
        # Uma distratora NÃO pode completar outra palavra válida na mesma lacuna
        # (ex.: PATO com lacuna no início não pode oferecer "GA", pois GATO existe).
        outras = [sil for pal, sil in self.PALAVRAS
                  if pal != palavra and len(sil) == len(silabas)]
        completam_palavra = {
            sil[self.indice_lacuna] for sil in outras
            if all(sil[i] == silabas[i] for i in range(len(silabas)) if i != self.indice_lacuna)
        }

        todas_silabas = set()
        for _, sset in self.PALAVRAS:
            for s in sset:
                todas_silabas.add(s)
        todas_silabas.discard(self.silaba_correta)
        todas_silabas -= completam_palavra

        candidatas = sorted(todas_silabas)
        random.shuffle(candidatas)

        opcoes_set = {self.silaba_correta}
        for s in candidatas:
            if len(opcoes_set) >= 4:
                break
            opcoes_set.add(s)

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


class Fase10Screen:
    """Jogo Sílabas em Construção - montar palavras com sílabas"""

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
        self.font_silaba = pygame.font.SysFont("Arial Rounded MT Bold", 48, bold=True)

        self.foguinho = Foguinho()
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

        for i, silaba in enumerate(self.problema.opcoes):
            x = start_x + i * (botao_w + gap)
            y = 500
            cor = [LEGO_BLUE, LEGO_ORANGE, LEGO_PURPLE, LEGO_RED][i]
            self.botoes_resposta.append({
                "rect": pygame.Rect(x, y, botao_w, botao_h),
                "silaba": silaba,
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
                        if botao["silaba"] == self.problema.silaba_correta:
                            self.pontos += 10
                            self.acertos_consecutivos += 1
                            self.foguinho.avanca(0.15 + 0.05 * min(self.acertos_consecutivos, 3))
                            self.popup = PopupRecompensa(acertou=True)
                        else:
                            self.acertos_consecutivos = 0
                            self.popup = PopupRecompensa(acertou=False)

                        self.regenerar_na_proxima = True
                        break


    def update(self):
        self.tick += 1
        self.foguinho.update()

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
        if self.popup is None and not self.fase_completa and self.foguinho.completo():
            self.fase_completa = True
            self.fase_concluida = PopupFaseConcluida(self.W, self.H, self.estado)

    def draw(self):
        # Fundo céu / chão
        pygame.draw.rect(self.surf, SKY_COLOR, (0, 0, self.W, self.H - 100))
        pygame.draw.rect(self.surf, GRASS_COLOR, (0, self.H - 100, self.W, 100))

        # Nuvens decorativas
        for cx, cy in [(400, 80), (800, 60), (600, 150)]:
            for dx, dy, r in [(-30, 0, 22), (0, -10, 28), (30, 0, 22), (0, 8, 24)]:
                pygame.draw.circle(self.surf, LEGO_WHITE, (cx + dx, cy + dy), r)

        # Escada com personagem
        self.foguinho.draw(self.surf, self.W, self.H)

        # Painel superior
        panel_h = 160
        pygame.draw.rect(self.surf, (40, 60, 100), (0, 0, self.W, panel_h))
        pygame.draw.rect(self.surf, LEGO_BLUE, (0, 0, self.W, panel_h), 5)

        # Pergunta
        quanto_txt = self.font_med.render("Qual sílaba está faltando?", True, LEGO_WHITE)
        self.surf.blit(quanto_txt, (self.W // 2 - quanto_txt.get_width() // 2, 30))

        pergunta2_txt = self.font_small.render("Complete a palavra!", True, LEGO_YELLOW)
        self.surf.blit(pergunta2_txt, (self.W // 2 - pergunta2_txt.get_width() // 2, 95))

        # Pontos
        pts_txt = self.font_small.render(f"Pontos: {self.pontos}", True, LEGO_WHITE)
        self.surf.blit(pts_txt, (20, 120))

        # Palavra com blocos/slots de sílabas
        n_silabas = len(self.problema.silabas_corretas)
        gap = 25
        total_w = n_silabas * BLOCK_W + (n_silabas - 1) * gap
        start_x = (self.W - total_w) // 2 + BLOCK_W // 2

        # Plataforma sob os blocos
        plat_y = SLOT_Y + BLOCK_H // 2 + 10
        pygame.draw.rect(self.surf, (220, 220, 230), (start_x - BLOCK_W // 2 - 10, plat_y, total_w + 20, 14), border_radius=6)

        for i, silaba in enumerate(self.problema.silabas_corretas):
            x = start_x + i * (BLOCK_W + gap)

            if i == self.problema.indice_lacuna:
                # Slot vazio
                desenhar_slot_vazio(self.surf, x, SLOT_Y, BLOCK_W, BLOCK_H)
            else:
                # Bloco com sílaba já preenchida
                cor = CORES_BLOCO[i % len(CORES_BLOCO)]
                desenhar_bloco_silaba(self.surf, x, SLOT_Y, silaba, cor, self.font_silaba)

        # Botões de resposta (sílabas)
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

            num_txt = self.font_big.render(botao["silaba"], True, LEGO_WHITE)
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
