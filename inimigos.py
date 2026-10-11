import pygame
import os


# ============================================================
# CONFIGURAÇÕES
# ============================================================
# WIDTH e CHAO precisam ser iguais aos do main.py
# (ficam repetidos aqui para evitar import circular)

WIDTH = 1280
CHAO = 588

ENEMY_FRAME_SIZE = 100
ENEMY_SCALE = 2

DISTANCIA_ATAQUE = 65

TEMPO_ENTRE_INIMIGOS = 1.5

# Aumento de dificuldade por onda (0.15 = +15% a cada onda)
AUMENTO_VIDA = 0.15
AUMENTO_DANO = 0.10
AUMENTO_VELOCIDADE = 0.05

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


# ============================================================
# CONFIGURAÇÃO DOS INIMIGOS
# ============================================================

ENEMY_CONFIG = {

    1: {
        "pasta": "enemy1",
        "vida": 50,
        "velocidade": 100,
        "dano": 10,
        "pontos": 100
    },

    2: {
        "pasta": "enemy2",
        "vida": 80,
        "velocidade": 75,
        "dano": 15,
        "pontos": 200
    },

    3: {
        "pasta": "enemy3",
        "vida": 120,
        "velocidade": 55,
        "dano": 20,
        "pontos": 350
    }
}


# ============================================================
# ONDAS
# ============================================================

ONDAS = [

    [1, 1, 1, 1],

    [1, 1, 2, 2, 1, 2],

    [1, 2, 2, 3, 3, 2, 3, 1]
]


# ============================================================
# FUNÇÕES
# ============================================================

def carregar_spritesheet(caminho, largura_frame, altura_frame):

    imagem = pygame.image.load(caminho).convert_alpha()

    largura = imagem.get_width()
    altura = imagem.get_height()

    frames = []

    for y in range(0, altura, altura_frame):

        for x in range(0, largura, largura_frame):

            if (
                x + largura_frame <= largura
                and y + altura_frame <= altura
            ):

                frame = imagem.subsurface(
                    pygame.Rect(
                        x,
                        y,
                        largura_frame,
                        altura_frame
                    )
                ).copy()

                frames.append(frame)

    if not frames:

        raise ValueError(
            f"Nenhum frame encontrado em: {caminho}"
        )

    return frames


# Cache: as animações de cada tipo de inimigo são carregadas
# do disco só uma vez e reaproveitadas por todos do mesmo tipo
_cache_animacoes = {}


def carregar_animacoes_inimigo(tipo):

    if tipo in _cache_animacoes:

        return _cache_animacoes[tipo]

    enemy_path = os.path.join(
        ASSETS_DIR,
        "enemies",
        ENEMY_CONFIG[tipo]["pasta"]
    )

    arquivos = {

        "idle": "idle.png",

        "walk": "walk.png",

        "attack_01": "attack_01.png",

        "attack_02": "attack_02.png",

        "hurt": "hurt.png",

        "death": "death.png"
    }

    animacoes = {}

    for estado, nome_arquivo in arquivos.items():

        caminho = os.path.join(
            enemy_path,
            nome_arquivo
        )

        if os.path.exists(caminho):

            animacoes[estado] = carregar_spritesheet(
                caminho,
                ENEMY_FRAME_SIZE,
                ENEMY_FRAME_SIZE
            )

        else:

            animacoes[estado] = []

    _cache_animacoes[tipo] = animacoes

    return animacoes


# ============================================================
# INIMIGO
# ============================================================

class Enemy:

    def __init__(self, tipo, x, nivel=0):

        # "nivel" é o número da onda (0, 1, 2...).
        # Quanto maior, mais forte o inimigo nasce.

        config = ENEMY_CONFIG[tipo]

        self.tipo = tipo

        self.x = x
        self.y = CHAO

        self.vida_maxima = round(
            config["vida"] * (1 + AUMENTO_VIDA * nivel)
        )

        self.vida = self.vida_maxima

        self.velocidade = (
            config["velocidade"]
            * (1 + AUMENTO_VELOCIDADE * nivel)
        )

        self.dano = round(
            config["dano"] * (1 + AUMENTO_DANO * nivel)
        )

        # Pontos que o HUD soma quando o inimigo é derrotado
        self.pontos = config["pontos"]

        # O HUD marca como True depois de contar os pontos
        self.pontuado = False

        if x < WIDTH // 2:

            self.direcao_movimento = "right"

        else:

            self.direcao_movimento = "left"

        self.estado = "idle"

        self.frame_atual = 0
        self.tempo_animacao = 0

        self.tempo_ataque = 0

        self.ja_deu_dano = False

        self.morto = False

        self.animacoes = carregar_animacoes_inimigo(tipo)

    # ========================================================
    # RETÂNGULO REAL DO INIMIGO
    # ========================================================

    def get_rect(self):

        frames = self.animacoes[
            self.estado
        ]

        if not frames:

            return pygame.Rect(
                self.x - 30,
                self.y - 80,
                60,
                80
            )

        frame = frames[
            min(
                self.frame_atual,
                len(frames) - 1
            )
        ]

        frame = pygame.transform.scale(
            frame,
            (
                ENEMY_FRAME_SIZE * ENEMY_SCALE,
                ENEMY_FRAME_SIZE * ENEMY_SCALE
            )
        )

        area_personagem = frame.get_bounding_rect(
            min_alpha=1
        )

        rect = pygame.Rect(
            0,
            0,
            area_personagem.width,
            area_personagem.height
        )

        rect.centerx = self.x
        rect.bottom = self.y

        return rect

    # ========================================================
    # HITBOX DO ATAQUE DO INIMIGO
    # ========================================================

    def get_attack_rect(self):

        distancia = 15
        largura = 75
        altura = 65

        if self.direcao_movimento == "right":

            return pygame.Rect(
                self.x + distancia,
                self.y - altura,
                largura,
                altura
            )

        else:

            return pygame.Rect(
                self.x - distancia - largura,
                self.y - altura,
                largura,
                altura
            )

    # ========================================================
    # MUDAR ESTADO
    # ========================================================

    def mudar_estado(self, novo_estado):

        if self.estado != novo_estado:

            self.estado = novo_estado

            self.frame_atual = 0
            self.tempo_animacao = 0

    # ========================================================
    # ATUALIZAR INIMIGO
    # ========================================================

    def atualizar(self, dt, player):

        if self.morto:

            return

        self.tempo_ataque -= dt

        # Morte e hurt: só animam
        if self.estado in ["death", "hurt"]:

            self.atualizar_animacao(dt)

            return

        # Ataque: anima e aplica o dano no attack_02
        if self.estado in ["attack_01", "attack_02"]:

            self.atualizar_animacao(dt)

            if (
                self.estado == "attack_02"
                and not self.ja_deu_dano
            ):

                ataque = self.get_attack_rect()
                jogador = player.get_rect()

                if ataque.colliderect(jogador):

                    player.receber_dano(self.dano)

                    self.ja_deu_dano = True

            return

        distancia_x = player.x - self.x

        distancia = abs(distancia_x)

        # Vira para o jogador
        if distancia_x > 0:

            self.direcao_movimento = "right"

        elif distancia_x < 0:

            self.direcao_movimento = "left"

        if distancia <= DISTANCIA_ATAQUE:

            # Perto do jogador: ataca ou espera o cooldown
            if self.tempo_ataque <= 0:

                self.mudar_estado("attack_01")

                self.tempo_ataque = 1.0

                self.ja_deu_dano = False

            else:

                self.mudar_estado("idle")

        else:

            # Longe: anda em direção ao jogador
            if distancia_x > 0:

                self.x += self.velocidade * dt

            else:

                self.x -= self.velocidade * dt

            self.mudar_estado("walk")

        self.y = CHAO

        self.atualizar_animacao(dt)

    # ========================================================
    # RECEBER DANO
    # ========================================================

    def receber_dano(self, dano):

        if self.morto or self.estado == "death":

            return

        self.vida -= dano

        self.vida = max(
            0,
            self.vida
        )

        if self.vida <= 0:

            self.mudar_estado("death")

        else:

            self.mudar_estado("hurt")

    # ========================================================
    # ANIMAÇÃO
    # ========================================================

    def atualizar_animacao(self, dt):

        frames = self.animacoes[
            self.estado
        ]

        if not frames:

            # Sem sprite de morte: marca como morto na hora
            if self.estado == "death":

                self.morto = True

            return

        if self.estado == "death":

            velocidade_animacao = 0.15

        elif self.estado == "hurt":

            velocidade_animacao = 0.08

        else:

            velocidade_animacao = 0.10

        self.tempo_animacao += dt

        if self.tempo_animacao >= velocidade_animacao:

            self.tempo_animacao = 0

            self.frame_atual += 1

            if self.estado == "death":

                if self.frame_atual >= len(frames):

                    self.frame_atual = len(frames) - 1

                    self.morto = True

            elif self.frame_atual >= len(frames):

                self.frame_atual = 0

                if self.estado == "attack_01":

                    # Segundo estágio do ataque (onde o dano acontece)
                    self.mudar_estado("attack_02")

                elif self.estado in ["attack_02", "hurt"]:

                    self.mudar_estado("idle")

    # ========================================================
    # DESENHAR
    # ========================================================

    def desenhar(self, tela):

        frames = self.animacoes[
            self.estado
        ]

        if not frames:

            return

        frame = frames[
            min(
                self.frame_atual,
                len(frames) - 1
            )
        ]

        frame = pygame.transform.scale(
            frame,
            (
                ENEMY_FRAME_SIZE * ENEMY_SCALE,
                ENEMY_FRAME_SIZE * ENEMY_SCALE
            )
        )

        if self.direcao_movimento == "left":

            frame = pygame.transform.flip(
                frame,
                True,
                False
            )

        area_personagem = frame.get_bounding_rect(
            min_alpha=1
        )

        pos_x = (
            self.x
            - area_personagem.centerx
        )

        pos_y = (
            self.y
            - area_personagem.bottom
        )

        tela.blit(
            frame,
            (pos_x, pos_y)
        )


# ============================================================
# GERENCIADOR DE ONDAS
# ============================================================

class GerenciadorOndas:

    def __init__(self):

        self.onda_atual = 0

        self.inimigos = []

        self.indice_spawn = 0
        self.tempo_spawn = 0

        # True quando todas as ondas foram vencidas
        self.terminou = False

        self.iniciar_onda()

    # ========================================================
    # INFORMAÇÕES (usadas pelo HUD)
    # ========================================================

    @property
    def total_ondas(self):

        return len(ONDAS)

    @property
    def numero_onda(self):

        return min(
            self.onda_atual + 1,
            len(ONDAS)
        )

    def total_na_onda(self):

        if self.terminou:

            return 0

        return len(ONDAS[self.onda_atual])

    def derrotados_na_onda(self):

        return sum(
            1
            for inimigo in self.inimigos
            if inimigo.vida <= 0
        )

    # ========================================================
    # DIFICULDADE
    # ========================================================

    def intervalo_spawn(self):

        # Inimigos aparecem mais rápido a cada onda
        return max(
            0.6,
            TEMPO_ENTRE_INIMIGOS - 0.25 * self.onda_atual
        )

    # ========================================================
    # INICIAR ONDA
    # ========================================================

    def iniciar_onda(self):

        self.indice_spawn = 0
        self.tempo_spawn = 0

        self.inimigos.clear()

    # ========================================================
    # ATUALIZAR
    # ========================================================

    def atualizar(self, dt, player):

        if self.terminou:

            return

        onda = ONDAS[self.onda_atual]

        # SPAWN
        if self.indice_spawn < len(onda):

            self.tempo_spawn += dt

            if self.tempo_spawn >= self.intervalo_spawn():

                tipo = onda[self.indice_spawn]

                if self.indice_spawn % 2 == 0:

                    x_spawn = -80

                else:

                    x_spawn = WIDTH + 80

                self.inimigos.append(
                    Enemy(
                        tipo,
                        x_spawn,
                        self.onda_atual
                    )
                )

                self.indice_spawn += 1

                self.tempo_spawn = 0

        # ATUALIZAR INIMIGOS
        for inimigo in self.inimigos:

            if not inimigo.morto:

                inimigo.atualizar(dt, player)

        # FIM DA ONDA
        if (
            self.indice_spawn >= len(onda)
            and len(self.inimigos) > 0
            and all(
                inimigo.morto
                for inimigo in self.inimigos
            )
        ):

            self.onda_atual += 1

            if self.onda_atual < len(ONDAS):

                self.iniciar_onda()

            else:

                self.terminou = True

    # ========================================================
    # DESENHAR
    # ========================================================

    def desenhar(self, tela):

        for inimigo in self.inimigos:

            inimigo.desenhar(tela)