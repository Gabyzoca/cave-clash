from hud import HUD
import pygame
import os


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

ENEMY_FRAME_SIZE = 100
ENEMY_SCALE = 2

DISTANCIA_ATAQUE = 65

TEMPO_ENTRE_INIMIGOS = 1.5

DANO_ATAQUE_1 = 25
DANO_ATAQUE_2 = 35


# ============================================================
# INICIALIZAÇÃO
# ============================================================

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arena Game")
hud = HUD(WIDTH, HEIGHT)

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

        self.attack_hit_enemies = set()

        self.dash_distancia = 180

        self.cura = 25

        self.animacoes = {}

        self.carregar_animacoes()

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
            "dash",
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

    def get_attack_rect(self):

        largura = 75
        altura = 60

        distancia = 20

        if self.direcao == "right":

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

    def mudar_estado(self, novo_estado):

        if self.estado != novo_estado:

            self.estado = novo_estado

            self.frame_atual = 0
            self.tempo_animacao = 0

    def atualizar_movimento(self, dt):

        if self.estado in [
            "attack_1",
            "attack_2",
            "hurt",
            "death",
            "heal",
            "dash"
        ]:

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

            self.x += (
                movimento
                * velocidade
                * dt
            )

        else:

            self.mudar_estado("idle")

        self.x = max(
            30,
            min(WIDTH - 30, self.x)
        )

        self.y = CHAO

    def atacar_1(self):

        if self.estado in [
            "attack_1",
            "attack_2",
            "hurt",
            "death",
            "heal",
            "dash"
        ]:

            return

        self.attack_hit_enemies.clear()

        self.mudar_estado(
            "attack_1"
        )

    def atacar_2(self):

        if self.estado in [
            "attack_1",
            "attack_2",
            "hurt",
            "death",
            "heal",
            "dash"
        ]:

            return

        self.attack_hit_enemies.clear()

        self.mudar_estado(
            "attack_2"
        )

    def fazer_dash(self):

        if self.estado in [
            "attack_1",
            "attack_2",
            "hurt",
            "death",
            "heal",
            "dash"
        ]:

            return

        self.mudar_estado("dash")

        if self.direcao == "right":

            self.x += self.dash_distancia

        else:

            self.x -= self.dash_distancia

        self.x = max(
            30,
            min(WIDTH - 30, self.x)
        )

    def curar(self):

        if self.estado in [
            "attack_1",
            "attack_2",
            "hurt",
            "death",
            "heal",
            "dash"
        ]:

            return

        if self.vida >= self.vida_maxima:

            return

        self.mudar_estado("heal")

    def receber_dano(self, dano):

        if self.estado == "death":

            return

        self.vida -= dano

        self.vida = max(
            0,
            self.vida
        )

        if self.vida <= 0:

            self.mudar_estado(
                "death"
            )

        else:

            self.mudar_estado(
                "hurt"
            )

    def atualizar_animacao(self, dt):

        frames = self.animacoes[
            self.estado
        ][self.direcao]

        if not frames:

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

                if self.estado in [
                    "attack_1",
                    "attack_2",
                    "hurt",
                    "heal",
                    "dash"
                ]:

                    if self.estado == "heal":

                        self.vida += self.cura

                        self.vida = min(
                            self.vida,
                            self.vida_maxima
                        )

                    self.mudar_estado(
                        "idle"
                    )

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
# CONFIGURAÇÃO DOS INIMIGOS
# ============================================================

ENEMY_CONFIG = {

    1: {
        "pasta": "enemy1",
        "vida": 50,
        "velocidade": 100,
        "dano": 10
    },

    2: {
        "pasta": "enemy2",
        "vida": 80,
        "velocidade": 75,
        "dano": 15
    },

    3: {
        "pasta": "enemy3",
        "vida": 120,
        "velocidade": 55,
        "dano": 20
    }
}


# ============================================================
# INIMIGO
# ============================================================

class Enemy:

    def __init__(self, tipo, x):

        config = ENEMY_CONFIG[tipo]

        self.tipo = tipo

        self.x = x
        self.y = CHAO

        self.vida_maxima = config["vida"]
        self.vida = self.vida_maxima

        self.velocidade = config["velocidade"]
        self.dano = config["dano"]

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

        self.animacoes = {}

        self.carregar_animacoes()

    def carregar_animacoes(self):

        enemy_path = os.path.join(
            ASSETS_DIR,
            "enemies",
            ENEMY_CONFIG[self.tipo]["pasta"]
        )

        arquivos = {

            "idle": "idle.png",

            "walk": "walk.png",

            "attack_01": "attack_01.png",

            "attack_02": "attack_02.png",

            "hurt": "hurt.png",

            "death": "death.png"
        }

        for estado, nome_arquivo in arquivos.items():

            caminho = os.path.join(
                enemy_path,
                nome_arquivo
            )

            if os.path.exists(caminho):

                self.animacoes[estado] = (
                    carregar_spritesheet(
                        caminho,
                        ENEMY_FRAME_SIZE,
                        ENEMY_FRAME_SIZE
                    )
                )

            else:

                self.animacoes[estado] = []

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

    def mudar_estado(self, novo_estado):

        if self.estado != novo_estado:

            self.estado = novo_estado

            self.frame_atual = 0
            self.tempo_animacao = 0

    def atualizar(self, dt, player):

        if self.morto:

            return

        self.tempo_ataque -= dt

        if self.estado == "death":

            self.atualizar_animacao(dt)

            return

        if self.estado == "hurt":

            self.atualizar_animacao(dt)

            return

        if self.estado in [
            "attack_01",
            "attack_02"
        ]:

            self.atualizar_animacao(dt)

            if (
                self.estado == "attack_02"
                and not self.ja_deu_dano
            ):

                ataque = self.get_attack_rect()
                jogador = player.get_rect()

                if ataque.colliderect(jogador):

                    player.receber_dano(
                        self.dano
                    )

                    self.ja_deu_dano = True

            return

        distancia_x = (
            player.x - self.x
        )

        distancia = abs(
            distancia_x
        )

        if distancia_x > 0:

            self.direcao_movimento = "right"

        elif distancia_x < 0:

            self.direcao_movimento = "left"

        if (
            distancia <= DISTANCIA_ATAQUE
            and self.tempo_ataque <= 0
        ):

            self.mudar_estado(
                "attack_01"
            )

            self.tempo_ataque = 1.0

            self.ja_deu_dano = False

        else:

            if distancia_x > 0:

                self.x += (
                    self.velocidade
                    * dt
                )

            elif distancia_x < 0:

                self.x -= (
                    self.velocidade
                    * dt
                )

            self.mudar_estado(
                "walk"
            )

        self.y = CHAO

        self.atualizar_animacao(dt)

    def receber_dano(self, dano):

        if self.morto:

            return

        if self.estado == "death":

            return

        self.vida -= dano

        self.vida = max(
            0,
            self.vida
        )

        if self.vida <= 0:

            self.mudar_estado(
                "death"
            )

        else:

            self.mudar_estado(
                "hurt"
            )

    def atualizar_animacao(self, dt):

        frames = self.animacoes[
            self.estado
        ]

        if not frames:
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
                    self.frame_atual = (len(frames) - 1)
                    self.morto = True

            elif self.frame_atual >= len(frames):

                self.frame_atual = 0

                if self.estado == "attack_01":
                    self.mudar_estado("attack_02")

                elif self.estado in ["attack_02", "hurt"]:
                    self.mudar_estado("idle")

    def desenhar(self):

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

        screen.blit(
            frame,
            (pos_x, pos_y)
        )


# ============================================================
# ONDAS
# ============================================================

ONDAS = [

    [1, 1, 1, 1],

    [1, 1, 2, 2, 1, 2],

    [1, 2, 2, 3, 3, 2, 3, 1]
]


onda_atual = 0

inimigos = []

indice_spawn = 0

tempo_spawn = 0

jogo_terminado = False


def iniciar_onda():

    global indice_spawn
    global tempo_spawn

    indice_spawn = 0
    tempo_spawn = 0

    inimigos.clear()


# ============================================================
# CRIAR JOGADOR
# ============================================================

player = Player()

iniciar_onda()


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

            if event.key == pygame.K_SPACE:

                player.atacar_1()

            if event.key == pygame.K_e:

                player.atacar_2()

            if event.key in [
                pygame.K_LCTRL,
                pygame.K_RCTRL
            ]:

                player.fazer_dash()

            if event.key == pygame.K_h:

                player.curar()

    # ========================================================
    # ATUALIZAÇÃO
    # ========================================================

    if not jogo_terminado:

        player.atualizar_movimento(dt)

        player.atualizar_animacao(dt)

        if onda_atual < len(ONDAS):

            onda = ONDAS[onda_atual]

            if indice_spawn < len(onda):

                tempo_spawn += dt

                if tempo_spawn >= TEMPO_ENTRE_INIMIGOS:

                    tipo = onda[
                        indice_spawn
                    ]

                    if indice_spawn % 2 == 0:

                        x_spawn = -80

                    else:

                        x_spawn = WIDTH + 80

                    inimigos.append(
                        Enemy(
                            tipo,
                            x_spawn
                        )
                    )

                    indice_spawn += 1

                    tempo_spawn = 0

            for inimigo in inimigos:

                if not inimigo.morto:

                    inimigo.atualizar(
                        dt,
                        player
                    )

            if player.estado in [
                "attack_1",
                "attack_2"
            ]:

                ataque = player.get_attack_rect()

                for inimigo in inimigos:

                    if inimigo.morto:

                        continue

                    if id(inimigo) in player.attack_hit_enemies:

                        continue

                    if ataque.colliderect(
                        inimigo.get_rect()
                    ):

                        if player.estado == "attack_1":

                            dano = DANO_ATAQUE_1

                        else:

                            dano = DANO_ATAQUE_2

                        inimigo.receber_dano(
                            dano
                        )

                        player.attack_hit_enemies.add(
                            id(inimigo)
                        )

            if (
                indice_spawn >= len(onda)
                and len(inimigos) > 0
            ):

                todos_mortos = all(
                    inimigo.morto
                    for inimigo in inimigos
                )

                if todos_mortos:

                    onda_atual += 1

                    if onda_atual < len(ONDAS):

                        iniciar_onda()

                    else:

                        jogo_terminado = True

        if player.estado == "death":

            jogo_terminado = True

    else:

        if player.estado == "death":

            player.atualizar_animacao(dt)

    # Atualiza as animações e efeitos do HUD (barra de vida
    # suave, flash de dano, fade de fim de jogo etc.)
    hud.atualizar(dt, player)

    # ========================================================
    # DESENHAR
    # ========================================================

    desenhar_background()

    for inimigo in inimigos:

        inimigo.desenhar()

    player.desenhar()

    hud.desenhar(
        screen,
        player,
        onda_atual,
        ONDAS,
        inimigos,
        jogo_terminado
    )

    # ========================================================
    # ATUALIZAR TELA
    # ========================================================

    pygame.display.flip()


pygame.quit()