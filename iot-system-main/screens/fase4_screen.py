import pygame
import random
import math
from ui_components import LegoButton, draw_lego_brick
from screens.audio_manager import play_error, play_success
from screens.fase_concluida import PopupFaseConcluida, avancar_para_proxima_fase

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

# ── Constantes do jogo ──────────────────────────────────────────────────
PISTA_Y = 480
CARRO_X_START = 100
CARRO_Y = PISTA_Y - 40
FINISH_X = 1000
BLOCK_SIZE = 50


class Carro:
    """Carrinho que avança na pista"""
    def __init__(self):
        self.x = CARRO_X_START
        self.y = CARRO_Y
        self.width = 80
        self.height = 50
        self.speed = 0
        self.target_x = CARRO_X_START
        self.wobble = 0

    def avanca(self, distancia):
        """Faz o carrinho avançar uma distância"""
        self.target_x = min(FINISH_X, self.x + distancia)
        self.speed = (self.target_x - self.x) / 20  # suave animação

    def update(self):
        """Atualiza posição do carrinho"""
        if abs(self.target_x - self.x) > 1:
            self.x += self.speed
        else:
            self.x = self.target_x
            self.speed = 0
        self.wobble += 0.1

    def chegou(self):
        """Verifica se chegou no final"""
        return self.x >= FINISH_X - 20

    def draw(self, surf, font):
        """Desenha o carrinho estilo LEGO"""
        x, y = int(self.x), int(self.y)
        
        # Sombra
        shadow = pygame.Surface((self.width + 10, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 50), (5, 8, self.width, 12))
        surf.blit(shadow, (x - 5, y + self.height - 5))
        
        # Corpo do carro (blocos LEGO)
        # Base
        pygame.draw.rect(surf, LEGO_RED, (x, y, self.width, 32), border_radius=6)
        pygame.draw.rect(surf, (150, 20, 15), (x, y, self.width, 32), 3, border_radius=6)
        
        # Teto (bloco LEGO em cima)
        pygame.draw.rect(surf, LEGO_YELLOW, (x + 12, y - 12, self.width - 24, 16), border_radius=4)
        pygame.draw.rect(surf, (200, 150, 20), (x + 12, y - 12, self.width - 24, 16), 2, border_radius=4)
        
        # Rodas
        roda_y = y + 30
        for roda_x in [x + 15, x + self.width - 15]:
            # Roda grande
            pygame.draw.circle(surf, LEGO_DARK, (roda_x, roda_y), 10)
            pygame.draw.circle(surf, LEGO_BLUE, (roda_x, roda_y), 8)
            # Padrão na roda
            for angle in range(0, 360, 60):
                rad = math.radians(angle + self.wobble * 10)
                px = roda_x + int(7 * math.cos(rad))
                py = roda_y + int(7 * math.sin(rad))
                pygame.draw.circle(surf, LEGO_DARK, (px, py), 2)
        
        # Números do LEGO na lateral
        for i, px in enumerate([x + 20, x + 50]):
            pygame.draw.ellipse(surf, (220, 100, 50), (px - 6, y - 8, 12, 8))
            pygame.draw.ellipse(surf, (180, 70, 30), (px - 6, y - 8, 12, 8), 1)


class Problema:
    """Problema matemático a resolver - Apropriado para 4-6 anos"""
    def __init__(self):
        self.historico = []
        self.tipo = None
        self.regenera()

    def regenera(self):
        """Gera um novo problema variado para crianças pequenas"""
        # Tenta gerar um problema diferente do histórico
        encontrou_diferente = False
        for _ in range(5):
            tipo = random.choice(["soma_facil", "soma_media", "subtracao_facil"])
            
            if tipo == "soma_facil":
                # 1-3 + 1-3 (resultado 2-6)
                self.a = random.randint(1, 3)
                self.b = random.randint(1, 3)
                self.resposta = self.a + self.b
                self.texto = f"{self.a} + {self.b}"
            
            elif tipo == "soma_media":
                # 2-5 + 2-5 (resultado 4-10)
                self.a = random.randint(2, 5)
                self.b = random.randint(2, 5)
                self.resposta = self.a + self.b
                self.texto = f"{self.a} + {self.b}"
            
            elif tipo == "subtracao_facil":
                # Subtração simples: 3-8 menos 1-3
                self.a = random.randint(3, 8)
                self.b = random.randint(1, min(3, self.a - 1))
                self.resposta = self.a - self.b
                self.texto = f"{self.a} - {self.b}"
            
            # Verifica se não está no histórico recente
            problema_atual = f"{self.texto}={self.resposta}"
            if problema_atual not in self.historico[-8:]:
                encontrou_diferente = True
                break
        
        # Atualiza histórico
        self.historico.append(f"{self.texto}={self.resposta}")
        if len(self.historico) > 15:
            self.historico.pop(0)
        
        # Gera 4 opções de resposta
        self.opcoes = []
        
        # Adiciona a resposta correta
        self.opcoes.append(self.resposta)
        
        # Gera 3 opções incorretas
        opcoes_incorretas_set = set()
        while len(opcoes_incorretas_set) < 3:
            # Opções próximas (ideais para crianças)
            opcao = self.resposta + random.choice([-2, -1, 1, 2, 3])
            
            # Garante que é válida (maior que 0 e diferente da resposta)
            if opcao > 0 and opcao != self.resposta and opcao not in opcoes_incorretas_set:
                opcoes_incorretas_set.add(opcao)
        
        self.opcoes.extend(list(opcoes_incorretas_set))
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
            particle["vy"] += 0.15  # gravidade

    def finalizado(self):
        return self.timer >= self.duracao

    def draw(self, surf, font_big):
        # Overlay semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 40))
        surf.blit(overlay, (0, 0))
        
        # Partículas
        for p in self.particles:
            if 0 <= p["y"] <= HEIGHT:
                pygame.draw.circle(surf, p["cor"], (int(p["x"]), int(p["y"])), p["tamanho"] // 2)
        
        # Caixa de mensagem
        box_w, box_h = 400, 150
        scale = max(0.1, self.scale)
        bw, bh = int(box_w * scale), int(box_h * scale)
        bx, by = WIDTH // 2 - bw // 2, HEIGHT // 2 - bh // 2 - 80
        
        cor_fundo = LEGO_GREEN if self.acertou else LEGO_RED
        cor_borda = (50, 140, 50) if self.acertou else (150, 20, 15)
        
        pygame.draw.rect(surf, cor_fundo, (bx, by, bw, bh), border_radius=16)
        pygame.draw.rect(surf, cor_borda, (bx, by, bw, bh), 4, border_radius=16)
        
        # Studs LEGO na caixa
        for sx in range(bx + 30, bx + bw - 20, 60):
            pygame.draw.circle(surf, cor_borda, (sx, by + 12), 8)
            pygame.draw.circle(surf, cor_fundo, (sx, by + 12), 8, 2)
        
        # Texto
        msg = "MUITO BEM!" if self.acertou else "TENTE NOVAMENTE"
        txt = font_big.render(msg, True, LEGO_WHITE)
        txt_scale = pygame.transform.smoothscale(txt, (int(txt.get_width() * scale), int(txt.get_height() * scale)))
        surf.blit(txt_scale, (bx + bw // 2 - txt_scale.get_width() // 2, by + bh // 2 - txt_scale.get_height() // 2))


class Fase4Screen:
    """Jogo da Corrida Matemática"""
    
    def __init__(self, surf, largura, altura, cores, estado):
        self.surf = surf
        self.W = largura
        self.H = altura
        self.cores = cores
        self.estado = estado
        self.tick = 0
        
        # Fontes - aumentadas para crianças verem melhor
        self.font_huge = pygame.font.SysFont("Arial Rounded MT Bold", 96, bold=True)
        self.font_big = pygame.font.SysFont("Arial Rounded MT Bold", 56, bold=True)
        self.font_med = pygame.font.SysFont("Arial Rounded MT Bold", 40, bold=True)
        self.font_small = pygame.font.SysFont("Arial Rounded MT Bold", 24, bold=True)
        
        # Game state
        self.carro = Carro()
        self.problema = Problema()
        self.pontos = 0
        self.acertos_consecutivos = 0
        self.fase_concluida = None
        self.popup = None
        self.fase_completa = False
        self.regenerar_na_proxima = False  # Flag para regenerar no próximo update
        
        # Botão voltar
        self.btn_voltar = LegoButton(
            40, self.H - 70, 200, 46,
            "VOLTAR AO MAPA", self.cores["cinza_med"], self.font_small, studs=0
        )
        
        # Botões de resposta
        self.botoes_resposta = []
        self._create_answer_buttons()

    def _create_answer_buttons(self):
        """Cria os botões com as opções de resposta"""
        self.botoes_resposta = []
        botao_w = 130
        botao_h = 110
        gap = 25
        total_w = 4 * botao_w + 3 * gap
        start_x = (self.W - total_w) // 2
        
        for i, resposta in enumerate(self.problema.opcoes):
            x = start_x + i * (botao_w + gap)
            y = 280
            cor = [LEGO_BLUE, LEGO_ORANGE, LEGO_PURPLE, LEGO_RED][i]
            self.botoes_resposta.append({
                "rect": pygame.Rect(x, y, botao_w, botao_h),
                "resposta": resposta,
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
                        if botao["resposta"] == self.problema.resposta:
                            self.pontos += 10
                            self.acertos_consecutivos += 1
                            self.carro.avanca(100 * self.acertos_consecutivos)
                            self.popup = PopupRecompensa(acertou=True)
                        else:
                            self.acertos_consecutivos = 0
                            self.popup = PopupRecompensa(acertou=False)
                        
                        # Marca para regenerar quando popup fechar
                        self.regenerar_na_proxima = True
                        break
            
            if ev.type == pygame.MOUSEBUTTONDOWN and self.fase_completa and not self.fase_concluida:
                self.estado["tela_atual"] = "mapa"

    def update(self):
        self.tick += 1
        self.carro.update()
        
        if self.popup:
            self.popup.update()
            # Se popup terminou e precisa regenerar
            if self.popup.finalizado() and self.regenerar_na_proxima:
                self.problema.regenera()
                self._create_answer_buttons()
                self.regenerar_na_proxima = False
                self.popup = None

        self._verificar_conclusao()

    def _verificar_conclusao(self):
        """Abre o popup de fase concluída só depois que o personagem terminou
        a animação e o popup de acerto sumiu (antes ficava faltando um acerto)."""
        if self.popup is None and not self.fase_completa and self.carro.chegou():
            self.fase_completa = True
            self.fase_concluida = PopupFaseConcluida(self.W, self.H, self.estado)

    def draw(self):
        # Fundo
        pygame.draw.rect(self.surf, SKY_COLOR, (0, 0, self.W, PISTA_Y))
        pygame.draw.rect(self.surf, GRASS_COLOR, (0, PISTA_Y, self.W, self.H - PISTA_Y))
        
        # Pista com marcações
        pygame.draw.rect(self.surf, (100, 100, 100), (0, PISTA_Y, self.W, 60))
        for x in range(0, self.W, 50):
            pygame.draw.line(self.surf, (255, 255, 255), (x, PISTA_Y + 28), (x + 30, PISTA_Y + 28), 3)
        
        # Linha de chegada
        for i in range(0, 60, 10):
            pygame.draw.rect(self.surf, LEGO_RED, (FINISH_X, PISTA_Y + i, 20, 10))
            pygame.draw.rect(self.surf, LEGO_WHITE, (FINISH_X + 20, PISTA_Y + i, 20, 10))
        
        # Bandeira de chegada
        pygame.draw.polygon(self.surf, LEGO_YELLOW, [
            (FINISH_X - 5, PISTA_Y - 60),
            (FINISH_X + 50, PISTA_Y - 40),
            (FINISH_X - 5, PISTA_Y - 20),
        ])
        pygame.draw.line(self.surf, LEGO_DARK, (FINISH_X - 5, PISTA_Y - 60), (FINISH_X - 5, PISTA_Y + 60), 4)
        
        # Carrinho
        self.carro.draw(self.surf, self.font_big)
        
        # Painel superior com problema - maior
        panel_h = 160
        pygame.draw.rect(self.surf, (40, 60, 100), (0, 0, self.W, panel_h))
        pygame.draw.rect(self.surf, LEGO_BLUE, (0, 0, self.W, panel_h), 5)
        
        # Pergunta grande e clara
        prob_txt = self.font_huge.render(self.problema.texto, True, LEGO_YELLOW)
        self.surf.blit(prob_txt, (self.W // 2 - prob_txt.get_width() // 2, 15))
        
        # "Quanto é?" em cima
        quanto_txt = self.font_med.render("Quanto é?", True, LEGO_WHITE)
        self.surf.blit(quanto_txt, (self.W // 2 - quanto_txt.get_width() // 2, 95))
        
        # Pontos na lateral
        pts_txt = self.font_small.render(f"Pontos: {self.pontos}", True, LEGO_WHITE)
        self.surf.blit(pts_txt, (20, 120))
        
        # Botões de resposta
        for botao in self.botoes_resposta:
            # Cor baseado em hover
            cor = botao["cor"] if not botao["hover"] else tuple(min(255, c + 40) for c in botao["cor"])
            cor_borda = tuple(max(0, c - 50) for c in cor)
            
            # Sombra
            shadow = pygame.Surface((botao["rect"].width + 6, botao["rect"].height + 6), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 60), (3, 3, botao["rect"].width, botao["rect"].height), border_radius=10)
            self.surf.blit(shadow, (botao["rect"].x - 2, botao["rect"].y + 2))
            
            # Botão
            pygame.draw.rect(self.surf, cor, botao["rect"], border_radius=10)
            pygame.draw.rect(self.surf, cor_borda, botao["rect"], 3, border_radius=10)
            
            # Studs LEGO
            pygame.draw.circle(self.surf, cor_borda, (botao["rect"].centerx - 20, botao["rect"].y + 10), 6)
            pygame.draw.circle(self.surf, cor_borda, (botao["rect"].centerx + 20, botao["rect"].y + 10), 6)
            
            # Número
            num_txt = self.font_big.render(str(botao["resposta"]), True, LEGO_WHITE)
            self.surf.blit(num_txt, (botao["rect"].centerx - num_txt.get_width() // 2,
                                     botao["rect"].centery - num_txt.get_height() // 2))
        
        # Popup se houver
        if self.popup:
            self.popup.draw(self.surf, self.font_big)
        
        # Tela de vitória
        if self.fase_completa and not self.fase_concluida:
            overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.surf.blit(overlay, (0, 0))
            
            # Caixa de vitória
            box_w, box_h = 500, 250
            bx, by = self.W // 2 - box_w // 2, self.H // 2 - box_h // 2 - 50
            
            pygame.draw.rect(self.surf, LEGO_GREEN, (bx, by, box_w, box_h), border_radius=20)
            pygame.draw.rect(self.surf, (50, 140, 50), (bx, by, box_w, box_h), 5, border_radius=20)
            
            # Studs
            for sx in range(bx + 40, bx + box_w - 20, 80):
                pygame.draw.circle(self.surf, (50, 140, 50), (sx, by + 20), 10)
            
            # Textos
            vitoria_txt = self.font_big.render(" VOCÊ VENCEU! ", True, LEGO_WHITE)
            self.surf.blit(vitoria_txt, (bx + box_w // 2 - vitoria_txt.get_width() // 2, by + 40))
            
            pontos_txt = self.font_med.render(f"Pontos: {self.pontos}", True, LEGO_YELLOW)
            self.surf.blit(pontos_txt, (bx + box_w // 2 - pontos_txt.get_width() // 2, by + 120))
            
            clique_txt = self.font_small.render("Clique para voltar ao mapa", True, LEGO_WHITE)
            self.surf.blit(clique_txt, (bx + box_w // 2 - clique_txt.get_width() // 2, by + 180))
        
        # Botão voltar
        self.btn_voltar.draw(self.surf)

        if self.fase_concluida:
            self.fase_concluida.draw(self.surf)
        
        # Hint ESC
        esc_txt = self.font_small.render("ESC = voltar ao mapa", True, (100, 120, 150))
        self.surf.blit(esc_txt, (self.W - esc_txt.get_width() - 16, self.H - 28))
