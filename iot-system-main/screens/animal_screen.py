import pygame
import os
import random

from ui_components import LegoButton


class AnimalScreen:
    def __init__(self, surf, largura, altura, cores, estado):
        self.surf = surf
        self.W = largura
        self.H = altura
        self.cores = cores
        self.estado = estado
        self.tick = 0

        self.FONT_BIG = pygame.font.SysFont("Arial", 48, bold=True)
        self.FONT_MED = pygame.font.SysFont("Arial", 34, bold=True)
        self.FONT_SM = pygame.font.SysFont("Arial", 24)

        self.bg = (240, 248, 255)

        # assets
        base = os.path.join(os.path.dirname(__file__), "..")
        self.ASSETS_DIR = os.path.normpath(os.path.join(base, "assets"))
        self.ANIMALS_DIR = os.path.join(self.ASSETS_DIR, "animais")
        self.OPCOES_DIR = os.path.join(self.ASSETS_DIR, "opcoes")

        # feedback images
        self.IMG_ACERTO = None
        self.IMG_ERRO = None
        for fn in ("Acertou.png", "Errou.png"):
            p = os.path.join(self.OPCOES_DIR, fn)
            if os.path.exists(p):
                try:
                    img = pygame.image.load(p).convert_alpha()
                    img = pygame.transform.smoothscale(img, (500, 300))
                    if fn == "Acertou.png":
                        self.IMG_ACERTO = img
                    else:
                        self.IMG_ERRO = img
                except Exception:
                    pass

        # exemplos de animais (nome, patas)
        self.ANIMAIS = [
            {"nome": "gato", "patas": 4},
            {"nome": "cachorro", "patas": 4},
            {"nome": "elefante", "patas": 4},
            {"nome": "pato", "patas": 2},
        ]

        # botão voltar
        self.btn_voltar = LegoButton(40, self.H - 70, 200, 46,
                                     " VOLTAR AO MAPA", self.cores["cinza_med"],
                                     pygame.font.SysFont("Impact", 20), studs=1)

        # estado do quiz
        self.reset_quiz()

    def reset_quiz(self):
        seq = self.ANIMAIS.copy()
        random.shuffle(seq)
        self.animal_seq = seq
        self.index = 0
        self.pontos = 0
        self.state = "pergunta1"  # pergunta1, pergunta2, pergunta3, feedback
        self.etapa_respondida = None  # etapa que gerou o feedback atual
        self.feedback = None
        self.feedback_t0 = 0
        self.buttons = []
        self.prepare_question()

    def prepare_question(self):
        self.buttons = []
        if self.index >= len(self.animal_seq):
            return
        animal = self.animal_seq[self.index]
        etapa = self.state
        if etapa == "pergunta1":
            correto = len(animal["nome"])
            opts = self._num_options(correto)
            for i, val in enumerate(opts):
                bx = 160 + i * 300
                self.buttons.append(Button((bx, 480, 240, 90), val))
        elif etapa == "pergunta2":
            correto = animal["nome"][0]
            opts = self._letter_options(correto)
            for i, val in enumerate(opts):
                bx = 160 + i * 240
                self.buttons.append(Button((bx, 480, 240, 90), val.upper()))
        elif etapa == "pergunta3":
            correto = animal["patas"]
            opts = self._num_options(correto)
            for i, val in enumerate(opts):
                bx = 160 + i * 300
                self.buttons.append(Button((bx, 480, 240, 90), val))

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
            if self.btn_voltar.handle_event(ev):
                self.estado["tela_atual"] = "mapa"
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.estado["tela_atual"] = "mapa"
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.state != "feedback":
                mx, my = ev.pos
                for b in self.buttons:
                    if b.collidepoint((mx, my)):
                        resp = b.text
                        animal = self.animal_seq[self.index]
                        if self.state == "pergunta1":
                            ok = (int(resp) == len(animal["nome"]))
                        elif self.state == "pergunta2":
                            ok = (str(resp).upper() == animal["nome"][0].upper())
                        else:
                            ok = (int(resp) == animal["patas"])

                        if ok:
                            self.pontos += 1
                            self.feedback = "acerto"
                        else:
                            self.feedback = "erro"
                        self.etapa_respondida = self.state
                        self.state = "feedback"
                        self.feedback_t0 = pygame.time.get_ticks()
                        break

    def update(self):
        self.tick += 1
        if self.state == "feedback":
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
                    if self.index >= len(self.animal_seq):
                        # fim -> voltar ao mapa
                        self.estado["tela_atual"] = "mapa"
                    else:
                        self.state = "pergunta1"
                        self.prepare_question()
                self.feedback = None

    def draw(self):
        self.surf.fill(self.bg)
        title = self.FONT_BIG.render("Quiz de Animais", True, (30, 30, 30))
        self.surf.blit(title, (40, 24))
        score_txt = self.FONT_SM.render(f"Pontos: {self.pontos}", True, (30, 30, 30))
        self.surf.blit(score_txt, (40, 90))

        if self.index < len(self.animal_seq):
            animal = self.animal_seq[self.index]
            # desenha caixa de imagem
            box = pygame.Rect(80, 140, 440, 300)
            pygame.draw.rect(self.surf, (230, 230, 230), box, border_radius=12)
            img_path = os.path.join(self.ANIMALS_DIR, f"{animal['nome']}.png")
            if os.path.exists(img_path):
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    iw = box.width - 20
                    ih = box.height - 20
                    img = pygame.transform.smoothscale(img, (iw, ih))
                    self.surf.blit(img, (box.x + 10, box.y + 10))
                except Exception:
                    txt = self.FONT_MED.render(animal["nome"].capitalize(), True, (30, 30, 30))
                    self.surf.blit(txt, (box.centerx - txt.get_width() // 2, box.centery - txt.get_height() // 2))
            else:
                txt = self.FONT_BIG.render(animal["nome"].capitalize(), True, (30, 30, 30))
                self.surf.blit(txt, (box.centerx - txt.get_width() // 2, box.centery - txt.get_height() // 2))

            # pergunta
            if self.state == "pergunta1":
                qtxt = self.FONT_MED.render("Quantas letras tem o nome?", True, (30, 30, 30))
                self.surf.blit(qtxt, (600, 200))
            elif self.state == "pergunta2":
                qtxt = self.FONT_MED.render("Qual é a primeira letra?", True, (30, 30, 30))
                self.surf.blit(qtxt, (600, 200))
            elif self.state == "pergunta3":
                qtxt = self.FONT_MED.render("Quantas patas ele possui?", True, (30, 30, 30))
                self.surf.blit(qtxt, (600, 200))

        # feedback
        if self.state == "feedback":
            t = pygame.time.get_ticks() - self.feedback_t0
            if self.feedback == "acerto" and self.IMG_ACERTO:
                self.surf.blit(self.IMG_ACERTO, (300, 180))
            elif self.feedback == "erro" and self.IMG_ERRO:
                self.surf.blit(self.IMG_ERRO, (300, 180))
            else:
                msg = "ACERTO!" if self.feedback == "acerto" else "ERRO"
                c = (40, 160, 60) if self.feedback == "acerto" else (200, 50, 50)
                ttxt = self.FONT_BIG.render(msg, True, c)
                self.surf.blit(ttxt, (self.W // 2 - ttxt.get_width() // 2, self.H // 2 - ttxt.get_height() // 2))

        # desenhar botões
        if self.state != "feedback":
            mx, my = pygame.mouse.get_pos()
            for b in self.buttons:
                b.draw(self.surf, b.collidepoint((mx, my)))

        # botão voltar
        self.btn_voltar.draw(self.surf)


class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text

    def draw(self, surf, hover=False):
        col = (255, 120, 140) if hover else (255, 160, 180)
        pygame.draw.rect(surf, col, self.rect, border_radius=16)
        pygame.draw.rect(surf, (60, 60, 60), self.rect, 3, border_radius=16)
        t = pygame.font.SysFont("Arial", 34, bold=True).render(str(self.text), True, (30, 30, 30))
        surf.blit(t, (self.rect.centerx - t.get_width() // 2, self.rect.centery - t.get_height() // 2))

    def collidepoint(self, p):
        return self.rect.collidepoint(p)
