# Arena Game

Um jogo 2D de arena desenvolvido em **Python com Pygame**, com sistema de ondas de inimigos, diferentes tipos de inimigos, animações, combate e HUD.

## Sobre o projeto

O jogador controla um personagem em uma arena e precisa enfrentar ondas de inimigos cada vez mais desafiadoras.

O projeto foi desenvolvido como uma aplicação prática para estudar conceitos de programação, desenvolvimento de jogos 2D e organização de projetos em Python.

## Tecnologias

* Python 3.14
* Pygame
* Git
* GitHub

## Funcionalidades

* Movimentação do personagem
* Corrida
* Ataques
* Dash
* Cura
* Sistema de vida
* Sistema de ondas
* 3 tipos de inimigos
* Diferentes atributos para cada inimigo
* Animações de personagens e inimigos
* HUD com informações da partida
* Tela de Game Over
* Sistema de dano
* Cenário com efeito de paralaxe

## Controles

| Tecla     | Ação                  |
| --------- | --------------------- |
| `A` / `←` | Mover para a esquerda |
| `D` / `→` | Mover para a direita  |
| `Shift`   | Correr                |
| `Space`   | Ataque 1              |
| `E`       | Ataque 2              |
| `Ctrl`    | Dash                  |
| `H`       | Curar                 |

## Estrutura do projeto

```text
arena_game/
├── main.py
├── hud.py
├── .gitignore
├── README.md
└── assets/
    ├── background/
    ├── enemies/
    │   ├── enemy1/
    │   ├── enemy2/
    │   └── enemy3/
    └── player/
        ├── DASH/
        ├── DEATH/
        ├── HEAL/
        ├── HURT/
        ├── IDLE/
        ├── RUN/
        ├── WALK/
        ├── attack_1/
        └── attack_2/
```

## Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/Gabyzoca/arena-game-pygame.git
```

### 2. Entre na pasta do projeto

```bash
cd arena-game-pygame
```

### 3. Crie um ambiente virtual

```bash
python -m venv .venv
```

### 4. Ative o ambiente virtual

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Instale o Pygame

```bash
pip install pygame
```

### 6. Execute o jogo

```bash
python main.py
```

## Objetivo

Sobreviver às ondas de inimigos e avançar pela arena utilizando movimentação, ataques, dash e cura.

## Status

Em desenvolvimento.
