import pygame
import os


# ============================================================
# CONFIGURAÇÕES DO COMBATE
# ============================================================

DANO_ATAQUE_1 = 25
DANO_ATAQUE_2 = 35

CURA = 25

# Tempo de recarga de cada habilidade (em segundos)
COOLDOWNS = {
    "attack_1": 0.6,
    "attack_2": 1.5,
    "heal": 6.0
}

# Tecla -> habilidade
TECLAS = {
    pygame.K_SPACE: "attack_1",
    pygame.K_e: "attack_2",
    pygame.K_h: "heal"
}


# ============================================================
# SONS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONS_DIR = os.path.join(BASE_DIR, "assets", "sounds")

NOMES_SONS = [
    "attack_1",
    "attack_2",
    "heal",
    "hit"
]


# ============================================================
# COMBATE
# ============================================================

class Combate:

    def __init__(self):

        self.cooldowns = {
            nome: 0
            for nome in COOLDOWNS
        }

        # Inimigos já atingidos pelo ataque atual
        # (para um golpe não dar dano várias vezes)
        self.alvos_atingidos = set()

        self.sons = self.carregar_sons()

    # ========================================================
    # SONS
    # ========================================================

    def carregar_sons(self):

        sons = {nome: None for nome in NOMES_SONS}

        try:

            if not pygame.mixer.get_init():

                pygame.mixer.init()

        except pygame.error:

            # Sem placa de som: o jogo roda normalmente, só sem áudio
            return sons

        for nome in NOMES_SONS:

            for extensao in [".wav", ".ogg", ".mp3"]:

                caminho = os.path.join(
                    SONS_DIR,
                    nome + extensao
                )

                if os.path.exists(caminho):

                    try:

                        som = pygame.mixer.Sound(caminho)

                        som.set_volume(0.5)

                        sons[nome] = som

                    except pygame.error:

                        sons[nome] = None

                    break

        return sons

    def tocar(self, nome):

        som = self.sons.get(nome)

        if som:

            som.play()

    # ========================================================
    # ENTRADA
    # ========================================================

    def processar_evento(self, event, player):

        if event.type != pygame.KEYDOWN:

            return

        habilidade = TECLAS.get(event.key)

        if habilidade:

            self.usar_habilidade(habilidade, player)

    # ========================================================
    # USAR HABILIDADE
    # ========================================================

    def usar_habilidade(self, habilidade, player):

        if self.cooldowns[habilidade] > 0:

            return False

        if not player.pode_agir():

            return False

        if (
            habilidade == "heal"
            and player.vida >= player.vida_maxima
        ):

            return False

        self.cooldowns[habilidade] = COOLDOWNS[habilidade]

        if habilidade in ["attack_1", "attack_2"]:

            self.alvos_atingidos.clear()

        player.mudar_estado(habilidade)

        self.tocar(habilidade)

        return True

    # ========================================================
    # HITBOX DO ATAQUE DO JOGADOR
    # ========================================================

    def get_attack_rect(self, player):

        largura = 75
        altura = 60

        distancia = 20

        if player.direcao == "right":

            return pygame.Rect(
                player.x + distancia,
                player.y - altura,
                largura,
                altura
            )

        else:

            return pygame.Rect(
                player.x - distancia - largura,
                player.y - altura,
                largura,
                altura
            )

    # ========================================================
    # DETECÇÃO DE ACERTOS
    # ========================================================

    def processar_acertos(self, player, inimigos):

        if player.estado not in ["attack_1", "attack_2"]:

            return

        if player.estado == "attack_1":

            dano = DANO_ATAQUE_1

        else:

            dano = DANO_ATAQUE_2

        ataque = self.get_attack_rect(player)

        for inimigo in inimigos:

            if inimigo.morto or inimigo.vida <= 0:

                continue

            if inimigo in self.alvos_atingidos:

                continue

            if ataque.colliderect(inimigo.get_rect()):

                inimigo.receber_dano(dano)

                self.alvos_atingidos.add(inimigo)

                self.tocar("hit")

    # ========================================================
    # ATUALIZAR
    # ========================================================

    def atualizar(self, dt, player, inimigos):

        # Diminui os cooldowns
        for nome in self.cooldowns:

            if self.cooldowns[nome] > 0:

                self.cooldowns[nome] = max(
                    0,
                    self.cooldowns[nome] - dt
                )

        # A cura é aplicada quando a animação de cura termina
        if player.animacao_terminou == "heal":

            player.vida = min(
                player.vida + CURA,
                player.vida_maxima
            )

        player.animacao_terminou = None

        self.processar_acertos(player, inimigos)

    # ========================================================
    # INFORMAÇÕES PARA O HUD
    # ========================================================

    def cooldown_restante(self, habilidade):

        return self.cooldowns[habilidade]

    def fracao_cooldown(self, habilidade):

        # 1 = acabou de usar, 0 = pronta
        return (
            self.cooldowns[habilidade]
            / COOLDOWNS[habilidade]
        )