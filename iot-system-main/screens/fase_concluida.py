import pygame
from screens.audio_manager import play_phase_complete


TOTAL_FASES = 10


def get_fase_atual(estado):
    return int(estado.get("fase_atual", 1) or 1)


def avancar_para_proxima_fase(estado, total_fases=TOTAL_FASES):
    fase_atual = get_fase_atual(estado)

    if fase_atual < total_fases:
        proxima = fase_atual + 1
        estado["fase_atual"] = proxima
        estado["tela_atual"] = f"fase_{proxima}"
    else:
        estado["fase_atual"] = total_fases
        estado["tela_atual"] = "jogo_concluido"


def get_phase_completion_text(estado, total_fases=TOTAL_FASES):
    fase_atual = get_fase_atual(estado)

    if fase_atual < total_fases:
        return "FASE CONCLUÍDA!", "Próxima fase desbloqueada!", "PRÓXIMA FASE"

    return "FASE CONCLUÍDA!", "Todas as fases foram concluídas!", "VER FINAL"


class PopupFaseConcluida:

    def __init__(self, largura, altura, estado=None):
        self.W = largura
        self.H = altura
        self.estado = estado or {}
        play_phase_complete()

        self.font_titulo = pygame.font.SysFont("Impact", 42)
        self.font_texto = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_botao = pygame.font.SysFont("Arial", 26, bold=True)

        self.titulo, self.subtitulo, self.texto_botao = get_phase_completion_text(self.estado)

        self.btn_rect = pygame.Rect(
            self.W // 2 - 140,
            self.H // 2 + 95,
            280,
            65
        )

    def draw_stud(self, tela, x, y, cor):
        pygame.draw.circle(tela, cor, (x, y), 12)
        pygame.draw.circle(tela, (255, 255, 255), (x - 3, y - 3), 4)

    def draw(self, tela):
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        tela.blit(overlay, (0, 0))

        popup_w = 650
        popup_h = 380

        popup_x = self.W // 2 - popup_w // 2
        popup_y = self.H // 2 - popup_h // 2

        pygame.draw.rect(
            tela,
            (70, 70, 70),
            (popup_x + 8, popup_y + 8, popup_w, popup_h),
            border_radius=25
        )

        pygame.draw.rect(
            tela,
            (255, 205, 0),
            (popup_x, popup_y, popup_w, popup_h),
            border_radius=25
        )

        pygame.draw.rect(
            tela,
            (30, 30, 30),
            (popup_x, popup_y, popup_w, popup_h),
            5,
            border_radius=25
        )

        for i in range(10):
            self.draw_stud(
                tela,
                popup_x + 45 + i * 62,
                popup_y + 15,
                (255, 230, 60)
            )

        trofeu = self.font_titulo.render("*", True, (255, 255, 255))
        tela.blit(
            trofeu,
            trofeu.get_rect(center=(self.W // 2, popup_y + 70))
        )

        titulo = self.font_titulo.render(self.titulo, True, (220, 38, 38))
        tela.blit(
            titulo,
            titulo.get_rect(center=(self.W // 2, popup_y + 130))
        )

        texto1 = self.font_texto.render("Parabéns!", True, (30, 30, 30))
        texto2 = self.font_texto.render(self.subtitulo, True, (30, 30, 30))

        tela.blit(
            texto1,
            texto1.get_rect(center=(self.W // 2, popup_y + 190))
        )

        tela.blit(
            texto2,
            texto2.get_rect(center=(self.W // 2, popup_y + 230))
        )

        estrelas = self.font_titulo.render("***", True, (255, 160, 0))
        tela.blit(
            estrelas,
            estrelas.get_rect(center=(self.W // 2, popup_y + 280))
        )

        pygame.draw.rect(
            tela,
            (34, 197, 94),
            self.btn_rect,
            border_radius=18
        )

        pygame.draw.rect(
            tela,
            (20, 120, 60),
            self.btn_rect,
            4,
            border_radius=18
        )

        pygame.draw.circle(
            tela,
            (80, 255, 140),
            (self.btn_rect.left + 40, self.btn_rect.top + 12),
            8
        )

        pygame.draw.circle(
            tela,
            (80, 255, 140),
            (self.btn_rect.right - 40, self.btn_rect.top + 12),
            8
        )

        texto_btn = self.font_botao.render(self.texto_botao, True, (255, 255, 255))
        tela.blit(
            texto_btn,
            texto_btn.get_rect(center=self.btn_rect.center)
        )

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_rect.collidepoint(ev.pos):
                return True

        return False
