import pygame
import os

from combate import Combate
from inimigos import GerenciadorOndas
from hud import HUD


# ============================================================
# CONFIGURAÇÕES
# ============================================================

WIDTH = 1280
HEIGHT = 720
FPS = 60

CHAO = 588

PLAYER_CANVAS_WIDTH = 96
PLAYER_CANVAS_HEIGHT = 80
PLAYER_SCALE = 2

# Estados em que o jogador não pode andar nem usar habilidades
ESTADOS_BLOQUEANTES = [
    "attack_1",
    "attack_2",
    "hurt",
    "death",
    "heal",
]

# Estados que tocam uma vez e voltam para "idle"
ESTADOS_UNICOS = [
    "attack_1",
    "attack_2",
    "hurt",
    "heal",
]


# ============================================================
# INICIALIZAÇÃO
# ============================================================

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arena Game")

clock = pygame.time.Clock()


# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


# ============================================================
# FUNÇÕES
# ============================================================

def carregar_imagem(caminho):

    return pygame.image.load(caminho).convert_alpha()


def carregar_spritesheet(caminho, largura_frame, altura_frame):

    imagem = carregar_imagem(caminho)

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


# ============================================================
# BACKGROUND
# ============================================================

background_path = os.path.join(
    ASSETS_DIR,
    "background"
)

background_layers = []

nomes_background = [
    "Sky.png",
    "Light.png",
    "MiddleLayer.png",
    "DownLayer.png",
    "TopLayer.png"
]

for nome in nomes_background:

    caminho = os.path.join(
        background_path,
        nome
    )

    imagem = carregar_imagem(caminho)

    imagem = pygame.transform.scale(
        imagem,
        (WIDTH, HEIGHT)
    )

    background_layers.append(imagem)


def desenhar_background():

    for camada in background_layers:

        screen.blit(
            camada,
            (0, 0)
        )


# ============================================================
# JOGADOR
# ============================================================

class Player:

    def __init__(self):

        self.x = WIDTH // 2
        self.y = CHAO

        self.velocidade = 250
        self.velocidade_run = 400

        self.vida_maxima = 100
        self.vida = 100

        self.direcao = "right"

        self.estado = "idle"

        self.frame_atual = 0
        self.tempo_animacao = 0

        # Guarda o nome da última animação "única" que acabou
        # (ex: "heal"). O Combate lê isso para aplicar a cura
        # e depois limpa o valor.
        self.animacao_terminou = None

        self.animacoes = {}

        self.carregar_animacoes()

    # ========================================================
    # CARREGAR ANIMAÇÕES
    # ========================================================

    def carregar_animacoes(self):

        player_path = os.path.join(
            ASSETS_DIR,
            "player"
        )

        estados = [
            "idle",
            "walk",
            "run",
            "attack_1",
            "attack_2",
            "heal",
            "hurt",
            "death"
        ]

        for estado in estados:

            self.animacoes[estado] = {}

            for direcao in [
                "left",
                "right"
            ]:

                caminho = os.path.join(
                    player_path,
                    estado,
                    f"{direcao}.png"
                )

                if os.path.exists(caminho):

                    self.animacoes[estado][direcao] = (
                        carregar_spritesheet(
                            caminho,
                            PLAYER_CANVAS_WIDTH,
                            PLAYER_CANVAS_HEIGHT
                        )
                    )

                else:

                    self.animacoes[estado][direcao] = []

    # ========================================================
    # RETÂNGULO DO PERSONAGEM
    # ========================================================

    def get_rect(self):

        frames = self.animacoes[
            self.estado
        ][self.direcao]

        if not frames:

            return pygame.Rect(
                self.x - 20,
                self.y - 60,
                40,
                60
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
                PLAYER_CANVAS_WIDTH * PLAYER_SCALE,
                PLAYER_CANVAS_HEIGHT * PLAYER_SCALE
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
    # ESTADO
    # ========================================================

    def mudar_estado(self, novo_estado):

        if self.estado != novo_estado:

            self.estado = novo_estado

            self.frame_atual = 0
            self.tempo_animacao = 0

    def pode_agir(self):

        return self.estado not in ESTADOS_BLOQUEANTES

    # ========================================================
    # MOVER (respeitando os limites da tela)
    # ========================================================

    def mover(self, deslocamento):

        self.x = max(
            30,
            min(WIDTH - 30, self.x + deslocamento)
        )

    # ========================================================
    # MOVIMENTO
    # ========================================================

    def atualizar_movimento(self, dt):

        if not self.pode_agir():

            return

        teclas = pygame.key.get_pressed()

        movimento = 0

        if (
            teclas[pygame.K_a]
            or teclas[pygame.K_LEFT]
        ):

            movimento -= 1

        if (
            teclas[pygame.K_d]
            or teclas[pygame.K_RIGHT]
        ):

            movimento += 1

        correndo = (
            teclas[pygame.K_LSHIFT]
            or teclas[pygame.K_RSHIFT]
        )

        if movimento != 0:

            if movimento > 0:

                self.direcao = "right"

            else:

                self.direcao = "left"

            if correndo:

                velocidade = self.velocidade_run

                self.mudar_estado("run")

            else:

                velocidade = self.velocidade

                self.mudar_estado("walk")

            self.mover(
                movimento
                * velocidade
                * dt
            )

        else:

            self.mudar_estado("idle")

        self.y = CHAO

    # ========================================================
    # RECEBER DANO
    # ========================================================

    def receber_dano(self, dano):

        if self.estado == "death":

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
        ][self.direcao]

        if not frames:

            # Se faltar o sprite de uma animação "única",
            # termina na hora para o jogador não ficar travado
            if self.estado in ESTADOS_UNICOS:

                self.animacao_terminou = self.estado

                self.mudar_estado("idle")

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

                    self.frame_atual = (
                        len(frames) - 1
                    )

            elif self.frame_atual >= len(frames):

                self.frame_atual = 0

                if self.estado in ESTADOS_UNICOS:

                    self.animacao_terminou = self.estado

                    self.mudar_estado("idle")

    # ========================================================
    # DESENHAR
    # ========================================================

    def desenhar(self):

        frames = self.animacoes[
            self.estado
        ][self.direcao]

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
                PLAYER_CANVAS_WIDTH * PLAYER_SCALE,
                PLAYER_CANVAS_HEIGHT * PLAYER_SCALE
            )
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

        screen.blit(
            frame,
            (pos_x, pos_y)
        )


# ============================================================
# NOVO JOGO
# ============================================================

def novo_jogo():

    return (
        Player(),
        Combate(),
        GerenciadorOndas(),
        HUD(WIDTH, HEIGHT)
    )


player, combate, ondas, hud = novo_jogo()

jogo_terminado = False


# ============================================================
# LOOP PRINCIPAL
# ============================================================

rodando = True

while rodando:

    dt = clock.tick(FPS) / 1000

    # ========================================================
    # EVENTOS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            rodando = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                rodando = False

            if jogo_terminado:

                # R reinicia o jogo
                if event.key == pygame.K_r:

                    player, combate, ondas, hud = novo_jogo()

                    jogo_terminado = False

            else:

                # O combate decide qual habilidade usar
                # conforme a tecla (SPACE, E, H)
                combate.processar_evento(event, player)

    # ========================================================
    # ATUALIZAÇÃO
    # ========================================================

    if not jogo_terminado:

        player.atualizar_movimento(dt)

        player.atualizar_animacao(dt)

        # Spawn, movimento e ataques dos inimigos
        ondas.atualizar(dt, player)

        # Cooldowns, cura e detecção de acertos do jogador
        combate.atualizar(dt, player, ondas.inimigos)

        if ondas.terminou or player.estado == "death":

            jogo_terminado = True

    else:

        if player.estado == "death":

            player.atualizar_animacao(dt)

    # O HUD identifica inimigos derrotados e soma os pontos
    hud.atualizar(dt, player, ondas)

    # ========================================================
    # DESENHAR
    # ========================================================

    desenhar_background()

    ondas.desenhar(screen)

    player.desenhar()

    hud.desenhar(
        screen,
        player,
        combate,
        ondas,
        jogo_terminado
    )

    pygame.display.flip()


pygame.quit()