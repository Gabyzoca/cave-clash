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


def desenhar_painel(screen, rect, cor=COR_PAINEL, borda=COR_BORDA, raio=10):

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

        # Garante que o módulo de fontes do pygame já foi
        # inicializado, mesmo que o HUD seja criado antes
        # (ou sem) um pygame.init() completo.
        if not pygame.font.get_init():

            pygame.font.init()

        self.fonte_pequena = pygame.font.Font(None, 22)
        self.fonte_media = pygame.font.Font(None, 30)
        self.fonte_grande = pygame.font.Font(None, 68)

        # Vida exibida na tela, que persegue a realidade
        # suavemente (dá aquele efeito de barra "escorregando")
        self.vida_exibida = None

        # Tempo interno, usado para animações (pulsar, brilhar etc)
        self.tempo = 0

        # Flash vermelho quando o jogador toma dano
        self.flash_dano = 0

        self.vida_anterior = None

        # Fade da tela de fim de jogo
        self.fade_fim = 0

    # ========================================================
    # ATUALIZAR
    # ========================================================

    def atualizar(self, dt, player):

        self.tempo += dt

        if self.vida_exibida is None:

            self.vida_exibida = player.vida
            self.vida_anterior = player.vida

        # Detecta se o jogador acabou de tomar dano
        if player.vida < self.vida_anterior:

            self.flash_dano = 0.35

        self.vida_anterior = player.vida

        # A barra "escorrega" até a realidade
        diferenca = player.vida - self.vida_exibida

        self.vida_exibida += diferenca * min(1, dt * 6)

        if abs(diferenca) < 0.5:

            self.vida_exibida = player.vida

        if self.flash_dano > 0:

            self.flash_dano -= dt

            if self.flash_dano < 0:

                self.flash_dano = 0

    # ========================================================
    # DESENHAR TUDO
    # ========================================================

    def desenhar(
        self,
        screen,
        player,
        onda_atual,
        ondas,
        inimigos,
        jogo_terminado
    ):

        self._desenhar_flash_dano(screen, player)

        self._desenhar_vida(screen, player)

        self._desenhar_onda(screen, onda_atual, ondas, inimigos)

        self._desenhar_habilidades(screen, player)

        if jogo_terminado:

            self._desenhar_fim_de_jogo(screen, player, onda_atual, ondas)

        else:

            self.fade_fim = 0

    # ========================================================
    # FLASH VERMELHO AO RECEBER DANO
    # ========================================================

    def _desenhar_flash_dano(self, screen, player):

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
    # BARRA DE VIDA
    # ========================================================

    def _desenhar_vida(self, screen, player):

        # ========================================================
        # POSIÇÃO DO PAINEL
        # ========================================================

        largura = 300
        altura = 26

        x = 28
        y = 18

        largura_painel = largura + 24
        altura_painel = 70

        rect_painel = pygame.Rect(
            x - 12,
            y,
            largura_painel,
            altura_painel
        )

        desenhar_painel(screen, rect_painel)

        # ========================================================
        # TÍTULO
        # ========================================================

        desenhar_texto_com_sombra(
            screen,
            self.fonte_pequena,
            "HERÓI",
            x,
            y + 10
        )

        # ========================================================
        # BARRA DE VIDA
        # ========================================================

        rect_fundo = pygame.Rect(
            x,
            y + 34,
            largura,
            altura
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

        largura_vida = int(
            largura * porcentagem
        )

        if largura_vida > 0:

            cor = cor_da_vida(porcentagem)

            # Leve brilho quando a vida está baixa
            if porcentagem < 0.3:
                pulso = (
                                math.sin(self.tempo * 6) + 1
                        ) / 2

                cor = interpolar_cor(
                    cor,
                    (255, 255, 255),
                    pulso * 0.15
                )

            rect_vida = pygame.Rect(
                x,
                y + 34,
                largura_vida,
                altura
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

        # ========================================================
        # TEXTO DA VIDA
        # ========================================================

        texto_vida = (
            f"{max(0, int(round(player.vida)))} "
            f"/ {player.vida_maxima}"
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
    # INDICADOR DE ONDA
    # ========================================================

    def _desenhar_onda(
            self,
            screen,
            onda_atual,
            ondas,
            inimigos
    ):

        if onda_atual >= len(ondas):
            return

        onda = ondas[onda_atual]

        largura_painel = 220
        altura_painel = 70

        # Mesmo Y do painel de vida
        rect_painel = pygame.Rect(
            self.largura - largura_painel - 24,
            18,
            largura_painel,
            altura_painel
        )

        desenhar_painel(
            screen,
            rect_painel
        )

        # ========================================================
        # NÚMERO DA ONDA
        # ========================================================

        desenhar_texto_com_sombra(
            screen,
            self.fonte_media,
            f"ONDA {onda_atual + 1} / {len(ondas)}",
            rect_painel.centerx,
            rect_painel.y + 20,
            centrado=True
        )

        # ========================================================
        # INIMIGOS RESTANTES
        # ========================================================

        vivos = sum(
            1
            for inimigo in inimigos
            if not inimigo.morto
        )

        restantes = (
                vivos
                + (len(onda) - len(inimigos))
        )

        restantes = max(
            0,
            restantes
        )

        # ========================================================
        # BOLINHAS DOS INIMIGOS
        # ========================================================

        total = len(onda)

        raio = 6
        espaco = 18

        largura_bolinhas = (
                total * espaco
        )

        x_inicial = (
                rect_painel.centerx
                - largura_bolinhas // 2
                + espaco // 2
        )

        y_bolinhas = (
                rect_painel.y + 46
        )

        for i in range(total):

            centro = (
                x_inicial + i * espaco,
                y_bolinhas
            )

            if i < (total - restantes):

                cor = (
                    90,
                    90,
                    100
                )

            else:

                cor = (
                    220,
                    80,
                    80
                )

            pygame.draw.circle(
                screen,
                cor,
                centro,
                raio
            )

            pygame.draw.circle(
                screen,
                COR_BORDA,
                centro,
                raio,
                width=1
            )

    # ========================================================
    # BARRA DE HABILIDADES
    # ========================================================

    def _desenhar_habilidades(self, screen, player):

        habilidades = [
            ("SPACE", "Ataque 1", "attack_1"),
            ("E", "Ataque 2", "attack_2"),
            ("CTRL", "Dash", "dash"),
            ("H", "Cura", "heal")
        ]

        largura_icone = 78
        altura_icone = 58
        espaco = 12

        total_largura = (
            len(habilidades) * largura_icone
            + (len(habilidades) - 1) * espaco
        )

        x_inicial = self.largura // 2 - total_largura // 2
        y = self.altura - altura_icone - 22

        for i, (tecla, nome, estado) in enumerate(habilidades):

            x = x_inicial + i * (largura_icone + espaco)

            rect = pygame.Rect(x, y, largura_icone, altura_icone)

            ativo = player.estado == estado

            cor_fundo = (60, 60, 90, 200) if ativo else (20, 20, 26, 170)

            desenhar_painel(
                screen,
                rect,
                cor=cor_fundo,
                borda=(230, 210, 120) if ativo else COR_BORDA,
                raio=8
            )

            desenhar_texto_com_sombra(
                screen,
                self.fonte_pequena,
                tecla,
                rect.centerx,
                rect.y + 16,
                centrado=True
            )

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

    def _desenhar_fim_de_jogo(self, screen, player, onda_atual, ondas):

        self.fade_fim = min(1, self.fade_fim + 0.02)

        superficie = pygame.Surface(
            (self.largura, self.altura),
            pygame.SRCALPHA
        )

        superficie.fill((0, 0, 0, int(160 * self.fade_fim)))

        screen.blit(superficie, (0, 0))

        venceu = onda_atual >= len(ondas) and player.vida > 0

        if venceu:

            texto = "VITÓRIA!"
            cor = (120, 220, 140)

        else:

            texto = "GAME OVER"
            cor = (220, 90, 90)

        pulso = (math.sin(self.tempo * 3) + 1) / 2

        cor_pulsante = interpolar_cor(cor, (255, 255, 255), pulso * 0.25)

        desenhar_texto_com_sombra(
            screen,
            self.fonte_grande,
            texto,
            self.largura // 2,
            self.altura // 2 - 20,
            cor=cor_pulsante,
            centrado=True
        )

        desenhar_texto_com_sombra(
            screen,
            self.fonte_pequena,
            "Pressione ESC para sair",
            self.largura // 2,
            self.altura // 2 + 40,
            centrado=True
        )