
# Cave Clash

Jogo 2D de ação e sobrevivência desenvolvido em **Python com Pygame**, com combate em tempo real, animações, ondas de inimigos e sistema de pontuação.

## Sobre o projeto

Cave Clash é um jogo de arena 2D no qual o jogador precisa sobreviver a três ondas de inimigos, utilizando movimentação, ataques e habilidades.

Cada tipo de inimigo possui atributos próprios de vida, velocidade e dano. Conforme a partida avança, os inimigos se tornam mais desafiadores.

O projeto foi desenvolvido para explorar conceitos de programação orientada a objetos, animações com spritesheets, detecção de colisões, gerenciamento de estados e organização modular de código.

## Tecnologias utilizadas

- Python 3.14
- Pygame
- Git e GitHub

## Funcionalidades

- Movimentação lateral e corrida
- Animações de personagens e inimigos
- Dois tipos de ataque
- Habilidade de cura
- Sistema de cooldown das habilidades
- Detecção de colisões e aplicação de dano
- Três tipos diferentes de inimigos
- Geração automática de inimigos
- Três ondas com dificuldade progressiva
- Sistema de pontuação
- Barra de vida e indicadores de habilidades
- Telas de vitória e derrota
- Reinício da partida
- Suporte a efeitos sonoros

## Controles

| Tecla | Ação |
|---|---|
| A / ← | Mover para a esquerda |
| D / → | Mover para a direita |
| Shift | Correr |
| Espaço | Ataque principal |
| E | Ataque secundário |
| H | Curar |
| R | Reiniciar após o fim da partida |
| Esc | Sair |

## Estrutura do projeto

```text
cave-clash/
├── main.py
├── combate.py
├── inimigos.py
├── hud.py
├── assets/
│   ├── background/
│   ├── enemies/
│   │   ├── enemy1/
│   │   ├── enemy2/
│   │   └── enemy3/
│   └── player/
├── README.md
└── .gitignore
```

### Organização dos módulos

- **main.py:** inicialização, cenário, personagem, movimentação, animações e loop principal.
- **combate.py:** ataques, habilidades, cooldowns, colisões e efeitos sonoros.
- **inimigos.py:** comportamento dos inimigos, atributos, ataques e gerenciamento de ondas.
- **hud.py:** pontuação, barra de vida, indicadores e telas de fim de jogo.

## Como executar

### 1. Clonar o repositório

```bash
git clone https://github.com/Gabyzoca/cave-clash.git
cd cave-clash
```

### 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

### 3. Ativar o ambiente virtual

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Instalar o Pygame

```bash
python -m pip install pygame-ce
```

### 5. Executar o jogo

```bash
python main.py
```

## Objetivo do jogo

Derrotar todos os inimigos das três ondas e alcançar a maior pontuação possível sem perder toda a vida.

## Status do projeto

**Versão funcional.**

O jogo possui seus principais sistemas implementados e poderá receber novas funcionalidades e melhorias.
