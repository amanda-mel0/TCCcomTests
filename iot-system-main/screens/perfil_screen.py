import pygame
import os
from ui_components import draw_lego_brick, draw_panel, draw_sky_background, draw_grass_strip, LegoButton


class PerfilScreen:
    """
    Tela de Perfil do Jogador — inspirada no design do colega (telas/perfil.py).
    Exibe avatar, nome, nível, barras de progresso por matéria e estrelas.
    Aparece logo após o login; botão "Iniciar" leva ao mapa de fases.
    """

    def __init__(self, surf, largura, altura, cores, estado):
        self.surf = surf
        self.W = largura
        self.H = altura
        self.cores = cores
        self.estado = estado
        self.tick = 0

        # Fontes
        self.f_titulo = pygame.font.SysFont("Segoe UI", 36, bold=True)
        self.f_nome    = pygame.font.SysFont("Arial",     26, bold=True)
        self.f_nivel   = pygame.font.SysFont("Arial",     18, bold=True)
        self.f_label   = pygame.font.SysFont("Segoe UI",  17, bold=True)
        self.f_barra   = pygame.font.SysFont("Arial",     14, bold=True)
        self.f_estrela = pygame.font.SysFont("Segoe UI",  28)
        self.f_id      = pygame.font.SysFont("Arial",     14)
        self.f_btn     = pygame.font.SysFont("Impact",    22)

        # Carregar imagens dos avatares
        base = os.path.dirname(__file__)
        avatares_dir = os.path.join(base, "..", "assets", "avatares")
        try:
            img_masc = pygame.image.load(
                os.path.join(avatares_dir, "robo_masculino.png")
            ).convert_alpha()
            self.avatar_masculino = pygame.transform.smoothscale(img_masc, (180, 180))
        except Exception:
            self.avatar_masculino = None

        try:
            img_fem = pygame.image.load(
                os.path.join(avatares_dir, "robo_feminino.png")
            ).convert_alpha()
            self.avatar_feminino = pygame.transform.smoothscale(img_fem, (180, 180))
        except Exception:
            self.avatar_feminino = None

        # Botão Iniciar
        bw, bh = 260, 52
        self.btn_iniciar = LegoButton(
            self.W // 2 - bw // 2,
            self.H - 75,
            bw, bh,
            "INICIAR",
            cores["verde"],
            self.f_btn,
            studs=0
        )

    # ─────────────────────────────────────────────────────────────────────────
    def handle_events(self, eventos):
        for ev in eventos:
            if self.btn_iniciar.handle_event(ev):
                self.estado["tela_atual"] = "mapa"

    def update(self):
        self.tick += 1

    # ─────────────────────────────────────────────────────────────────────────
    def draw(self):
        draw_sky_background(self.surf, self.W, self.H, self.tick)
        draw_grass_strip(self.surf, self.W, self.H)

        usuario = self.estado.get("usuario") or {}
        apelido  = usuario.get("apelido", "Jogador")
        uid      = usuario.get("uid", "—")
        avatar   = usuario.get("avatar", "masculino")   # campo salvo no login

        # ── Cabeçalho LEGO ────────────────────────────────────────────────────

        header_w = 420
        header_h = 60

        header_x = self.W // 2 - header_w // 2
        header_y = 15

        # sombra
        pygame.draw.rect(
            self.surf,
            (70, 70, 70),
            (header_x + 4, header_y + 4, header_w, header_h),
            border_radius=14
        )

        # corpo
        pygame.draw.rect(
            self.surf,
            (255, 205, 0),
            (header_x, header_y, header_w, header_h),
            border_radius=14
        )

        # borda
        pygame.draw.rect(
            self.surf,
            (40, 40, 40),
            (header_x, header_y, header_w, header_h),
            3,
            border_radius=14
        )

        # pinos LEGO teste teste teste
        for i in range(8):
            stud_x = header_x + 35 + i * 50

            pygame.draw.circle(
                self.surf,
                (235, 185, 0),
                (stud_x, header_y + 10),
                7
            )

            pygame.draw.circle(
                self.surf,
                (255, 225, 50),
                (stud_x, header_y + 7),
                7
            )

        # texto
        titulo = self.f_titulo.render(
            "PERFIL",
            True,
            (40, 40, 40)
        )

        self.surf.blit(
            titulo,
            titulo.get_rect(
                center=(
                    header_x + header_w // 2,
                    header_y + header_h // 2 + 4
                )
            )
        )

        # ── Card principal ────────────────────────────────────────────────────
        card_w, card_h = 780, 430
        card_x = self.W // 2 - card_w // 2
        card_y = 95
        self._draw_card(card_x, card_y, card_w, card_h)

        # ── Coluna esquerda: avatar ───────────────────────────────────────────
        col_esq_x = card_x + 40
        self._draw_avatar_card(col_esq_x, card_y + 30, apelido, avatar)

        # ── Coluna direita: painel info ───────────────────────────────────────
        col_dir_x = card_x + 320
        self._draw_painel_info(col_dir_x, card_y + 30, uid)

        # ── Botão Iniciar ─────────────────────────────────────────────────────
        self.btn_iniciar.draw(self.surf)

    # ─────────────────────────────────────────────────────────────────────────
    def _draw_card(self, x, y, w, h):
        """Card principal translúcido (rosa claro — igual ao #cardPrincipal do colega)."""
        surf_card = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf_card, (255, 210, 235, 220), (0, 0, w, h), border_radius=28)
        pygame.draw.rect(surf_card, (255, 255, 255, 100), (0, 0, w, h), 3, border_radius=28)
        self.surf.blit(surf_card, (x, y))

        # Sombra embaixo do card
        sombra = pygame.Surface((w, 16), pygame.SRCALPHA)
        for i in range(16):
            alpha = int(70 * (1 - i / 16))
            pygame.draw.rect(sombra, (0, 0, 0, alpha), (i, i, w - i * 2, 4), border_radius=4)
        self.surf.blit(sombra, (x, y + h))

    # ─────────────────────────────────────────────────────────────────────────
    def _draw_avatar_card(self, x, y, nome, avatar):
        """Card branco com avatar, nome e nível — igual ao #avatarCard do colega."""
        cw, ch = 240, 340

        surf_ac = pygame.Surface((cw, ch), pygame.SRCALPHA)
        pygame.draw.rect(surf_ac, (255, 255, 255, 210), (0, 0, cw, ch), border_radius=22)
        pygame.draw.rect(surf_ac, (255, 255, 255, 140), (0, 0, cw, ch), 2, border_radius=22)
        self.surf.blit(surf_ac, (x, y))

        # Imagem do avatar
        img = self.avatar_masculino if avatar == "masculino" else self.avatar_feminino
        if img:
            img_rect = img.get_rect(centerx=x + cw // 2, top=y + 18)
            self.surf.blit(img, img_rect)
            img_bottom = img_rect.bottom + 10
        else:
            emoji_surf = self.f_nivel.render( True, (80, 80, 80))
            self.surf.blit(emoji_surf, emoji_surf.get_rect(centerx=x + cw // 2, top=y + 30))
            img_bottom = y + 210

        # Placa com nome e nível (amarela — #placaAvatar)
        placa_h = 68
        placa_y = img_bottom
        placa_surf = pygame.Surface((cw - 20, placa_h), pygame.SRCALPHA)
        pygame.draw.rect(placa_surf, (255, 190, 40, 230), (0, 0, cw - 20, placa_h), border_radius=16)
        pygame.draw.rect(placa_surf, (255, 255, 255, 140), (0, 0, cw - 20, placa_h), 2, border_radius=16)
        self.surf.blit(placa_surf, (x + 10, placa_y))

        nome_txt    = self.f_nome.render(nome, True, (43, 29, 29))
        nivel_txt   = self.f_nivel.render("Nível 7", True, (43, 29, 29))
        cx_placa    = x + cw // 2
        self.surf.blit(nome_txt,  nome_txt.get_rect(centerx=cx_placa, top=placa_y + 6))
        self.surf.blit(nivel_txt, nivel_txt.get_rect(centerx=cx_placa, top=placa_y + 38))

    # ─────────────────────────────────────────────────────────────────────────
    def _draw_painel_info(self, x, y, uid):
        """Painel com ID, barras de progresso e estrelas — igual ao #painelInfo do colega."""
        pw, ph = 390, 340

        surf_p = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(surf_p, (255, 255, 255, 210), (0, 0, pw, ph), border_radius=26)
        pygame.draw.rect(surf_p, (255, 255, 255, 150), (0, 0, pw, ph), 3, border_radius=26)
        self.surf.blit(surf_p, (x, y))

        pad_x = x + 22
        cy    = y + 20

        # ID
        id_txt = self.f_id.render(f"ID: {uid[:20] if uid else '—'}", True, (90, 90, 110))
        self.surf.blit(id_txt, (pad_x, cy))
        cy += 32

        # Barras de progresso das matérias
        materias = [
            ("Matemática", 80, (37, 99, 235)),
            ("Português",  60, (220, 38, 38)),
            ("Lógica",     90, (147, 51, 234)),
        ]
        bar_w = 320
        bar_h = 22

        for (label, valor, cor_barra) in materias:
            lbl_surf = self.f_label.render(label, True, (53, 33, 58))
            self.surf.blit(lbl_surf, (pad_x, cy))
            cy += 26

            # Trilho da barra
            trilho = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
            pygame.draw.rect(trilho, (255, 255, 255, 180), (0, 0, bar_w, bar_h), border_radius=11)
            pygame.draw.rect(trilho, (255, 255, 255, 120), (0, 0, bar_w, bar_h), 2, border_radius=11)
            self.surf.blit(trilho, (pad_x, cy))

            # Chunk colorido
            chunk_w = int(bar_w * valor / 100)
            if chunk_w > 0:
                chunk = pygame.Surface((chunk_w, bar_h), pygame.SRCALPHA)
                r, g, b = cor_barra
                pygame.draw.rect(chunk, (r, g, b, 230), (0, 0, chunk_w, bar_h), border_radius=10)
                self.surf.blit(chunk, (pad_x, cy))

            # Percentual
            pct_txt = self.f_barra.render(f"{valor}%", True, (53, 33, 58))
            self.surf.blit(pct_txt, (pad_x + bar_w + 8, cy + 4))

            cy += bar_h + 16

        # Estrelas
        cy += 6
        estrelas_completas = 3
        total_estrelas = 5
        estrelas_str = "" * estrelas_completas + "" * (total_estrelas - estrelas_completas)
        est_surf = self.f_estrela.render(estrelas_str, True, (255, 200, 20))
        self.surf.blit(est_surf, est_surf.get_rect(centerx=x + pw // 2, top=cy))
