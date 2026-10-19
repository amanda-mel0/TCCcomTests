import pygame
import os
from ui_components import draw_lego_brick, draw_panel, LegoButton
from screens.fase_concluida import TOTAL_FASES


# Posições dos blocos no mapa (ajustadas à imagem 1100x700)
POSICOES_FASES = [
    (175, 210),   # Fase 1  - verde  canto superior esq
    (370, 255),   # Fase 2  - azul
    (545, 210),   # Fase 3  - laranja
    (800, 245),   # Fase 4  - amarelo
    (360, 420),   # Fase 5  - roxo
    (530, 430),   # Fase 6  - verde
    (800, 415),   # Fase 7  - azul
    (345, 590),   # Fase 8  - vermelho
    (525, 615),   # Fase 9  - amarelo
    (820, 595),   # Fase 10 - azul
]
CORES_FASES = [
    (34,  139,  34),   # 1  verde
    (37,   99, 235),   # 2  azul
    (234, 120,  10),   # 3  laranja
    (200, 170,   0),   # 4  amarelo
    (130,  50, 210),   # 5  roxo
    (34,  139,  34),   # 6  verde
    (37,   99, 235),   # 7  azul
    (210,  30,  30),   # 8  vermelho
    (200, 170,   0),   # 9  amarelo
    (37,   99, 235),   # 10 azul
]

TAMANHO_BLOCO = 105   # px largura e altura do bloco


def _posicoes_fases():
    posicoes = list(POSICOES_FASES[:TOTAL_FASES])

    if len(posicoes) >= TOTAL_FASES:
        return posicoes

    colunas = 5
    inicio_x = 165
    inicio_y = 160
    espaco_x = 190
    espaco_y = 150

    for i in range(len(posicoes), TOTAL_FASES):
        linha = i // colunas
        coluna = i % colunas
        posicoes.append((inicio_x + coluna * espaco_x, inicio_y + linha * espaco_y))

    return posicoes


class MapaScreen:
    def __init__(self, surf, largura, altura, cores, estado):
        self.surf = surf
        self.W = largura
        self.H = altura
        self.cores = cores
        self.estado = estado
        self.tick = 0
        self.hover_fase = -1   # índice do bloco sob o mouse (-1 = nenhum)

        # Fontes
        self.f_num    = pygame.font.SysFont("Impact", 54, bold= False)
        self.f_titulo = pygame.font.SysFont("Impact", 48, bold=True)
        self.f_info   = pygame.font.SysFont("Arial", 18, bold=True)
        self.f_tooltip= pygame.font.SysFont("Arial", 14)

        # Carregar imagem de fundo do mapa
        mapa_path = os.path.join(os.path.dirname(__file__), "..", "assets", "mapa.png")
        try:
            img = pygame.image.load(mapa_path).convert()
            self.bg = pygame.transform.scale(img, (largura, altura))
        except Exception:
            self.bg = None

        # Rects dos blocos
        self.rects_fases = []
        for cx, cy in _posicoes_fases():
            bw = TAMANHO_BLOCO
            bh = TAMANHO_BLOCO - 8
            self.rects_fases.append(
                pygame.Rect(cx - bw//2, cy - bh//2, bw, bh)
            )

        # Botão sair
        self.btn_sair = LegoButton(self.W - 130, 12, 110, 36,
                                   "SAIR", cores["vermelho"],
                                   pygame.font.SysFont("Impact", 16), studs=1)

    # ──────────────────────────────────────────────────────────────────────────
    def handle_events(self, eventos):
        for ev in eventos:
            if ev.type == pygame.MOUSEMOTION:
                self.hover_fase = -1
                for i, r in enumerate(self.rects_fases):
                    if r.collidepoint(ev.pos):
                        self.hover_fase = i
                        break

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, r in enumerate(self.rects_fases):
                    if r.collidepoint(ev.pos):
                        self.estado["fase_atual"] = i + 1
                        self.estado["tela_atual"] = f"fase_{i+1}"
                        break

            if self.btn_sair.handle_event(ev):
                self.estado["usuario"] = None
                self.estado["tela_atual"] = "login"

    # ──────────────────────────────────────────────────────────────────────────
    def update(self):
        self.tick += 1

    # ──────────────────────────────────────────────────────────────────────────
    def draw(self):
        # Fundo: imagem do mapa
        if self.bg:
            self.surf.blit(self.bg, (0, 0))
        else:
            self.surf.fill((56, 182, 100))

        # Overlay suave para destacar os blocos
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 30))
        self.surf.blit(overlay, (0, 0))

        # Blocos das fases
        for i, r in enumerate(self.rects_fases):
            cor = CORES_FASES[i % len(CORES_FASES)]
            self._draw_bloco_fase(i, r, cor)

        # HUD: saudação
        usuario = self.estado.get("usuario")
        if usuario:
            apelido = usuario.get("apelido", "Jogador")
            saud = self.f_info.render(f" Olá, {apelido}!", True, (255, 255, 255))
            # Sombra
            saud_sombra = self.f_info.render(f" Olá, {apelido}!", True, (0, 0, 0))
            self.surf.blit(saud_sombra, (12, 14))
            self.surf.blit(saud, (10, 12))

        # Tooltip da fase em hover
        if self.hover_fase >= 0:
            self._draw_tooltip(self.hover_fase)

        # Botão sair
        self.btn_sair.draw(self.surf)

    # ──────────────────────────────────────────────────────────────────────────
    def _draw_bloco_fase(self, idx, r, cor):
        hover = (idx == self.hover_fase)
        pulso = abs(pygame.math.Vector2(0, 1).rotate(self.tick * 3).y) * 4 if hover else 0

        rx = r.x
        ry = r.y - int(pulso)
        rw = r.w
        rh = r.h

        # Sombra
        pygame.draw.ellipse(self.surf, (0,0,0,80),
                            (rx+4, ry+rh-4, rw, 12))

        # Tijolo
        draw_lego_brick(self.surf, cor, (rx, ry, rw, rh), studs=2, raio_borda=10)

        # Número da fase
        num_txt = self.f_num.render(str(idx+1), True, (255, 255, 255))
        sombra  = self.f_num.render(str(idx+1), True, (0, 0, 0))
        cx = rx + rw//2
        cy = ry + rh//2 + 2
        self.surf.blit(sombra, sombra.get_rect(center=(cx+2, cy+2)))
        self.surf.blit(num_txt, num_txt.get_rect(center=(cx, cy)))

        # Borda brilhante no hover
        if hover:
            pygame.draw.rect(self.surf, (255, 255, 100), (rx-2, ry-2, rw+4, rh+4), 3, border_radius=12)

    def _draw_tooltip(self, idx):
        txt = self.f_tooltip.render(f"  Fase {idx+1}", True, (255, 255, 255))
        r = self.rects_fases[idx]
        tx = r.centerx - txt.get_width()//2 - 6
        ty = r.top - 30
        bg_r = pygame.Rect(tx, ty, txt.get_width()+12, 22)
        pygame.draw.rect(self.surf, (20,20,30,200), bg_r, border_radius=6)
        pygame.draw.rect(self.surf, (255,255,100), bg_r, 1, border_radius=6)
        self.surf.blit(txt, (tx+6, ty+3))
