import pygame
import math


# ─────────────────────────────────────────────────────────────────────────────
#  Utilitário de toque/clique unificado
# ─────────────────────────────────────────────────────────────────────────────

def _touch_or_click(ev, rect, largura_tela=None, altura_tela=None):
    """Retorna True se o evento é um clique esquerdo OU um toque finger
    que colide com 'rect'.

    FINGERDOWN usa coordenadas normalizadas (0.0–1.0); quando largura_tela
    e altura_tela são None, tenta usar pygame.display.get_surface() para
    obter o tamanho da janela automaticamente.
    """
    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
        return rect.collidepoint(ev.pos)
    if ev.type == pygame.FINGERDOWN:
        surf = pygame.display.get_surface()
        w = largura_tela or (surf.get_width()  if surf else 800)
        h = altura_tela  or (surf.get_height() if surf else 480)
        px = int(ev.x * w)
        py = int(ev.y * h)
        return rect.collidepoint(px, py)
    return False


# ─────────────────────────────────────────────────────────────────────────────
#  Utilitários de desenho LEGO
# ─────────────────────────────────────────────────────────────────────────────

def draw_lego_brick(surf, cor, rect, studs=2, raio_borda=8):
    x, y, w, h = rect
    r, g, b = cor
    # Sombra
    pygame.draw.rect(surf, (max(0,r-60), max(0,g-60), max(0,b-60)),
                     (x+4, y+4, w, h), border_radius=raio_borda)
    # Corpo
    pygame.draw.rect(surf, cor, (x, y, w, h), border_radius=raio_borda)
    # Brilho
    brilho = (min(255,r+60), min(255,g+60), min(255,b+60))
    pygame.draw.rect(surf, brilho, (x, y, w, 6), border_radius=raio_borda)
    pygame.draw.rect(surf, brilho, (x, y, 6, h), border_radius=raio_borda)
    # Borda escura
    pygame.draw.rect(surf, (max(0,r-80), max(0,g-80), max(0,b-80)),
                     (x, y, w, h), 2, border_radius=raio_borda)
    # Studs — só desenha se studs > 0
    if studs > 0:
        stud_r = min(w // (studs * 3), 10)
        stud_cor = (min(255,r+40), min(255,g+40), min(255,b+40))
        stud_sombra = (max(0,r-40), max(0,g-40), max(0,b-40))
        spacing = w // (studs + 1)
        for i in range(studs):
            cx = x + spacing * (i + 1)
            cy = y - stud_r + 2
            pygame.draw.circle(surf, stud_sombra, (cx+2, cy+2), stud_r)
            pygame.draw.circle(surf, stud_cor, (cx, cy), stud_r)
            pygame.draw.circle(surf, (max(0,r-80), max(0,g-80), max(0,b-80)), (cx, cy), stud_r, 1)


def draw_panel(surf, rect, cor_fundo=(30, 30, 40), alfa=220, raio=16):
    """Painel semi-transparente arredondado."""
    x, y, w, h = rect
    painel = pygame.Surface((w, h), pygame.SRCALPHA)
    r, g, b = cor_fundo
    pygame.draw.rect(painel, (r, g, b, alfa), (0, 0, w, h), border_radius=raio)
    pygame.draw.rect(painel, (255, 255, 255, 40), (0, 0, w, h), 2, border_radius=raio)
    surf.blit(painel, (x, y))


def draw_sky_background(surf, largura, altura, tick):
    """Céu azul animado com nuvens."""
    # Gradiente céu
    for i in range(altura):
        t = i / altura
        r = int(56 + (120 - 56) * t)
        g = int(182 + (210 - 182) * t)
        b = int(255 + (240 - 255) * t)
        pygame.draw.line(surf, (r, g, b), (0, i), (largura, i))
    # Nuvens simples
    _draw_clouds(surf, largura, tick)


def _draw_clouds(surf, largura, tick):
    posicoes = [(100, 80), (350, 50), (600, 90), (850, 60), (1050, 80)]
    offset = (tick // 3) % largura
    for bx, by in posicoes:
        cx = (bx - offset) % (largura + 200) - 100
        for dx, dy, r in [(0,0,28),(22,0,24),(-22,0,22),(10,-14,18),(-10,-14,16)]:
            pygame.draw.circle(surf, (255, 255, 255), (cx+dx, by+dy), r)


def draw_grass_strip(surf, largura, altura):
    """Faixa de grama no rodapé."""
    pygame.draw.rect(surf, (34, 139, 34), (0, altura-60, largura, 60))
    pygame.draw.rect(surf, (50, 180, 50), (0, altura-60, largura, 10))


# ─────────────────────────────────────────────────────────────────────────────
#  Componentes de UI
# ─────────────────────────────────────────────────────────────────────────────

class LegoButton:
    """Botão estilo tijolo LEGO clicável."""

    def __init__(self, x, y, w, h, texto, cor, fonte, studs=2):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto
        self.cor = cor
        self.fonte = fonte
        self.studs = studs
        self.hover = False
        self.pressionado = False
        self._tick = 0

    def handle_event(self, ev):
        clicou = False
        if ev.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(ev.pos)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.rect.collidepoint(ev.pos):
                self.pressionado = True
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            if self.pressionado and self.rect.collidepoint(ev.pos):
                clicou = True
            self.pressionado = False
        elif ev.type == pygame.FINGERDOWN:
            if _touch_or_click(ev, self.rect):
                self.pressionado = True
        elif ev.type == pygame.FINGERUP:
            if self.pressionado:
                clicou = True
            self.pressionado = False
        return clicou

    def draw(self, surf):
        self._tick += 1
        r, g, b = self.cor
        escala = 1.05 if self.hover and not self.pressionado else 1.0
        dy = 2 if self.pressionado else 0

        w = int(self.rect.w * escala)
        h = int(self.rect.h * escala)
        x = self.rect.centerx - w // 2
        y = self.rect.centery - h // 2 + dy

        draw_lego_brick(surf, self.cor, (x, y, w, h), studs=self.studs, raio_borda=10)

        txt = self.fonte.render(self.texto, True, (255, 255, 255))
        surf.blit(txt, txt.get_rect(center=(self.rect.centerx, self.rect.centery + dy + 2)))


class InputField:
    """Campo de texto estilo LEGO."""

    def __init__(self, x, y, w, h, placeholder="", senha=False, fonte=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.placeholder = placeholder
        self.senha = senha
        self.fonte = fonte or pygame.font.SysFont("Arial", 18)
        self.texto = ""
        self.ativo = False
        self.cursor_visivel = True
        self._cursor_tick = 0
        self.erro = False

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            self.ativo = self.rect.collidepoint(ev.pos)
        elif ev.type == pygame.FINGERDOWN:
            self.ativo = _touch_or_click(ev, self.rect)
        if ev.type == pygame.KEYDOWN and self.ativo:
            if ev.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            elif ev.key not in (pygame.K_RETURN, pygame.K_TAB):
                if len(self.texto) < 60:
                    self.texto += ev.unicode

    def draw(self, surf):
        self._cursor_tick += 1
        if self._cursor_tick % 60 < 30:
            self.cursor_visivel = True
        else:
            self.cursor_visivel = False

        # Fundo
        cor_borda = (220, 38, 38) if self.erro else ((37, 99, 235) if self.ativo else (100, 100, 120))
        pygame.draw.rect(surf, (20, 20, 30), self.rect, border_radius=8)
        pygame.draw.rect(surf, cor_borda, self.rect, 2, border_radius=8)


        # Texto ou placeholder
        exibir = self.texto if self.texto else self.placeholder
        cor_txt = (255,255,255) if self.texto else (120,120,140)
        mostrar = ("●" * len(self.texto)) if self.senha and self.texto else exibir
        txt_surf = self.fonte.render(mostrar, True, cor_txt)
        # Clip para não vazar
        area = pygame.Rect(self.rect.x+10, self.rect.y, self.rect.w-20, self.rect.h)
        surf.set_clip(area)
        surf.blit(txt_surf, (self.rect.x+10, self.rect.centery - txt_surf.get_height()//2))
        surf.set_clip(None)

        # Cursor
        if self.ativo and self.cursor_visivel and self.texto:
            cx = self.rect.x + 10 + txt_surf.get_width() + 2
            cy1 = self.rect.centery - 10
            cy2 = self.rect.centery + 10
            pygame.draw.line(surf, (255,255,255), (cx, cy1), (cx, cy2), 2)


class Checkbox:
    """Checkbox estilo LEGO."""

    def __init__(self, x, y, texto, fonte, cor_ativa=(34,197,94)):
        self.x = x
        self.y = y
        self.texto = texto
        self.fonte = fonte
        self.cor_ativa = cor_ativa
        self.marcado = False
        self.rect = pygame.Rect(x, y, 22, 22)

    def handle_event(self, ev):
        if _touch_or_click(ev, self.rect):
            self.marcado = not self.marcado

    def draw(self, surf):
        cor = self.cor_ativa if self.marcado else (60, 60, 75)
        pygame.draw.rect(surf, cor, self.rect, border_radius=4)
        pygame.draw.rect(surf, (200,200,220), self.rect, 2, border_radius=4)
        if self.marcado:
            # Check mark
            pts = [
                (self.x+4, self.y+11),
                (self.x+9, self.y+16),
                (self.x+18, self.y+5),
            ]
            pygame.draw.lines(surf, (255,255,255), False, pts, 3)
        txt = self.fonte.render(self.texto, True, (220,220,240))
        surf.blit(txt, (self.x+28, self.y+3))


class RadioGroup:
    """Grupo de opções de rádio (selecionar uma)."""

    def __init__(self, x, y, opcoes, fonte, cor_ativa=(37,99,235), espacamento=32):
        self.opcoes = opcoes
        self.fonte = fonte
        self.cor_ativa = cor_ativa
        self.selecionado = 0
        self.rects = []
        for i, _ in enumerate(opcoes):
            self.rects.append(pygame.Rect(x, y + i*espacamento, 20, 20))
        self.x = x
        self.y = y

    def handle_event(self, ev):
        for i, r in enumerate(self.rects):
            if _touch_or_click(ev, r):
                self.selecionado = i

    def draw(self, surf):
        for i, (r, opcao) in enumerate(zip(self.rects, self.opcoes)):
            ativo = (i == self.selecionado)
            cor = self.cor_ativa if ativo else (60,60,75)
            pygame.draw.circle(surf, cor, r.center, 10)
            pygame.draw.circle(surf, (200,200,220), r.center, 10, 2)
            if ativo:
                pygame.draw.circle(surf, (255,255,255), r.center, 5)
            txt = self.fonte.render(opcao, True, (220,220,240))
            surf.blit(txt, (r.right+8, r.centery - txt.get_height()//2))

    @property
    def valor(self):
        return self.opcoes[self.selecionado]


class AvatarSelector:
    """Seletor de avatares LEGO (círculos coloridos com letra/emoji)."""

    AVATARES = [
        {"label": "🧒", "cor": (220,38,38),   "nome": "Herói"},
        {"label": "👧", "cor": (236,72,153),  "nome": "Princesa"},
        {"label": "🧑", "cor": (37,99,235),   "nome": "Explorador"},
        {"label": "🦸", "cor": (34,197,94),   "nome": "Super"},
        {"label": "🧙", "cor": (147,51,234),  "nome": "Mago"},
        {"label": "🤖", "cor": (100,116,139), "nome": "Robô"},
    ]

    def __init__(self, cx, y, fonte_pequena):
        self.cx = cx
        self.y = y
        self.fonte = fonte_pequena
        self.selecionado = 0
        self.rects = []
        total = len(self.AVATARES)
        espacamento = 90
        inicio = cx - (total-1)*espacamento//2
        for i in range(total):
            self.rects.append(pygame.Rect(inicio + i*espacamento - 30, y, 60, 60))

    def handle_event(self, ev):
        for i, r in enumerate(self.rects):
            if _touch_or_click(ev, r):
                self.selecionado = i

    def draw(self, surf):
        for i, (r, av) in enumerate(zip(self.rects, self.AVATARES)):
            ativo = (i == self.selecionado)
            # Sombra
            pygame.draw.circle(surf, (0,0,0,100), (r.centerx+3, r.centery+3), 30)
            # Círculo
            pygame.draw.circle(surf, av["cor"], r.center, 30)
            if ativo:
                pygame.draw.circle(surf, (255,255,255), r.center, 30, 4)
            # Emoji
            emoji_surf = self.fonte.render(av["label"], True, (255,255,255))
            surf.blit(emoji_surf, emoji_surf.get_rect(center=r.center))
            # Nome abaixo
            nome_surf = self.fonte.render(av["nome"], True,
                                          (255,255,100) if ativo else (180,180,200))
            surf.blit(nome_surf, nome_surf.get_rect(centerx=r.centerx, top=r.bottom+4))

    @property
    def valor(self):
        return self.AVATARES[self.selecionado]["nome"]


class VirtualKeyboard:
    """Teclado virtual responsivo para uso em telas touch.

    O tamanho de cada tecla é calculado a partir do espaço disponível (w, h),
    usando a linha mais larga como referência — assim o teclado preenche
    exatamente a área passada em qualquer resolução.
    """

    # Duplas: teclas que ocupam 2 unidades de largura
    DOUBLE_KEYS = {"ESPACO", "APAGAR", "LIMPAR"}
    GAP = 6  # espaço entre teclas (px) — escala com a resolução via _build_keys

    def __init__(self, x, y, w, h, fonte=None):
        self.rows = [
            list("1234567890"),
            list("qwertyuiop"),
            list("asdfghjkl"),
            list("zxcvbnm.-_/"),
            ["@", "ESPACO", "APAGAR", "LIMPAR", "OK"],
        ]
        self.key_rects = []
        self.visible = False
        self.rect = pygame.Rect(x, y, w, h)
        self._fonte_override = fonte  # guarda para recriar se necessário
        self._build_keys()

    def _max_units(self):
        """Número de unidades de largura da linha mais larga."""
        return max(
            sum(2 if k in self.DOUBLE_KEYS else 1 for k in row)
            for row in self.rows
        )

    def _build_keys(self):
        self.key_rects = []
        n_rows = len(self.rows)
        gap = self.GAP

        # Uma unidade-base de largura, calculada pela linha mais larga
        max_u = self._max_units()
        unit_w = (self.rect.w - gap * (max_u + 1)) // max_u
        row_h  = (self.rect.h - gap * (n_rows + 1)) // n_rows

        # Fonte escala proporcionalmente ao tamanho da tecla
        font_size = max(12, int(row_h * 0.52))
        self.fonte = (
            self._fonte_override
            if self._fonte_override
            else pygame.font.SysFont("Arial", font_size, bold=True)
        )

        y = self.rect.y + gap
        for row in self.rows:
            # Centraliza linhas mais curtas dentro da largura total
            row_units = sum(2 if k in self.DOUBLE_KEYS else 1 for k in row)
            row_w = row_units * unit_w + gap * (row_units - 1)
            x = self.rect.x + (self.rect.w - row_w) // 2  # centraliza

            for key in row:
                units = 2 if key in self.DOUBLE_KEYS else 1
                kw = unit_w * units + gap * (units - 1)
                rect = pygame.Rect(x, y, kw, row_h)
                self.key_rects.append((key, rect))
                x += kw + gap

            y += row_h + gap

    def move_to(self, x, y):
        if self.rect.x == x and self.rect.y == y:
            return
        self.rect.x = x
        self.rect.y = y
        self._build_keys()

    def resize(self, w, h):
        """Redimensiona o teclado e reconstrói as teclas."""
        self.rect.w = w
        self.rect.h = h
        self._build_keys()

    def move_to(self, x, y):
        if self.rect.x == x and self.rect.y == y:
            return
        self.rect.x = x
        self.rect.y = y
        self._build_keys()

    def handle_event(self, ev, campo):
        if not self.visible or campo is None:
            return False

        # Normaliza posição para mouse ou finger
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            pos = ev.pos
        elif ev.type == pygame.FINGERDOWN:
            surf = pygame.display.get_surface()
            w = surf.get_width()  if surf else 800
            h = surf.get_height() if surf else 480
            pos = (int(ev.x * w), int(ev.y * h))
        else:
            return False

        if not self.rect.collidepoint(pos):
            return False

        for key, rect in self.key_rects:
            if not rect.collidepoint(pos):
                continue

            if key == "APAGAR":
                campo.texto = campo.texto[:-1]
            elif key == "LIMPAR":
                campo.texto = ""
            elif key == "OK":
                campo.ativo = False
                self.visible = False
            elif key == "ESPACO" and len(campo.texto) < 60:
                campo.texto += " "
            elif len(campo.texto) < 60:
                campo.texto += key
            return True

        return True

    def draw(self, surf):
        if not self.visible:
            return

        panel = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (15, 18, 28, 235), panel.get_rect(), border_radius=12)
        pygame.draw.rect(panel, (255, 255, 255, 45), panel.get_rect(), 2, border_radius=12)
        surf.blit(panel, self.rect.topleft)

        for key, rect in self.key_rects:
            if key == "OK":
                color = (34, 197, 94)
            elif key in ("APAGAR", "LIMPAR"):
                color = (220, 38, 38)
            elif key == "ESPACO":
                color = (75, 151, 74)
            else:
                color = (37, 99, 235)

            pygame.draw.rect(surf, color, rect, border_radius=7)
            pygame.draw.rect(surf, (15, 15, 25), rect, 2, border_radius=7)
            label = self.fonte.render(key, True, (255, 255, 255))
            surf.blit(label, label.get_rect(center=rect.center))