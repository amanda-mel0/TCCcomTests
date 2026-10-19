import pygame
import os
import random
import sys

pygame.init()

WIDTH, HEIGHT = 1100, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quiz de Animais")

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
ANIMALS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "animais")
OPCOES_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "opcoes")

FONT_BIG = pygame.font.SysFont("Arial", 48, bold=True)
FONT_MED = pygame.font.SysFont("Arial", 34, bold=True)
FONT_SM = pygame.font.SysFont("Arial", 24)

BG = (240, 248, 255)
BTN_COLOR = (255, 160, 180)
BTN_HOVER = (255, 120, 140)
TEXT_COLOR = (30, 30, 30)

# Lista de animais de exemplo. Se houver imagens em assets/animais/<nome>.png, serão mostradas.
ANIMAIS = [
    {"nome": "gato", "patas": 4},
    {"nome": "cachorro", "patas": 4},
    {"nome": "elefante", "patas": 4},
    {"nome": "pato", "patas": 2},
]

# carregar imagens de feedback se existirem
IMG_ACERTO = None
IMG_ERRO = None
for fn, varname in [("Acertou.png", "IMG_ACERTO"), ("Errou.png", "IMG_ERRO")]:
    path = os.path.join(OPCOES_DIR, fn)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (500, 300))
            if fn == "Acertou.png":
                IMG_ACERTO = img
            else:
                IMG_ERRO = img
        except Exception:
            pass


class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text

    def draw(self, surf, hover=False):
        col = BTN_HOVER if hover else BTN_COLOR
        pygame.draw.rect(surf, col, self.rect, border_radius=16)
        pygame.draw.rect(surf, (60,60,60), self.rect, 3, border_radius=16)
        t = FONT_MED.render(str(self.text), True, TEXT_COLOR)
        surf.blit(t, (self.rect.centerx - t.get_width()//2, self.rect.centery - t.get_height()//2))

    def collidepoint(self, p):
        return self.rect.collidepoint(p)


def escolhe_opcoes_numero(correto):
    # gera 3 alternativas incluindo a correta
    opts = {correto}
    while len(opts) < 3:
        delta = random.choice([-3, -2, -1, 1, 2, 3, 4])
        alt = max(0, correto + delta)
        opts.add(alt)
    l = list(opts)
    random.shuffle(l)
    return l


def escolhe_opcoes_letra(correta):
    letras = list("abcdefghijklmnopqrstuvwxyz")
    letras.remove(correta)
    escolhas = random.sample(letras, 3)
    escolhas.append(correta)
    random.shuffle(escolhas)
    return escolhas


def run_quiz():
    index = 0
    pontos = 0
    state = "pergunta1"  # pergunta1, pergunta2, pergunta3, feedback
    feedback = None
    feedback_t0 = 0

    animal_seq = ANIMAIS.copy()
    random.shuffle(animal_seq)

    # botões atuais
    buttons = []

    def preparar_pergunta(animal, etapa):
        nonlocal buttons
        buttons = []
        if etapa == 1:
            correto = len(animal["nome"])
            opts = escolhe_opcoes_numero(correto)
            for i, val in enumerate(opts):
                bx = 160 + i * 300
                buttons.append(Button((bx, 480, 240, 90), val))
            return corret
        elif etapa == 2:
            correto = animal["nome"][0]
            opts = escolhe_opcoes_letra(correto)
            for i, val in enumerate(opts):
                bx = 160 + i * 240
                buttons.append(Button((bx, 480, 240, 90), val.upper()))
            return correto
        elif etapa == 3:
            correto = animal["patas"]
            opts = escolhe_opcoes_numero(correto)
            for i, val in enumerate(opts):
                bx = 160 + i * 300
                buttons.append(Button((bx, 480, 240, 90), val))
            return correto

    # preparar primeira pergunta
    animal = animal_seq[index]
    correto_atual = preparar_pergunta(animal, 1)

    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and state != "feedback":
                mx,my = ev.pos
                for b in buttons:
                    if b.collidepoint((mx,my)):
                        resp = b.text
                        # normalizar respostas (números vs letras)
                        if state == "pergunta1":
                            correto = len(animal["nome"])
                            ok = (int(resp) == correto)
                        elif state == "pergunta2":
                            correto = animal["nome"][0].upper()
                            ok = (str(resp).upper() == correto)
                        else:
                            correto = animal["patas"]
                            ok = (int(resp) == correto)

                        if ok:
                            pontos += 1
                            feedback = "acerto"
                        else:
                            feedback = "erro"

                        state = "feedback"
                        feedback_t0 = pygame.time.get_ticks()
                        break
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False

        SCREEN.fill(BG)

        # desenhar título e pontuação
        title = FONT_BIG.render("Quiz de Animais", True, TEXT_COLOR)
        SCREEN.blit(title, (40, 24))
        score_txt = FONT_SM.render(f"Pontos: {pontos}", True, TEXT_COLOR)
        SCREEN.blit(score_txt, (40, 90))

        # desenhar animal (imagem se existir)
        box = pygame.Rect(80, 140, 440, 300)
        pygame.draw.rect(SCREEN, (230,230,230), box, border_radius=12)
        img_path = os.path.join(ANIMALS_DIR, f"{animal['nome']}.png")
        if os.path.exists(img_path):
            try:
                img = pygame.image.load(img_path).convert_alpha()
                iw = box.width - 20
                ih = box.height - 20
                img = pygame.transform.smoothscale(img, (iw, ih))
                SCREEN.blit(img, (box.x+10, box.y+10))
            except Exception:
                txt = FONT_MED.render(animal["nome"].capitalize(), True, TEXT_COLOR)
                SCREEN.blit(txt, (box.centerx - txt.get_width()//2, box.centery - txt.get_height()//2))
        else:
            # placeholder
            txt = FONT_BIG.render(animal["nome"].capitalize(), True, TEXT_COLOR)
            SCREEN.blit(txt, (box.centerx - txt.get_width()//2, box.centery - txt.get_height()//2))

        # perguntar conforme etapa
        if state == "pergunta1":
            qtxt = FONT_MED.render("Quantas letras tem o nome?", True, TEXT_COLOR)
            SCREEN.blit(qtxt, (600, 200))
        elif state == "pergunta2":
            qtxt = FONT_MED.render("Qual é a primeira letra?", True, TEXT_COLOR)
            SCREEN.blit(qtxt, (600, 200))
        elif state == "pergunta3":
            qtxt = FONT_MED.render("Quantas patas ele possui?", True, TEXT_COLOR)
            SCREEN.blit(qtxt, (600, 200))
        elif state == "feedback":
            # mostrar imagem de feedback por 900ms
            t = pygame.time.get_ticks() - feedback_t0
            if feedback == "acerto" and IMG_ACERTO:
                SCREEN.blit(IMG_ACERTO, (300, 180))
            elif feedback == "erro" and IMG_ERRO:
                SCREEN.blit(IMG_ERRO, (300, 180))
            else:
                msg = "ACERTO!" if feedback == "acerto" else "ERRO"
                c = (40,160,60) if feedback == "acerto" else (200,50,50)
                ttxt = FONT_BIG.render(msg, True, c)
                SCREEN.blit(ttxt, (WIDTH//2 - ttxt.get_width()//2, HEIGHT//2 - ttxt.get_height()//2))

            if t > 900:
                # avançar etapa
                if state == "feedback":
                    # se era feedback da pergunta1, ir para pergunta2
                    if 'last_question' not in locals():
                        pass
                # avançar fluxo
                if state == "feedback":
                    # descobrir qual pergunta foi respondida anteriormente
                    # inferimos pela composição dos botões: se as opções são letras -> pergunta2
                    sample = buttons[0].text if buttons else None
                    if isinstance(sample, str) and sample.isalpha() and len(sample) == 1:
                        prev = 2
                    else:
                        # se o texto for número -> prev = 1 ou 3
                        # se o primeiro botão corresponde a len(nome) -> era pergunta1
                        try:
                            if int(buttons[0].text) == len(animal['nome']):
                                prev = 1
                            else:
                                prev = 3
                        except Exception:
                            prev = 1

                    if prev == 1:
                        state = 'pergunta2'
                        correto_atual = preparar_pergunta(animal, 2)
                    elif prev == 2:
                        state = 'pergunta3'
                        correto_atual = preparar_pergunta(animal, 3)
                    else:
                        # fim do ciclo para este animal -> próximo animal
                        index += 1
                        if index >= len(animal_seq):
                            # terminou lista
                            running = False
                        else:
                            animal = animal_seq[index]
                            state = 'pergunta1'
                            preparar_pergunta(animal, 1)
                feedback = None

        # desenhar botões (somente se não estiver em feedback)
        if state != 'feedback':
            mx,my = pygame.mouse.get_pos()
            for b in buttons:
                b.draw(SCREEN, b.collidepoint((mx,my)))

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    run_quiz()
