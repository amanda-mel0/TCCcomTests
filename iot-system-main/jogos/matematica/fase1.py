import pygame
import random
import sys

pygame.init()

LARGURA = 1000
ALTURA = 700

TELA = pygame.display.set_mode(
    (LARGURA, ALTURA)
)

pygame.display.set_caption(
    "LerBrincando - Matemática"
)

BRANCO = (255, 255, 255)
PRETO = (30, 30, 30)
ROSA = (255, 120, 180)



fonte_titulo = pygame.font.SysFont(
    "arial",
    50,
    bold=True
)

fonte_botao = pygame.font.SysFont(
    "arial",
    36,
    bold=True
)

imagem_acerto = pygame.image.load(
    "assets/opcoes/acertou.png"
)

imagem_erro = pygame.image.load(
    "assets/opcoes/errou.png"
)



imagem_acerto = pygame.transform.scale(
    imagem_acerto,
    (1000, 700)
)

imagem_erro = pygame.transform.scale(
    imagem_erro,
    (1000, 700)
)


feedback = None

tempo_feedback = 0



def gerar_pergunta():

    numero1 = 3

    numero2 = 5

    resposta_correta = numero1 + numero2

    alternativas = [

        resposta_correta,

        resposta_correta + 1,

        resposta_correta - 4
    ]

    random.shuffle(alternativas)

    pergunta = f"{numero1} + {numero2} = ?"

    return pergunta, resposta_correta, alternativas



pergunta, resposta_correta, alternativas = gerar_pergunta()

pontos = 0

botoes = []

for i in range(3):

    rect = pygame.Rect(

        250 + (i * 220),
        400,
        180,
        100
    )

    botoes.append(rect)


while True:


    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:

            pygame.quit()

            sys.exit()


        if evento.type == pygame.MOUSEBUTTONDOWN:

            mouse_pos = pygame.mouse.get_pos()

            
            for i, botao in enumerate(botoes):

                if botao.collidepoint(mouse_pos):

                    resposta = alternativas[i]

                    if resposta == resposta_correta:

                        pontos += 1

                        feedback = "acerto"

                        tempo_feedback = pygame.time.get_ticks()
                        exit()

                    
                    else:

                        feedback = "erro"

                        tempo_feedback = pygame.time.get_ticks()


    TELA.fill((255, 220, 240))


    titulo = fonte_titulo.render(

        pergunta,
        True,
        PRETO
    )

    TELA.blit(
        titulo,
        (350, 200)
    )



    texto_pontos = fonte_botao.render(

        f"Pontos: {pontos}",
        True,
        PRETO
    )

    TELA.blit(
        texto_pontos,
        (40, 40)
    )



    for i, botao in enumerate(botoes):

        pygame.draw.rect(

            TELA,
            ROSA,
            botao,
            border_radius=20
        )

        texto = fonte_botao.render(

            str(alternativas[i]),
            True,
            BRANCO
        )

        texto_rect = texto.get_rect(

            center=botao.center
        )

        TELA.blit(texto, texto_rect)



    if feedback == "acerto":

        TELA.blit(
            imagem_acerto,
            (390, 120)
        )

    elif feedback == "erro":

        TELA.blit(
            imagem_erro,
            (390, 120)
        )



    if feedback is not None:

        tempo_atual = pygame.time.get_ticks()

   
        if tempo_atual - tempo_feedback > 700:

    
            pergunta, resposta_correta, alternativas = gerar_pergunta()

         
            feedback = None



    pygame.display.update()