import pygame
from ui_components import (
    draw_lego_brick, draw_panel, draw_sky_background,
    draw_grass_strip, LegoButton, InputField, Checkbox,
    RadioGroup, VirtualKeyboard
)
from firebase_auth import cadastrar


COR_ETAPA = [(220, 38, 38), (37, 99, 235)]


def _remover_emoji(texto):
    """Remove caracteres fora do plano BMP (emojis e símbolos especiais)."""
    return "".join(c for c in texto if ord(c) < 0x10000 and (
        c.isalnum() or c in " .,!?@#$%&*()-_+=/:;'\"\\|<>[]{}~^`\n\t"
        or ord(c) < 256
    ))


class CadastroScreen:
    def __init__(self, surf, largura, altura, cores, estado):
        self.surf = surf
        self.W = largura
        self.H = altura
        self.cores = cores
        self.estado = estado
        self.tick = 0
        self.etapa = 0
        self.msg_erro = ""
        self.scroll_y = 0

        self.f_titulo  = pygame.font.SysFont("Impact", 40, bold=True)
        self.f_secao   = pygame.font.SysFont("Impact", 22)
        self.f_label   = pygame.font.SysFont("Arial", 14, bold=True)
        self.f_normal  = pygame.font.SysFont("Arial", 16)
        self.f_btn     = pygame.font.SysFont("Impact", 20)
        self.f_erro    = pygame.font.SysFont("Arial", 13, bold=True)

        self._build_etapa0()
        self._build_etapa1()

        # ── Teclado responsivo ──────────────────────────────────────────────
        margin = 6
        kb_w = self.W - margin * 2
        kb_h = int(self.H * 0.46)
        kb_y = self.H - kb_h - margin
        self.teclado = VirtualKeyboard(margin, kb_y, kb_w, kb_h)
        self._kb_margin = margin
        self._kb_h = kb_h
        # ────────────────────────────────────────────────────────────────────

    # ──────────────────────────────────────────────────────────────────────────
    def _build_etapa0(self):
        W = self.W
        lx, ly = 40, 90
        rx, ry = W // 2 + 20, 90
        iw = W // 2 - 70

        self.inp_nome_resp  = InputField(lx, ly+50,  iw, 38, "Nome completo",                fonte=self.f_normal)
        self.inp_email      = InputField(lx, ly+120, iw, 38, "Email",                         fonte=self.f_normal)
        self.inp_senha      = InputField(lx, ly+190, iw, 38, "Senha",      senha=True,        fonte=self.f_normal)
        self.inp_conf_senha = InputField(lx, ly+260, iw, 38, "Confirmar senha", senha=True,   fonte=self.f_normal)
        self.inp_telefone   = InputField(lx, ly+330, iw, 38, "Telefone/WhatsApp (opcional)",  fonte=self.f_normal)
        self.inp_cidade     = InputField(lx, ly+400, iw//2-4, 38, "Cidade",                   fonte=self.f_normal)
        self.inp_estado     = InputField(lx + iw//2+4, ly+400, iw//2-4, 38, "UF",            fonte=self.f_normal)

        self.chk_termos      = Checkbox(lx, ly+455, "Aceito os Termos de Uso",          self.f_normal)
        self.chk_privacidade = Checkbox(lx, ly+485, "Aceito a Política de Privacidade", self.f_normal)
        self.chk_dados       = Checkbox(lx, ly+515, "Consinto dados da criança",        self.f_normal)

        self.inp_nome_cri = InputField(rx, ry+50,  iw, 38, "Nome da crianca",  fonte=self.f_normal)
        self.inp_apelido  = InputField(rx, ry+120, iw, 38, "Apelido no jogo",  fonte=self.f_normal)
        self.inp_nasc     = InputField(rx, ry+190, iw//2-4, 38, "DD/MM/AAAA",  fonte=self.f_normal)
        self.radio_sexo   = RadioGroup(rx + iw//2+4, ry+190,
                                       ["Menino", "Menina"],
                                       self.f_normal, espacamento=26)
        self.radio_serie  = RadioGroup(rx, ry+310,
                                       ["Pré I", "Pré II", "Jardim", "1 ano"],
                                       self.f_normal, espacamento=26)
        self.inp_escola   = InputField(rx, ry+435, iw, 38, "Escola (opcional)", fonte=self.f_normal)

        bw = 200
        self.btn_proximo      = LegoButton(W//2-bw//2, self.H-58, bw, 44,
                                           "PRÓXIMO", self.cores["verde"], self.f_btn, studs=0)
        self.btn_voltar_login = LegoButton(20, self.H-58, 160, 44,
                                           "LOGIN", self.cores["cinza_med"], self.f_btn, studs=0)

        self._inputs_etapa0 = [
            self.inp_nome_resp, self.inp_email, self.inp_senha, self.inp_conf_senha,
            self.inp_telefone, self.inp_cidade, self.inp_estado,
            self.inp_nome_cri, self.inp_apelido, self.inp_nasc, self.inp_escola,
        ]
        self._checks_etapa0 = [self.chk_termos, self.chk_privacidade, self.chk_dados]
        self._radios_etapa0 = [self.radio_sexo, self.radio_serie]

    # ──────────────────────────────────────────────────────────────────────────
    def _build_etapa1(self):
        x = self.W // 2 - 300
        y0 = 110

        self.radio_nivel = RadioGroup(x, y0, [
            "Ainda não reconhece letras",
            "Reconhece letras",
            "Reconhece sílabas",
            "Lê palavras simples",
            "Lê frases simples",
        ], self.f_normal, espacamento=30)

        difs = [
            "Troca letras", "Dificuldade com sílabas",
            "Dificuldade de atenção", "Dificuldade para escrever",
            "Coordenção motora", "Timidez", "Nenhuma percebida",
        ]
        dy = y0 + 200
        self.chks_dific = [Checkbox(x, dy + i*30, d, self.f_normal) for i, d in enumerate(difs)]

        oy = dy + len(difs)*30 + 20
        self.radio_objetivo = RadioGroup(x, oy, [
            "Aprender o alfabeto",
            "Melhorar leitura",
            "Melhorar escrita",
            "Melhorar coordenação",
            "Preparação escolar",
        ], self.f_normal, espacamento=30)

        self._altura_conteudo1 = oy + 6*30 + 60

        bw = 220
        cx = self.W // 2
        self.btn_cadastrar    = LegoButton(cx - bw - 10, self.H-58, bw, 44,
                                           "CADASTRAR", self.cores["verde"], self.f_btn, studs=0)
        self.btn_voltar_etapa = LegoButton(cx + 10, self.H-58, bw, 44,
                                           "VOLTAR", self.cores["cinza_med"], self.f_btn, studs=0)

    # ──────────────────────────────────────────────────────────────────────────
    def _sanitizar_inputs(self):
        """Remove emojis e caracteres inválidos de todos os campos de texto."""
        for inp in self._inputs_etapa0:
            inp.texto = _remover_emoji(inp.texto)

    def handle_events(self, eventos):
        for ev in eventos:
            campo_ativo = self._campo_ativo()
            self._posicionar_teclado(campo_ativo)
            if self.teclado.handle_event(ev, campo_ativo):
                # Sanitiza após cada tecla do teclado virtual
                self._sanitizar_inputs()
                continue

            if ev.type == pygame.MOUSEWHEEL and self.etapa == 1:
                self.scroll_y = max(0, min(
                    self.scroll_y - ev.y * 20,
                    max(0, self._altura_conteudo1 - self.H + 120)
                ))

            if self.etapa == 0:
                for inp in self._inputs_etapa0:
                    inp.handle_event(ev)
                # Sanitiza após evento de teclado físico também
                if ev.type == pygame.KEYDOWN:
                    self._sanitizar_inputs()

                campo_ativo = self._campo_ativo()
                self._posicionar_teclado(campo_ativo)
                self.teclado.visible = campo_ativo is not None

                for chk in self._checks_etapa0:
                    chk.handle_event(ev)
                for rad in self._radios_etapa0:
                    rad.handle_event(ev)

                if self.btn_proximo.handle_event(ev):
                    self._validar_etapa0()
                if self.btn_voltar_login.handle_event(ev):
                    self.teclado.visible = False
                    self.estado["tela_atual"] = "login"
            else:
                self.teclado.visible = False
                ev_scroll = self._ev_com_scroll(ev)
                self.radio_nivel.handle_event(ev_scroll)
                for chk in self.chks_dific:
                    chk.handle_event(ev_scroll)
                self.radio_objetivo.handle_event(ev_scroll)

                if self.btn_cadastrar.handle_event(ev):
                    self._fazer_cadastro()
                if self.btn_voltar_etapa.handle_event(ev):
                    self.etapa = 0

    def _campo_ativo(self):
        if self.etapa != 0:
            return None
        for inp in self._inputs_etapa0:
            if inp.ativo:
                return inp
        return None

    def _posicionar_teclado(self, campo):
        if campo is None:
            return
        margin = self._kb_margin
        kb_h   = self._kb_h
        # Se o campo está na metade inferior, sobe o teclado para a metade superior
        if campo.rect.centery > self.H // 2:
            kb_y = margin
        else:
            kb_y = self.H - kb_h - margin
        self.teclado.move_to(margin, kb_y)

    def _ev_com_scroll(self, ev):
        if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            pos = (ev.pos[0], ev.pos[1] + self.scroll_y)
            class FakeEv:
                pass
            fe = FakeEv()
            fe.type = ev.type
            fe.pos = pos
            if hasattr(ev, "button"):
                fe.button = ev.button
            return fe
        if ev.type == pygame.FINGERDOWN:
            surf = pygame.display.get_surface()
            w = surf.get_width()  if surf else self.W
            h = surf.get_height() if surf else self.H
            class FakeFingerEv:
                pass
            fe = FakeFingerEv()
            fe.type = pygame.FINGERDOWN
            # Reemite como MOUSEBUTTONDOWN com pos ajustada pelo scroll
            fe.type = pygame.MOUSEBUTTONDOWN
            fe.button = 1
            fe.pos = (int(ev.x * w), int(ev.y * h) + self.scroll_y)
            return fe
        return ev

    # ──────────────────────────────────────────────────────────────────────────
    def _validar_etapa0(self):
        self.msg_erro = ""
        campos = [
            (self.inp_nome_resp,  "Nome do responsável"),
            (self.inp_email,      "E-mail"),
            (self.inp_senha,      "Senha"),
            (self.inp_conf_senha, "Confirmação de senha"),
            (self.inp_nome_cri,   "Nome da crianca"),
            (self.inp_apelido,    "Apelido no jogo"),
            (self.inp_nasc,       "Data de nascimento"),
        ]
        for inp, nome in campos:
            inp.erro = False
            if not inp.texto.strip():
                inp.erro = True
                self.msg_erro = f"Campo obrigatório: {nome}"
                return

        if self.inp_senha.texto != self.inp_conf_senha.texto:
            self.inp_senha.erro = True
            self.inp_conf_senha.erro = True
            self.msg_erro = "As senhas não coincidem!"
            return

        if len(self.inp_senha.texto) < 6:
            self.inp_senha.erro = True
            self.msg_erro = "Senha deve ter pelo menos 6 caracteres!"
            return

        if not self.chk_termos.marcado:
            self.msg_erro = "Aceite os Termos de Uso para continuar!"
            return
        if not self.chk_privacidade.marcado:
            self.msg_erro = "Aceite a Política de Privacidade para continuar!"
            return
        if not self.chk_dados.marcado:
            self.msg_erro = "Consinta o uso dos dados da criança para continuar!"
            return

        self.etapa = 1
        self.scroll_y = 0
        self.teclado.visible = False

    def _fazer_cadastro(self):
        self.msg_erro = ""
        dados = {
            "nome_responsavel":     self.inp_nome_resp.texto.strip(),
            "email":                self.inp_email.texto.strip(),
            "senha":                self.inp_senha.texto,
            "telefone":             self.inp_telefone.texto.strip(),
            "cidade":               self.inp_cidade.texto.strip(),
            "estado":               self.inp_estado.texto.strip(),
            "aceite_termos":        self.chk_termos.marcado,
            "aceite_privacidade":   self.chk_privacidade.marcado,
            "aceite_dados_crianca": self.chk_dados.marcado,
            "nome_crianca":         self.inp_nome_cri.texto.strip(),
            "apelido":              self.inp_apelido.texto.strip(),
            "data_nascimento":      self.inp_nasc.texto.strip(),
            "sexo":                 self.radio_sexo.valor,
            "serie_escolar":        self.radio_serie.valor,
            "escola":               self.inp_escola.texto.strip(),
            "nivel_leitura":        self.radio_nivel.valor,
            "dificuldades":         [c.texto for c in self.chks_dific if c.marcado],
            "objetivo":             self.radio_objetivo.valor,
        }
        resultado = cadastrar(dados)
        if resultado["ok"]:
            self.estado["usuario"] = resultado
            self.estado["tela_atual"] = "perfil"
        else:
            self.msg_erro = resultado["erro"]

    # ──────────────────────────────────────────────────────────────────────────
    def update(self):
        self.tick += 1

    def draw(self):
        draw_sky_background(self.surf, self.W, self.H, self.tick)
        draw_grass_strip(self.surf, self.W, self.H)

        if self.etapa == 0:
            self._draw_etapa0()
        else:
            self._draw_etapa1()

        self._draw_progresso()

        if self.msg_erro:
            err = self.f_erro.render(f"  {self.msg_erro}", True, (255, 100, 100))
            pygame.draw.rect(self.surf, (60, 10, 10),
                             (self.W//2 - err.get_width()//2 - 8,
                              self.H-90, err.get_width()+16, 24), border_radius=6)
            self.surf.blit(err, err.get_rect(centerx=self.W//2, top=self.H-88))

        self.teclado.draw(self.surf)

    # ──────────────────────────────────────────────────────────────────────────
    def _draw_etapa0(self):
        W, H = self.W, self.H
        lx, ly = 40, 90
        rx, ry = W//2+20, 90
        iw = W//2-70

        draw_panel(self.surf, (lx-10, ly-36, iw+20, H-100))
        draw_panel(self.surf, (rx-10, ry-36, iw+20, H-100))

        self._secao("RESPONSÁVEL", lx, ly-28, self.cores["vermelho"])
        self._label("Nome completo *",    lx, ly+32)
        self._label("E-mail *",           lx, ly+102)
        self._label("Senha *",            lx, ly+172)
        self._label("Confirmar Senha *",  lx, ly+242)
        self._label("Telefone/WhatsApp",  lx, ly+312)
        self._label("Cidade / UF",        lx, ly+382)

        for inp in [self.inp_nome_resp, self.inp_email, self.inp_senha,
                    self.inp_conf_senha, self.inp_telefone,
                    self.inp_cidade, self.inp_estado]:
            inp.draw(self.surf)

        for chk in self._checks_etapa0:
            chk.draw(self.surf)

        self._secao("CRIANÇA", rx, ry-28, self.cores["azul"])
        self._label("Nome da criança *",    rx, ry+32)
        self._label("Apelido no jogo *",    rx, ry+102)
        self._label("Data de nascimento *", rx, ry+172)
        self._label("Sexo (opcional)",      rx + iw//2+4, ry+172)
        self._label("Série escolar",        rx, ry+293)
        self._label("Nome da escola",       rx, ry+418)

        for inp in [self.inp_nome_cri, self.inp_apelido, self.inp_nasc, self.inp_escola]:
            inp.draw(self.surf)
        self.radio_sexo.draw(self.surf)
        self.radio_serie.draw(self.surf)

        self.btn_proximo.draw(self.surf)
        self.btn_voltar_login.draw(self.surf)

    # ──────────────────────────────────────────────────────────────────────────
    def _draw_etapa1(self):
        W, H = self.W, self.H
        area_clip = pygame.Rect(0, 70, W, H-130)
        self.surf.set_clip(area_clip)

        offset = self.scroll_y
        x = W//2 - 300
        y0 = 110 - offset

        draw_panel(self.surf, (x-20, y0-40, 640, self._altura_conteudo1))

        self._secao("PERFIL DE APRENDIZAGEM", x, y0-32, self.cores["laranja"])

        niv_y = y0
        self._label("Nível de leitura atual:", x, niv_y-18)
        for i, r in enumerate(self.radio_nivel.rects):
            r.x = x
            r.y = niv_y + i*30
        self.radio_nivel.draw(self.surf)

        difs_base = 110 + 200
        for i, chk in enumerate(self.chks_dific):
            chk.x = x
            chk.y = difs_base + i*30 - offset
            chk.rect = pygame.Rect(chk.x, chk.y, 22, 22)
        lbl_dif = self.f_label.render("Dificuldades percebidas:", True, (160, 180, 220))
        self.surf.blit(lbl_dif, (x, difs_base - offset - 18))
        for chk in self.chks_dific:
            chk.draw(self.surf)

        obj_base = difs_base + len(self.chks_dific)*30 + 20
        for i, r in enumerate(self.radio_objetivo.rects):
            r.x = x
            r.y = obj_base + i*30 - offset
        lbl_obj = self.f_label.render("Objetivo principal:", True, (160, 180, 220))
        self.surf.blit(lbl_obj, (x, obj_base - offset - 18))
        self.radio_objetivo.draw(self.surf)

        self.surf.set_clip(None)

        total = max(1, self._altura_conteudo1 - H + 130)
        pct = self.scroll_y / total
        bh = max(40, (H-130) * (H-130) // self._altura_conteudo1)
        by = 70 + int(pct * (H-130-bh))
        pygame.draw.rect(self.surf, (60, 60, 80),   (W-12, 70, 8, H-130), border_radius=4)
        pygame.draw.rect(self.surf, (100, 150, 255), (W-12, by, 8, bh),   border_radius=4)

        self.btn_cadastrar.draw(self.surf)
        self.btn_voltar_etapa.draw(self.surf)

    # ──────────────────────────────────────────────────────────────────────────
    def _secao(self, texto, x, y, cor):
        txt = self.f_secao.render(texto, True, cor)
        self.surf.blit(txt, (x, y))

    def _label(self, texto, x, y):
        txt = self.f_label.render(texto, True, (140, 160, 200))
        self.surf.blit(txt, (x, y))

    def _draw_progresso(self):
        total = 2
        bw = 180
        gap = 10
        total_w = total * bw + (total-1)*gap
        sx = self.W//2 - total_w//2
        labels = ["Responsável e Criança", "Aprendizagem"]
        cores_prog = [self.cores["vermelho"], self.cores["azul"]]
        for i in range(total):
            cor = cores_prog[i] if i <= self.etapa else (60, 60, 75)
            x = sx + i*(bw+gap)
            draw_lego_brick(self.surf, cor, (x, 8, bw, 28), studs=0, raio_borda=6)
            lbl = self.f_label.render(labels[i], True, (255, 255, 255))
            self.surf.blit(lbl, lbl.get_rect(centerx=x+bw//2, centery=22))