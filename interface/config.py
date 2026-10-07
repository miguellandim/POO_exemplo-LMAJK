"""Constantes visuais da interface (tamanho da janela, cores, tempos)."""

LARGURA = 1280
ALTURA = 720
FPS = 60
TITULO = "Jogo de Batalha - POO"

# Paleta principal
FUNDO = (13, 11, 26)
TEXTO = (238, 234, 248)
TEXTO_SUAVE = (164, 158, 190)
TEXTO_APAGADO = (102, 96, 128)
CONTORNO = (18, 14, 30)

OURO = (246, 200, 92)
OURO_ESCURO = (170, 122, 40)
PAINEL = (22, 20, 42)
PAINEL_CLARO = (36, 33, 64)
PAINEL_BORDA = (86, 76, 132)

VIDA = (228, 62, 86)
VIDA_ESCURA = (120, 24, 44)
MANA = (74, 146, 255)
MANA_ESCURA = (24, 56, 130)
CURA = (96, 226, 140)
DANO = (255, 96, 96)
FANTASMA = (255, 214, 120)
ROXO = (154, 108, 255)
FOGO = (255, 140, 40)

CORES_CLASSE = {
    "guerreiro": (232, 92, 72),
    "mago": (128, 112, 255),
    "arqueiro": (96, 204, 120),
}

# Cores de cada cenário: (céu em cima, céu embaixo, montanhas, chão, partículas)
CENARIOS = {
    "menu": ((10, 8, 30), (58, 30, 82), (30, 20, 52), (22, 16, 38), (255, 170, 90)),
    "goblin": ((8, 22, 30), (34, 74, 70), (16, 40, 40), (18, 34, 28), (180, 255, 140)),
    "orc": ((36, 14, 22), (186, 92, 52), (60, 26, 30), (40, 22, 22), (255, 180, 90)),
    "dragao": ((18, 4, 8), (120, 24, 20), (44, 10, 14), (34, 10, 10), (255, 120, 40)),
}

# Posições no campo de batalha
CHAO_Y = 540
HEROI_X = 330
INIMIGO_X = 950
