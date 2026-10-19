import pygame
from ui_components import (
    draw_lego_brick, draw_panel, draw_sky_background,
    draw_grass_strip, LegoButton
)


CORES_FASES = [
    (34,  139,  34),
    (37,   99, 235),
    (234, 120,  10),
    (200, 170,   0),
    (130,  50, 210),
    (34,  139,  34),
    (37,   99, 235),
    (210,  30,  30),
    (200, 170,   0),
    (37,   99, 235),
]

NOMES_FASES = [
    "As Vogais",
    "As Consoantes",
    "Sílabas Simples",
    "Corrida Matemática",
    "Palavras com Dígrafo",
    "Frases Simples",
    "Leitura de Histórias",
    "Escrita Criativa",
    "Alfabeto Completo",
    "Desafio Final",
]

MISSOES_FASES = {
    4: {
        "titulo": "Corrida Matemática",
        "descricao": "Um carrinho avança quando a criança resolve:",
        "problemas": ["1 + 2", "3 + 1", "5 - 2"],
        "habilidades": "soma e subtração"
    }
}


class FaseScreen:
    def __init__(self, surf, largura, altura, cores, estado, numero):
        self.surf = surf
        self.W = largura
        self.H = altura
        self.cores = cores
        self.estado = estado
        self.numero = numero
        self.tick = 0

        self.cor_fase = CORES_FASES[numero - 1]
        self.nome_fase = NOMES_FASES[numero - 1]

        # Fontes
        self.f_num    = pygame.font.SysFont("Impact", 100, bold=True)
        self.f_titulo = pygame.font.SysFont("Impact", 48, bold=True)
        self.f_sub    = pygame.font.SysFont("Arial", 22, bold=True)
        self.f_info   = pygame.font.SysFont("Arial", 18)
        self.f_btn    = pygame.font.SysFont("Impact", 20)

        # Botão voltar
        self.btn_voltar = LegoButton(
            40, self.H - 70, 200, 46,
            "VOLTAR AO MAPA", self.cores["cinza_med"], self.f_btn, studs=0
        )

        # Partículas decorativas
        import random
        self.particulas = [
            {
                "x": random.randint(0, largura),
                "y": random.randint(0, altura),
                "r": random.randint(4, 12),
                "vel": random.uniform(0.3, 1.2),
                "cor": random.choice([
                    (220,38,38),(37,99,235),(34,197,94),
                    (234,179,8),(249,115,22),(147,51,234)
                ])
            }
            for _ in range(18)
        ]

    def handle_events(self, eventos):
        for ev in eventos:
            if self.btn_voltar.handle_event(ev):
                self.estado["tela_atual"] = "mapa"
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.estado["tela_atual"] = "mapa"

    def update(self):
        self.tick += 1
        for p in self.particulas:
            p["y"] -= p["vel"]
            if p["y"] < -20:
                import random
                p["y"] = self.H + 10
                p["x"] = random.randint(0, self.W)

    def draw(self):
        draw_sky_background(self.surf, self.W, self.H, self.tick)
        draw_grass_strip(self.surf, self.W, self.H)

        # Partículas flutuantes
        for p in self.particulas:
            pygame.draw.circle(self.surf, p["cor"], (int(p["x"]), int(p["y"])), p["r"])
            r, g, b = p["cor"]
            pygame.draw.circle(self.surf,
                                (min(255,r+60), min(255,g+60), min(255,b+60)),
                                (int(p["x"])-2, int(p["y"])-2), p["r"]//2)

        # Painel central
        pw, ph = 600, 400
        px = self.W//2 - pw//2
        py = self.H//2 - ph//2
        draw_panel(self.surf, (px, py, pw, ph), cor_fundo=(20,20,30), alfa=230)

        # Tijolos decorativos no topo do painel
        qtd = 6
        tw = pw // qtd
        cores_deco = [(220,38,38),(37,99,235),(34,197,94),(234,179,8),(249,115,22),(147,51,234)]
        for i in range(qtd):
            draw_lego_brick(self.surf, cores_deco[i],
                            (px + i*tw, py-20, tw-2, 22), studs=1, raio_borda=5)

        # Grande número da fase com animação de pulso
        escala_pulso = 1 + 0.04 * abs(pygame.math.Vector2(0,1).rotate(self.tick*2).y)
        num_str = str(self.numero)
        num_base = self.f_num.render(num_str, True, self.cor_fase)
        ns = pygame.transform.scale(num_base,
             (int(num_base.get_width()*escala_pulso),
              int(num_base.get_height()*escala_pulso)))
        # Sombra
        num_sombra = self.f_num.render(num_str, True, (0,0,0))
        self.surf.blit(num_sombra, num_sombra.get_rect(center=(self.W//2+4, py+110)))
        self.surf.blit(ns, ns.get_rect(center=(self.W//2, py+108)))

        # "FASE X"
        fase_txt = self.f_titulo.render(f"FASE {self.numero}", True, (255,255,255))
        sombra   = self.f_titulo.render(f"FASE {self.numero}", True, (0,0,0))
        self.surf.blit(sombra, sombra.get_rect(centerx=self.W//2+2, top=py+190))
        self.surf.blit(fase_txt,fase_txt.get_rect(centerx=self.W//2,   top=py+188))

        # Nome da fase
        nome_txt = self.f_sub.render(self.nome_fase, True, (200,220,255))
        self.surf.blit(nome_txt, nome_txt.get_rect(centerx=self.W//2, top=py+245))

        # Linha separadora
        pygame.draw.line(self.surf, self.cor_fase,
                         (px+40, py+288), (px+pw-40, py+288), 2)

        # Conteúdo específico da fase
        if self.numero in MISSOES_FASES:
            missao = MISSOES_FASES[self.numero]
            desc = self.f_info.render(missao["descricao"], True, (150,170,210))
            self.surf.blit(desc, desc.get_rect(centerx=self.W//2, top=py+308))
            
            # Problemas
            y_pos = py+338
            for i, problema in enumerate(missao["problemas"]):
                if i < 2:
                    prob_txt = self.f_info.render(f"- {problema}", True, (120,140,180))
                    self.surf.blit(prob_txt, prob_txt.get_rect(centerx=self.W//2, top=y_pos))
                    y_pos += 25
            
            # Habilidades
            hab_txt = self.f_info.render(f"Habilidades: {missao['habilidades']}", True, (100,200,100))
            self.surf.blit(hab_txt, hab_txt.get_rect(centerx=self.W//2, top=y_pos+10))
        else:
            # Placeholder padrão para outras fases
            info1 = self.f_info.render("Conteúdo em construção...", True, (150,170,210))
            info2 = self.f_info.render("Esta tela será preenchida com as atividades da fase.",
                                       True, (120,140,180))
            self.surf.blit(info1, info1.get_rect(centerx=self.W//2, top=py+308))
            self.surf.blit(info2, info2.get_rect(centerx=self.W//2, top=py+338))

        # Barra inferior colorida
        draw_lego_brick(self.surf, self.cor_fase,
                        (px, py+ph-12, pw, 14), studs=0, raio_borda=8)

        # Botão voltar
        self.btn_voltar.draw(self.surf)

        # Tecla ESC hint
        esc = self.f_info.render("ESC = voltar ao mapa", True, (100,120,150))
        self.surf.blit(esc, (self.W-esc.get_width()-16, self.H-28))
