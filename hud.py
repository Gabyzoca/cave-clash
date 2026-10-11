import pygame
import math


# ============================================================
# CORES
# ============================================================

COR_FUNDO_BARRA = (30, 30, 36)
COR_BORDA = (210, 200, 170)
COR_TEXTO = (240, 240, 240)
COR_TEXTO_SOMBRA = (10, 10, 10)

COR_VIDA_ALTA = (90, 200, 90)
COR_VIDA_MEDIA = (230, 200, 60)
COR_VIDA_BAIXA = (220, 60, 60)

COR_PAINEL = (18, 18, 24, 170)

# ============================================================
# LAYOUT DO TOPO (todos os painéis usam os mesmos valores)
# ============================================================

MARGEM = 24
TOPO_PAINEL = 20
ALTURA_PAINEL = 72

LARGURA_PAINEL_LATERAL = 320
LARGURA_PAINEL_CENTRO = 240

DURACAO_POPUP = 1.0

HABILIDADES = [
    ("SPACE", "Ataque 1", "attack_1"),
    ("E", "Ataque 2", "attack_2"),
    ("H", "Cura", "heal")
]


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def interpolar_cor(cor_a, cor_b, t):

    t = max(0, min(1, t))

    return (
        int(cor_a[0] + (cor_b[0] - cor_a[0]) * t),
        int(cor_a[1] + (cor_b[1] - cor_a[1]) * t),
        int(cor_a[2] + (cor_b[2] - cor_a[2]) * t)
    )


def cor_da_vida(porcentagem):

    if porcentagem > 0.5:

        t = (1 - porcentagem) / 0.5

        return interpolar_cor(
            COR_VIDA_ALTA,
            COR_VIDA_MEDIA,
            t
        )

    else:

        t = (0.5 - porcentagem) / 0.5

        return interpolar_cor(
            COR_VIDA_MEDIA,
            COR_VIDA_BAIXA,
            t
        )


def desenhar_texto_com_sombra(
    screen,
    fonte,
    texto,
    x,
    y,
    cor=COR_TEXTO,
    centrado=False
):

    sombra = fonte.render(texto, True, COR_TEXTO_SOMBRA)
    principal = fonte.render(texto, True, cor)

    if centrado:

        rect = principal.get_rect(center=(x, y))

        screen.blit(sombra, (rect.x + 2, rect.y + 2))
        screen.blit(principal, rect)

    else:

        screen.blit(sombra, (x + 2, y + 2))
        screen.blit(principal, (x, y))


def desenhar_painel(
    screen,
    rect,
    cor=COR_PAINEL,
    borda=COR_BORDA,
    raio=10
):

    superficie = pygame.Surface(
        (rect.width, rect.height),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        superficie,
        cor,
        superficie.get_rect(),
        border_radius=raio
    )

    screen.blit(superficie, rect.topleft)

    pygame.draw.rect(
        screen,
        borda,
        rect,
        width=2,
        border_radius=raio
    )


# ============================================================
# CLASSE HUD
# ============================================================

class HUD:

    def __init__(self, largura, altura):

        self.largura = largura
        self.altura = altura

        if not pygame.font.get_init():

            pygame.font.init()

        self.fonte_pequena = pygame.font.Font(None, 22)
        self.fonte_media = pygame.font.Font(None, 30)
        self.fonte_grande = pygame.font.Font(None, 68)
        self.fonte_popup = pygame.font.Font(None, 34)

        # Vida exibida (persegue a vida real suavemente)
        self.vida_exibida = None
        self.vida_anterior = None

        self.tempo = 0

        self.flash_dano = 0

        self.fade_fim = 0

        # Pontuação
        self.pontuacao = 0
        self.pontuacao_exibida = 0

        # Textos flutuantes "+100"
        self.popups = []

    # ========================================================
    # ATUALIZAR
    # ========================================================

    def atualizar(self, dt, player, ondas):

        self.tempo += dt

        # ---------------- Vida ----------------

        if self.vida_exibida is None:

            self.vida_exibida = player.vida
            self.vida_anterior = player.vida

        if player.vida < self.vida_anterior:

            self.flash_dano = 0.35

        self.vida_anterior = player.vida

        diferenca = player.vida - self.vida_exibida

        self.vida_exibida += diferenca * min(1, dt * 6)

        if abs(diferenca) < 0.5:

            self.vida_exibida = player.vida

        if self.flash_dano > 0:

            self.flash_dano = max(0, self.flash_dano - dt)

        # ---------------- Pontuação ----------------

        self.contabilizar_pontos(ondas)

        diferenca_pontos = self.pontuacao - self.pontuacao_exibida

        self.pontuacao_exibida += diferenca_pontos * min(1, dt * 8)

        if abs(diferenca_pontos) < 1:

            self.pontuacao_exibida = self.pontuacao

        # ---------------- Popups ----------------

        for popup in self.popups:

            popup["tempo"] += dt

        self.popups = [
            popup
            for popup in self.popups
            if popup["tempo"] < DURACAO_POPUP
        ]

    # ========================================================
    # PONTUAÇÃO: identifica inimigos derrotados
    # ========================================================

    def contabilizar_pontos(self, ondas):

        for inimigo in ondas.inimigos:

            if inimigo.vida <= 0 and not inimigo.pontuado:

                inimigo.pontuado = True

                self.pontuacao += inimigo.pontos

                self.popups.append({
                    "texto": f"+{inimigo.pontos}",
                    "x": inimigo.x,
                    "y": inimigo.y - 180,
                    "tempo": 0
                })

    # ========================================================
    # DESENHAR TUDO
    # ========================================================

    def desenhar(
        self,
        screen,
        player,
        combate,
        ondas,
        jogo_terminado
    ):

        self.desenhar_flash_dano(screen)

        self.desenhar_popups(screen)

        self.desenhar_vida(screen, player)

        self.desenhar_pontuacao(screen)

        self.desenhar_onda(screen, ondas)

        self.desenhar_habilidades(screen, player, combate)

        if jogo_terminado:

            self.desenhar_fim_de_jogo(screen, player, ondas)

        else:

            self.fade_fim = 0

    # ========================================================
    # FLASH VERMELHO AO RECEBER DANO
    # ========================================================

    def desenhar_flash_dano(self, screen):

        if self.flash_dano <= 0:

            return

        alpha = int(90 * (self.flash_dano / 0.35))

        superficie = pygame.Surface(
            (self.largura, self.altura),
            pygame.SRCALPHA
        )

        superficie.fill((200, 20, 20, alpha))

        screen.blit(superficie, (0, 0))

    # ========================================================
    # TEXTOS FLUTUANTES (+100)
    # ========================================================

    def desenhar_popups(self, screen):

        for popup in self.popups:

            t = popup["tempo"] / DURACAO_POPUP

            x = int(popup["x"])
            y = int(popup["y"] - 60 * t)

            alpha = int(255 * (1 - t))

            sombra = self.fonte_popup.render(
                popup["texto"],
                True,
                COR_TEXTO_SOMBRA
            )

            texto = self.fonte_popup.render(
                popup["texto"],
                True,
                (255, 220, 90)
            )

            sombra.set_alpha(alpha)
            texto.set_alpha(alpha)

            rect = texto.get_rect(center=(x, y))

            screen.blit(sombra, (rect.x + 2, rect.y + 2))
            screen.blit(texto, rect)

    # ========================================================
    # BARRA DE VIDA (painel esquerdo)
    # ========================================================

    def desenhar_vida(self, screen, player):

        rect_painel = pygame.Rect(
            MARGEM,
            TOPO_PAINEL,
            LARGURA_PAINEL_LATERAL,
            ALTURA_PAINEL
        )

        desenhar_painel(screen, rect_painel)

        desenhar_texto_com_sombra(
            screen,
            self.fonte_pequena,
            "HERÓI",
            rect_painel.centerx,
            rect_painel.y + 18,
            centrado=True
        )

        rect_fundo = pygame.Rect(
            rect_painel.x + 16,
            rect_painel.y + 34,
            rect_painel.width - 32,
            26
        )

        pygame.draw.rect(
            screen,
            COR_FUNDO_BARRA,
            rect_fundo,
            border_radius=6
        )

        porcentagem = max(
            0,
            min(1, self.vida_exibida / player.vida_maxima)
        )

        largura_vida = int(rect_fundo.width * porcentagem)

        if largura_vida > 0:

            cor = cor_da_vida(porcentagem)

            # Pulsa quando a vida está baixa
            if porcentagem < 0.3:
                pulso = (math.sin(self.tempo * 6) + 1) / 2

                cor = interpolar_cor(
                    cor,
                    (255, 255, 255),
                    pulso * 0.15
                )

            rect_vida = pygame.Rect(
                rect_fundo.x,
                rect_fundo.y,
                largura_vida,
                rect_fundo.height
            )

            pygame.draw.rect(
                screen,
                cor,
                rect_vida,
                border_radius=6
            )

        pygame.draw.rect(
            screen,
            COR_BORDA,
            rect_fundo,
            width=2,
            border_radius=6
        )

        texto_vida = (
            f"{max(0, int(round(player.vida)))}"
            f" / {player.vida_maxima}"
        )

        desenhar_texto_com_sombra(
            screen,
            self.fonte_pequena,
            texto_vida,
            rect_fundo.centerx,
            rect_fundo.centery,
            centrado=True
        )

    # ========================================================
    # PONTUAÇÃO (painel central)
    # ========================================================

    def desenhar_pontuacao(self, screen):

        rect_painel = pygame.Rect(
            0,
            TOPO_PAINEL,
            LARGURA_PAINEL_CENTRO,
            ALTURA_PAINEL
        )

        rect_painel.centerx = self.largura // 2

        desenhar_painel(screen, rect_painel)

        desenhar_texto_com_sombra(
            screen,
            self.fonte_pequena,
            "PONTOS",
            rect_painel.centerx,
            rect_painel.y + 18,
            centrado=True
        )

        desenhar_texto_com_sombra(
            screen,
            self.fonte_media,
            f"{int(round(self.pontuacao_exibida)):06d}",
            rect_painel.centerx,
            rect_painel.y + 46,
            cor=(255, 220, 90),
            centrado=True
        )

    # ========================================================
    # INDICADOR DE ONDA (painel direito)
    # ========================================================

    def desenhar_onda(self, screen, ondas):

        rect_painel = pygame.Rect(
            self.largura - MARGEM - LARGURA_PAINEL_LATERAL,
            TOPO_PAINEL,
            LARGURA_PAINEL_LATERAL,
            ALTURA_PAINEL
        )

        desenhar_painel(screen, rect_painel)

        if ondas.terminou:
            desenhar_texto_com_sombra(
                screen,
                self.fonte_pequena,
                "ONDA",
                rect_painel.centerx,
                rect_painel.y + 18,
                centrado=True
            )

            desenhar_texto_com_sombra(
                screen,
                self.fonte_media,
                "COMPLETA!",
                rect_painel.centerx,
                rect_painel.y + 46,
                cor=(120, 220, 140),
                centrado=True
            )

            return

        desenhar_texto_com_sombra(
            screen,
            self.fonte_pequena,
            f"ONDA {ondas.numero_onda} / {ondas.total_ondas}",
            rect_painel.centerx,
            rect_painel.y + 18,
            centrado=True
        )

        total = ondas.total_na_onda()
        derrotados = ondas.derrotados_na_onda()

        raio = 7
        espaco = 22

        x_inicial = (
                rect_painel.centerx
                - (total - 1) * espaco // 2
        )

        y_bolinhas = rect_painel.y + 46

        for i in range(total):

            centro = (x_inicial + i * espaco, y_bolinhas)

            if i < derrotados:

                cor = (90, 90, 100)

            else:

                cor = (220, 80, 80)

            pygame.draw.circle(screen, cor, centro, raio)

            pygame.draw.circle(
                screen,
                COR_BORDA,
                centro,
                raio,
                width=1
            )

    # ========================================================
    # INDICADORES DE HABILIDADES (com cooldown)
    # ========================================================

    def desenhar_habilidades(self, screen, player, combate):

        largura_icone = 78
        altura_icone = 58
        espaco = 12

        total_largura = (
            len(HABILIDADES) * largura_icone
            + (len(HABILIDADES) - 1) * espaco
        )

        x_inicial = self.largura // 2 - total_largura // 2
        y = self.altura - altura_icone - 22

        for i, (tecla, nome, habilidade) in enumerate(HABILIDADES):

            x = x_inicial + i * (largura_icone + espaco)

            rect = pygame.Rect(x, y, largura_icone, altura_icone)

            ativo = player.estado == habilidade

            fracao = combate.fracao_cooldown(habilidade)

            em_cooldown = fracao > 0

            cor_fundo = (60, 60, 90, 200) if ativo else (20, 20, 26, 170)

            desenhar_painel(
                screen,
                rect,
                cor=cor_fundo,
                borda=(230, 210, 120) if ativo else COR_BORDA,
                raio=8
            )

            # Película escura que "desce" conforme o cooldown acaba
            if em_cooldown:

                altura_cd = int((altura_icone - 4) * fracao)

                if altura_cd > 0:

                    pelicula = pygame.Surface(
                        (largura_icone - 4, altura_cd),
                        pygame.SRCALPHA
                    )

                    pelicula.fill((0, 0, 0, 150))

                    screen.blit(pelicula, (rect.x + 2, rect.y + 2))

            cor_texto = (140, 140, 140) if em_cooldown else COR_TEXTO

            desenhar_texto_com_sombra(
                screen,
                self.fonte_pequena,
                tecla,
                rect.centerx,
                rect.y + 16,
                cor=cor_texto,
                centrado=True
            )

            if em_cooldown:

                segundos = combate.cooldown_restante(habilidade)

                desenhar_texto_com_sombra(
                    screen,
                    self.fonte_pequena,
                    f"{segundos:.1f}s",
                    rect.centerx,
                    rect.y + 40,
                    cor=(255, 220, 90),
                    centrado=True
                )

            else:

                desenhar_texto_com_sombra(
                    screen,
                    self.fonte_pequena,
                    nome,
                    rect.centerx,
                    rect.y + 40,
                    centrado=True
                )

    # ========================================================
    # TELA DE FIM DE JOGO
    # ========================================================

    def desenhar_fim_de_jogo(self, screen, player, ondas):

        self.fade_fim = min(1, self.fade_fim + 0.02)

        superficie = pygame.Surface(
            (self.largura, self.altura),
            pygame.SRCALPHA
        )

        superficie.fill((0, 0, 0, int(170 * self.fade_fim)))

        screen.blit(superficie, (0, 0))

        venceu = ondas.terminou and player.vida > 0

        if venceu:

            texto = "VITÓRIA!"
            cor = (120, 220, 140)

        else:

            texto = "GAME OVER"
            cor = (220, 90, 90)

        pulso = (math.sin(self.tempo * 3) + 1) / 2

        cor_pulsante = interpolar_cor(
            cor,
            (255, 255, 255),
            pulso * 0.25
        )

        centro_x = self.largura // 2
        centro_y = self.altura // 2

        desenhar_texto_com_sombra(
            screen,
            self.fonte_grande,
            texto,
            centro_x,
            centro_y - 50,
            cor=cor_pulsante,
            centrado=True
        )

        desenhar_texto_com_sombra(
            screen,
            self.fonte_media,
            "Pontuação final",
            centro_x,
            centro_y + 10,
            centrado=True
        )

        desenhar_texto_com_sombra(
            screen,
            self.fonte_grande,
            f"{self.pontuacao}",
            centro_x,
            centro_y + 55,
            cor=(255, 220, 90),
            centrado=True
        )

        desenhar_texto_com_sombra(
            screen,
            self.fonte_pequena,
            "R - Jogar novamente   |   ESC - Sair",
            centro_x,
            centro_y + 110,
            centrado=True
        )