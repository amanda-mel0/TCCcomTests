import pygame
from ui_components import (
    draw_lego_brick, draw_panel, draw_sky_background,
    draw_grass_strip, LegoButton, InputField, VirtualKeyboard
)
from firebase_auth import login


class LoginScreen:
    def __init__(self, surf, largura, altura, cores, estado):
        self.surf = surf
        self.W = largura
        self.H = altura
        self.cores = cores
        self.estado = estado
        self.tick = 0
        self.msg_erro = ""
        self.carregando = False

        # Fontes
        self.fonte_titulo  = pygame.font.SysFont("Constantia", 45, bold=True)
        self.fonte_sub     = pygame.font.SysFont("Arial", 16, bold=True)
        self.fonte_label   = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.fonte_btn     = pygame.font.SysFont("Arial", 20, bold=True)
        self.fonte_link    = pygame.font.SysFont("Arial", 20, bold=True)
        self.fonte_erro    = pygame.font.SysFont("Arial", 20, bold=True)

        # Painel central
        pw, ph = 420, 430
        px = self.W // 2 - pw // 2
        py = self.H // 2 - ph // 2

        # Inputs
        iw = 340
        ix = self.W // 2 - iw // 2
        self.inp_email = InputField(ix, py+145, iw, 42, "seu@email.com", fonte=self.fonte_sub)
        self.inp_senha = InputField(ix, py+230, iw, 42, "Senha", senha=True, fonte=self.fonte_sub)

        # Botões
        bw = 340
        bx = self.W // 2 - bw // 2
        self.btn_entrar   = LegoButton(bx, py+300, bw, 48, "Entrar", cores["verde"], self.fonte_btn, studs=0)
        self.btn_cadastro = LegoButton(bx, py+362, bw, 40, "Criar conta", cores["azul"], self.fonte_btn, studs=0)

        # ── Teclado responsivo ──────────────────────────────────────────────
        # Largura: tela inteira menos margem lateral
        # Altura: 46% da tela — equilibra teclas confortáveis em 480p e 768p
        # Posição y: calculada para encostar na borda inferior
        margin = 6
        kb_w = self.W - margin * 2
        kb_h = int(self.H * 0.46)
        kb_y = self.H - kb_h - margin
        self.teclado = VirtualKeyboard(margin, kb_y, kb_w, kb_h)
        # ────────────────────────────────────────────────────────────────────

        self.py = py
        self.pw = pw
        self.ph = ph
        self.px = px

        # Tijolos decorativos (posição, cor, largura)
        self.tijolos_deco = [
            (30,  80,  120, cores["vermelho"]),
            (900, 120, 100, cores["amarelo"]),
            (50,  580, 90,  cores["azul"]),
            (940, 560, 110, cores["verde"]),
            (200, 30,  80,  cores["laranja"]),
            (780, 40,  90,  cores["roxo"]),
        ]

    def handle_events(self, eventos):
        for ev in eventos:
            campo_ativo = self._campo_ativo()
            if self.teclado.handle_event(ev, campo_ativo):
                continue

            self.inp_email.handle_event(ev)
            self.inp_senha.handle_event(ev)
            self.teclado.visible = self._campo_ativo() is not None

            if self.btn_entrar.handle_event(ev):
                self._fazer_login()

            if self.btn_cadastro.handle_event(ev):
                self.estado["tela_atual"] = "cadastro"

    def _campo_ativo(self):
        if self.inp_email.ativo:
            return self.inp_email
        if self.inp_senha.ativo:
            return self.inp_senha
        return None

    def _fazer_login(self):
        self.msg_erro = ""
        email = self.inp_email.texto.strip()
        senha = self.inp_senha.texto.strip()

        if not email or not senha:
            self.msg_erro = "Preencha e-mail e senha!"
            return

        self.carregando = True
        resultado = login(email, senha)
        self.carregando = False

        if resultado["ok"]:
            self.estado["usuario"] = resultado
            self.estado["usuario"]["avatar"] = self.estado.get("avatar_escolhido", "masculino")
            self.estado["tela_atual"] = "perfil"
        else:
            self.msg_erro = resultado["erro"]
            self.inp_email.erro = True
            self.inp_senha.erro = True

    def update(self):
        self.tick += 1

    def draw(self):
        draw_sky_background(self.surf, self.W, self.H, self.tick)
        draw_grass_strip(self.surf, self.W, self.H)

        for (x, y, w, cor) in self.tijolos_deco:
            draw_lego_brick(self.surf, cor, (x, y, w, 44), studs=2)

        draw_panel(self.surf, (self.px, self.py, self.pw, self.ph), alfa=230)

        titulo = self.fonte_titulo.render("LER", True, self.cores["amarelo"])
        titulo2 = self.fonte_titulo.render("BRINCANDO", True, self.cores["vermelho"])
        self.surf.blit(titulo,  titulo.get_rect(centerx=self.W//2, top=self.py+18))
        self.surf.blit(titulo2, titulo2.get_rect(centerx=self.W//2, top=self.py+72))

        lbl_e = self.fonte_label.render("Email", True, (50,170,210))
        lbl_s = self.fonte_label.render("Senha", True, (50,170,210))
        self.surf.blit(lbl_e, (self.inp_email.rect.x, self.inp_email.rect.y - 30))
        self.surf.blit(lbl_s, (self.inp_senha.rect.x, self.inp_senha.rect.y - 30))

        self.inp_email.draw(self.surf)
        self.inp_senha.draw(self.surf)

        if self.msg_erro:
            err = self.fonte_erro.render(f"Aviso: {self.msg_erro}", True, (255, 100, 100))
            self.surf.blit(err, err.get_rect(centerx=self.W//2, top=self.py+285))

        if self.carregando:
            pts = "..." if (self.tick // 20) % 2 == 0 else ".. "
            load = self.fonte_sub.render(f"Conectando{pts}", True, (200,200,100))
            self.surf.blit(load, load.get_rect(centerx=self.W//2, top=self.py+285))

        self.btn_entrar.draw(self.surf)
        self.btn_cadastro.draw(self.surf)

        for i in range(5):
            cor = [self.cores["vermelho"], self.cores["amarelo"],
                   self.cores["azul"], self.cores["verde"], self.cores["laranja"]][i]
            draw_lego_brick(self.surf, cor,
                            (self.px + i * (self.pw//5), self.py - 18, self.pw//5 - 2, 20),
                            studs=1, raio_borda=4)

        self.teclado.draw(self.surf)