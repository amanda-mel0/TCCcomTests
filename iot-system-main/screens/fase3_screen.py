import pygame
import os
import random

from ui_components import LegoButton, draw_lego_brick
from screens.audio_manager import play_error, play_success
from screens.fase_concluida import PopupFaseConcluida, avancar_para_proxima_fase


class Popup:
    def __init__(self, success):
        self.success = success
        self.timer = 0
        self.duration = 120
        self.alpha = 0
        self.scale = 0.4

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
        if self.success:
            bg_color = (50, 180, 60)
            line1 = "MUITO BEM!"
            line2 = "Resposta correta!"
        else:
            bg_color = (200, 50, 40)
            line1 = "OPS!"
            line2 = "Tente de novo!"

        pw, ph = 520, 300
        bw = int(pw * self.scale)
        bh = int(ph * self.scale)
        bx = (surf.get_width() - bw) // 2
        by = (surf.get_height() - bh) // 2

        overlay = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(140, self.alpha // 2)))
        surf.blit(overlay, (0, 0))

        box = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.rect(box, (*bg_color, self.alpha), (0, 0, bw, bh), border_radius=30)
        pygame.draw.rect(box, (255, 255, 255, self.alpha), (0, 0, bw, bh), 6, border_radius=30)
        for sx in range(40, bw - 20, 55):
            pygame.draw.circle(box, (*tuple(min(255, c + 30) for c in bg_color), self.alpha), (sx, 18), 12)
            pygame.draw.circle(box, (255, 255, 255, self.alpha // 3), (sx, 18), 12, 2)
        surf.blit(box, (bx, by))

        scale_f = max(0.4, self.scale)
        txt1 = font_big.render(line1, True, (255, 255, 255))
        txt2 = font_small.render(line2, True, (255, 255, 255))
        txt1 = pygame.transform.smoothscale(txt1, (int(txt1.get_width() * scale_f), int(txt1.get_height() * scale_f)))
        txt2 = pygame.transform.smoothscale(txt2, (int(txt2.get_width() * scale_f * 0.85), int(txt2.get_height() * scale_f * 0.85)))
        surf.blit(txt1, (surf.get_width() // 2 - txt1.get_width() // 2, by + bh // 2 - txt1.get_height() - 10))
        surf.blit(txt2, (surf.get_width() // 2 - txt2.get_width() // 2, by + bh // 2 + 10))


class LogicaScreen:
    def __init__(self, surf, largura, altura, cores, estado):
        self.surf = surf
        self.W = largura
        self.H = altura
        self.cores = cores
        self.estado = estado
        self.tick = 0

        # ── Fontes mais legíveis (Arial bold no lugar de Impact) ──────────────
        # Impact é estreita e difícil de ler para crianças.
        # Arial bold é ampla, clara e disponível em todos os sistemas.
        self.FONT_BIG = pygame.font.SysFont("Arial", 52, bold=True)
        self.FONT_MED = pygame.font.SysFont("Arial", 40, bold=True)
        self.FONT_SM  = pygame.font.SysFont("Arial", 24, bold=True)
        # Fonte extra para os botões de resposta — tamanho maior para facilitar leitura
        self.FONT_BTN = pygame.font.SysFont("Arial", 44, bold=True)

        self.bg = self.cores["cinza_esc"]

        # assets
        base = os.path.join(os.path.dirname(__file__), "..")
        self.ASSETS_DIR = os.path.normpath(os.path.join(base, "assets"))
        self.ANIMALS_DIR = os.path.join(self.ASSETS_DIR, "animais")
        self.OPCOES_DIR = os.path.join(self.ASSETS_DIR, "opcoes")

        # feedback is exibido apenas como mensagem de texto no final
        self.IMG_ACERTO = None
        self.IMG_ERRO = None

        # exemplos de problemas lógicos (nome, patas serves as data placeholder)
        self.ITEMS = [
            {"nome": "gato", "patas": 4},
            {"nome": "cachorro", "patas": 4},
            {"nome": "elefante", "patas": 4},
            {"nome": "pato", "patas": 2},
        ]

        # botão voltar
        self.btn_voltar = LegoButton(40, self.H - 70, 200, 46,
                                     "VOLTAR AO MAPA", self.cores["cinza_med"],
                                     pygame.font.SysFont("Arial", 20, bold=True), studs=0)

        # estado do quiz
        self.reset_quiz()

    def reset_quiz(self):
        seq = self.ITEMS.copy()
        random.shuffle(seq)
        self.seq = seq
        self.index = 0
        self.pontos = 0
        self.state = "pergunta1"  # pergunta1, pergunta2, pergunta3, feedback
        self.etapa_respondida = None  # etapa que gerou o feedback atual
        self.feedback = None
        self.feedback_t0 = 0
        self.popup = None
        self.fase_concluida = None
        self.buttons = []
        self.prepare_question()

    def prepare_question(self):
        self.buttons = []
        if self.index >= len(self.seq):
            return
        item = self.seq[self.index]
        etapa = self.state

        # Cores LEGO para alternância
        cores_btns = [self.cores["vermelho"], self.cores["azul"], self.cores["amarelo"]]

        if etapa == "pergunta1":
            correto = len(item["nome"])
            opts = self._num_options(correto)
            for i, val in enumerate(opts):
                bx = 160 + i * 300
                cor = cores_btns[i % len(cores_btns)]
                self.buttons.append(LegoButton(bx, 480, 240, 90, str(val), cor,
                                               self.FONT_BTN, studs=1))
        elif etapa == "pergunta2":
            correto = item["nome"][0]
            opts = self._letter_options(correto)
            for i, val in enumerate(opts):
                bx = 160 + i * 240
                cor = cores_btns[i % len(cores_btns)]
                self.buttons.append(LegoButton(bx, 480, 240, 90, val.upper(), cor,
                                               self.FONT_BTN, studs=1))
        elif etapa == "pergunta3":
            correto = item["patas"]
            opts = self._num_options(correto)
            for i, val in enumerate(opts):
                bx = 160 + i * 300
                cor = cores_btns[i % len(cores_btns)]
                self.buttons.append(LegoButton(bx, 480, 240, 90, str(val), cor,
                                               self.FONT_BTN, studs=1))

    def _num_options(self, correto):
        opts = {correto}
        while len(opts) < 3:
            delta = random.choice([-3, -2, -1, 1, 2, 3, 4])
            alt = max(0, correto + delta)
            opts.add(alt)
        l = list(opts)
        random.shuffle(l)
        return l

    def _letter_options(self, correta):
        letras = list("abcdefghijklmnopqrstuvwxyz")
        if correta.lower() in letras:
            letras.remove(correta.lower())
        escolhas = random.sample(letras, 3)
        escolhas.append(correta.lower())
        random.shuffle(escolhas)
        return escolhas

    def handle_events(self, eventos):
        for ev in eventos:
            if self.fase_concluida:
                if self.fase_concluida.handle_event(ev):
                    avancar_para_proxima_fase(self.estado)
                continue

            if self.btn_voltar.handle_event(ev):
                self.estado["tela_atual"] = "mapa"
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.estado["tela_atual"] = "mapa"
            if self.state != "feedback":
                for b in self.buttons:
                    if b.handle_event(ev):
                        resp = b.texto  # LegoButton usa 'texto' não 'text'
                        item = self.seq[self.index]
                        if self.state == "pergunta1":
                            ok = (int(resp) == len(item["nome"]))
                        elif self.state == "pergunta2":
                            ok = (str(resp).upper() == item["nome"][0].upper())
                        else:
                            ok = (int(resp) == item["patas"])

                        if ok:
                            self.pontos += 1
                            self.feedback = "acerto"
                            self.popup = Popup(success=True)
                            play_success()
                        else:
                            self.feedback = "erro"
                            self.popup = Popup(success=False)
                            play_error()
                        self.etapa_respondida = self.state
                        self.state = "feedback"
                        self.feedback_t0 = pygame.time.get_ticks()
                        break

    def update(self):
        self.tick += 1
        if self.state == "feedback":
            if self.popup:
                self.popup.update()
            t = pygame.time.get_ticks() - self.feedback_t0
            if t > 900:
                # avançar
                # a etapa respondida é guardada em handle_events (não dá para
                # deduzi-la pelo texto do primeiro botão, que vem embaralhado)
                prev = {"pergunta1": 1, "pergunta2": 2}.get(self.etapa_respondida, 3)

                if prev == 1:
                    self.state = "pergunta2"
                    self.prepare_question()
                elif prev == 2:
                    self.state = "pergunta3"
                    self.prepare_question()
                else:
                    self.index += 1
                    if self.index >= len(self.seq):
                        self.fase_concluida = PopupFaseConcluida(self.W, self.H, self.estado)
                        self.state = "concluida"
                    else:
                        self.state = "pergunta1"
                        self.prepare_question()
                self.feedback = None
                self.popup = None

    def _draw_text_with_shadow(self, font, texto, cor_texto, x, y, shadow_offset=3):
        """Desenha texto com sombra escura para melhor contraste."""
        sombra = font.render(texto, True, (0, 0, 0))
        principal = font.render(texto, True, cor_texto)
        self.surf.blit(sombra, (x + shadow_offset, y + shadow_offset))
        self.surf.blit(principal, (x, y))

    def _draw_text_centered(self, font, texto, cor_texto, cy, shadow_offset=3):
        """Desenha texto centralizado horizontalmente com sombra."""
        principal = font.render(texto, True, cor_texto)
        x = self.W // 2 - principal.get_width() // 2
        self._draw_text_with_shadow(font, texto, cor_texto, x, cy, shadow_offset)

    def draw(self):
        self.surf.fill(self.bg)

        # ── Título ──────────────────────────────────────────────────────────────
        self._draw_text_with_shadow(self.FONT_BIG, "QUIZ DE ANIMAIS",
                                    (255, 255, 100), 40, 24)

        # ── Pontuação ───────────────────────────────────────────────────────────
        self._draw_text_with_shadow(self.FONT_SM, f"Pontos: {self.pontos}",
                                    (255, 255, 255), 40, 95)

        if self.index < len(self.seq):
            item = self.seq[self.index]

            # ── Painel da imagem do animal ───────────────────────────────────────
            box = pygame.Rect(80, 140, 440, 300)
            pygame.draw.rect(self.surf, (235, 235, 235), box, border_radius=14)
            pygame.draw.rect(self.surf, (80, 80, 80), box, 3, border_radius=14)

            img_path = os.path.join(self.ANIMALS_DIR, f"{item['nome']}.png")
            if os.path.exists(img_path):
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    iw = box.width - 20
                    ih = box.height - 20
                    img = pygame.transform.smoothscale(img, (iw, ih))
                    self.surf.blit(img, (box.x + 10, box.y + 10))
                except Exception:
                    txt = self.FONT_MED.render(item["nome"].capitalize(), True, (30, 30, 30))
                    self.surf.blit(txt, (box.centerx - txt.get_width() // 2,
                                        box.centery - txt.get_height() // 2))
            else:
                txt = self.FONT_BIG.render(item["nome"].capitalize(), True, (30, 30, 30))
                self.surf.blit(txt, (box.centerx - txt.get_width() // 2,
                                     box.centery - txt.get_height() // 2))

            # ── Caixa da pergunta (painel com fundo escuro p/ contraste) ─────────
            if self.state in ("pergunta1", "pergunta2", "pergunta3"):
                perguntas = {
                    "pergunta1": "Quantas letras tem o nome?",
                    "pergunta2": "Qual é a primeira letra?",
                    "pergunta3": "Quantas patas ele possui?",
                }
                texto_pergunta = perguntas[self.state]

                # Renderiza para calcular largura real
                surf_p = self.FONT_MED.render(texto_pergunta, True, (255, 255, 255))
                px = 560
                py = 210
                pad_x, pad_y = 18, 12
                painel = pygame.Rect(px - pad_x, py - pad_y,
                                     surf_p.get_width() + pad_x * 2,
                                     surf_p.get_height() + pad_y * 2)
                # Fundo semitransparente para a pergunta
                overlay = pygame.Surface((painel.width, painel.height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                self.surf.blit(overlay, (painel.x, painel.y))
                pygame.draw.rect(self.surf, (255, 255, 100), painel, 3, border_radius=10)

                self._draw_text_with_shadow(self.FONT_MED, texto_pergunta,
                                            (255, 255, 255), px, py, shadow_offset=2)

        # ── Feedback ────────────────────────────────────────────────────────────
        if self.state == "feedback" and self.popup:
            self.popup.draw(self.surf, self.FONT_BIG, self.FONT_SM)

        if self.fase_concluida:
            self.fase_concluida.draw(self.surf)

        # ── Botões de resposta ───────────────────────────────────────────────────
        if self.state != "feedback" and not self.fase_concluida:
            for b in self.buttons:
                b.draw(self.surf)

        # ── Botão voltar ─────────────────────────────────────────────────────────
        self.btn_voltar.draw(self.surf)
