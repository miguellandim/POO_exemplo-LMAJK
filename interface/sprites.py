"""Personagens desenhados por código e suas animações.

Cada desenho é feito em resolução 3x maior e depois reduzido com
``smoothscale``, o que deixa as bordas suaves (antialiasing).
"""

import math
import random

import pygame

from .config import CONTORNO, OURO, OURO_ESCURO
from .efeitos import desenhar_brilho

SUPERAMOSTRAGEM = 3

PELE = (236, 196, 160)
ACO = (178, 188, 208)
ACO_CLARO = (222, 228, 240)
ACO_ESCURO = (98, 104, 126)
MADEIRA = (124, 82, 44)
COURO = (110, 72, 42)


def misturar(cor, alvo, fator):
    return tuple(int(c + (a - c) * fator) for c, a in zip(cor, alvo))


def escurecer(cor, fator=0.35):
    return misturar(cor, (0, 0, 0), fator)


def clarear(cor, fator=0.35):
    return misturar(cor, (255, 255, 255), fator)


class Pincel:
    """Desenha formas com contorno numa superfície ampliada."""

    def __init__(self, largura, altura, s=SUPERAMOSTRAGEM):
        self.s = s
        self.superficie = pygame.Surface((largura * s, altura * s), pygame.SRCALPHA)
        self.tamanho = (largura, altura)

    def _p(self, ponto):
        return ponto[0] * self.s, ponto[1] * self.s

    def poli(self, cor, pontos, contorno=True):
        pts = [self._p(p) for p in pontos]
        pygame.draw.polygon(self.superficie, cor, pts)
        if contorno:
            pygame.draw.polygon(self.superficie, CONTORNO, pts, int(2 * self.s))

    def circ(self, cor, centro, raio, contorno=True):
        pygame.draw.circle(self.superficie, cor, self._p(centro), raio * self.s)
        if contorno:
            pygame.draw.circle(self.superficie, CONTORNO, self._p(centro), raio * self.s, int(2 * self.s))

    def elip(self, cor, ret, contorno=True):
        r = pygame.Rect(*(v * self.s for v in ret))
        pygame.draw.ellipse(self.superficie, cor, r)
        if contorno:
            pygame.draw.ellipse(self.superficie, CONTORNO, r, int(2 * self.s))

    def ret(self, cor, ret, contorno=True, raio=2):
        r = pygame.Rect(*(v * self.s for v in ret))
        pygame.draw.rect(self.superficie, cor, r, border_radius=raio * self.s)
        if contorno:
            pygame.draw.rect(self.superficie, CONTORNO, r, int(2 * self.s), border_radius=raio * self.s)

    def linha(self, cor, a, b, largura, contorno=True):
        if contorno:
            pygame.draw.line(self.superficie, CONTORNO, self._p(a), self._p(b), int((largura + 4) * self.s))
            for ponta in (a, b):
                pygame.draw.circle(self.superficie, CONTORNO, self._p(ponta), (largura + 4) * self.s / 2)
        pygame.draw.line(self.superficie, cor, self._p(a), self._p(b), int(largura * self.s))
        for ponta in (a, b):
            pygame.draw.circle(self.superficie, cor, self._p(ponta), largura * self.s / 2)

    def arco(self, cor, ret, inicio, fim, largura):
        r = pygame.Rect(*(v * self.s for v in ret))
        pygame.draw.arc(self.superficie, CONTORNO, r.inflate(4 * self.s, 4 * self.s), inicio, fim,
                        int((largura + 4) * self.s))
        pygame.draw.arc(self.superficie, cor, r, inicio, fim, int(largura * self.s))

    def estrela(self, cor, centro, raio):
        x, y = centro
        pontos = []
        for i in range(8):
            r = raio if i % 2 == 0 else raio * 0.38
            a = i * math.pi / 4 - math.pi / 2
            pontos.append((x + math.cos(a) * r, y + math.sin(a) * r))
        self.poli(cor, pontos, contorno=False)

    def finalizar(self, escala=1.0):
        largura, altura = self.tamanho
        return pygame.transform.smoothscale(
            self.superficie, (int(largura * escala), int(altura * escala))
        )


# ----------------------------------------------------------------------
# Desenhos (todos olhando para a direita)
# ----------------------------------------------------------------------
def desenhar_guerreiro(cor_classe):
    p = Pincel(200, 240)
    capa = escurecer(cor_classe, 0.3)
    p.poli(capa, [(84, 118), (118, 118), (110, 152), (64, 224), (46, 214)])
    p.ret((62, 66, 88), (84, 184, 14, 36))
    p.ret((62, 66, 88), (104, 184, 14, 36))
    p.ret(COURO, (78, 212, 22, 14), raio=4)
    p.ret(COURO, (102, 212, 24, 14), raio=4)
    p.poli(ACO, [(76, 118), (126, 118), (122, 190), (80, 190)])
    p.poli(ACO_CLARO, [(86, 126), (102, 126), (98, 162), (88, 162)], contorno=False)
    p.ret(COURO, (78, 178, 46, 10), raio=2)
    p.ret(OURO, (96, 178, 10, 10), raio=2)
    p.circ(ACO, (124, 124), 13)
    # Braço e espada
    p.linha(ACO_ESCURO, (124, 130), (142, 160), 10)
    p.poli(ACO_CLARO, [(141, 150), (150, 157), (184, 58), (178, 54)])
    p.linha((255, 255, 255), (148, 150), (180, 60), 1.5, contorno=False)
    p.linha(OURO, (134, 148), (158, 166), 6)
    p.circ(PELE, (146, 160), 7)
    p.circ(OURO, (140, 172), 4)
    # Escudo
    escudo = cor_classe
    p.poli(escudo, [(46, 128), (90, 128), (88, 170), (68, 200), (48, 170)])
    p.poli(OURO, [(52, 133), (84, 133), (83, 168), (68, 191), (53, 168)], contorno=False)
    p.poli(escudo, [(56, 137), (80, 137), (79, 166), (68, 184), (57, 166)], contorno=False)
    p.ret(OURO, (65, 142, 6, 34), contorno=False, raio=1)
    p.ret(OURO, (56, 152, 24, 6), contorno=False, raio=1)
    p.circ(ACO, (78, 124), 13)
    # Cabeça
    p.poli(cor_classe, [(82, 80), (96, 60), (124, 62), (108, 74)])
    p.circ(ACO, (101, 96), 24)
    p.poli(ACO_CLARO, [(86, 82), (100, 76), (96, 92)], contorno=False)
    p.ret((26, 22, 40), (98, 92, 28, 8), contorno=False, raio=3)
    p.ret(ACO_ESCURO, (98, 102, 26, 4), contorno=False, raio=2)
    p.circ((255, 236, 170), (116, 96), 2.5, contorno=False)
    return p


def desenhar_mago(cor_classe):
    p = Pincel(200, 240)
    manto = escurecer(cor_classe, 0.35)
    p.linha(MADEIRA, (148, 228), (148, 76), 6)
    p.poli(manto, [(84, 116), (118, 116), (142, 228), (58, 228)])
    p.poli(cor_classe, [(94, 120), (108, 120), (114, 224), (88, 224)], contorno=False)
    p.poli(OURO, [(60, 220), (140, 220), (142, 228), (58, 228)], contorno=False)
    p.ret(OURO_ESCURO, (80, 158, 44, 6), raio=2)
    p.poli(manto, [(110, 122), (130, 118), (152, 150), (140, 160), (114, 142)])
    p.circ(PELE, (148, 152), 7)
    p.circ((150, 230, 255), (148, 66), 12)
    p.circ((235, 250, 255), (144, 62), 4, contorno=False)
    # Cabeça
    p.circ(PELE, (100, 102), 17)
    p.poli((236, 236, 246), [(84, 106), (120, 106), (114, 140), (102, 156), (90, 140)])
    p.circ((40, 30, 50), (110, 98), 2.5, contorno=False)
    p.circ(escurecer(PELE, 0.1), (117, 104), 3.5, contorno=False)
    # Chapéu
    p.elip(manto, (62, 82, 78, 16))
    p.poli(manto, [(80, 90), (122, 90), (112, 50), (142, 24), (98, 44)])
    p.poli(OURO, [(81, 84), (121, 84), (122, 90), (80, 90)], contorno=False)
    p.estrela(OURO, (102, 64), 7)
    p.estrela(clarear(OURO, 0.3), (114, 44), 4)
    return p


def desenhar_arqueiro(cor_classe):
    p = Pincel(200, 240)
    capa = escurecer(cor_classe, 0.45)
    tunica = escurecer(cor_classe, 0.15)
    # Aljava
    p.poli(COURO, [(66, 112), (80, 104), (104, 168), (90, 176)])
    for i, x in enumerate((64, 72, 80)):
        p.poli((230, 80, 80), [(x, 100 - i * 2), (x + 6, 88 - i * 2), (x + 10, 102 - i * 2)])
    p.poli(capa, [(80, 112), (122, 112), (130, 214), (66, 214)])
    p.ret((96, 68, 46), (86, 186, 13, 32))
    p.ret((96, 68, 46), (104, 186, 13, 32))
    p.ret((60, 42, 30), (82, 212, 20, 12), raio=4)
    p.ret((60, 42, 30), (102, 212, 22, 12), raio=4)
    p.poli(tunica, [(84, 118), (118, 118), (124, 192), (80, 192)])
    p.poli(clarear(tunica, 0.2), [(90, 122), (100, 122), (98, 160), (90, 160)], contorno=False)
    p.ret(COURO, (80, 170, 44, 8), raio=2)
    p.ret(OURO, (98, 170, 8, 8), raio=2)
    # Arco
    p.linha((240, 232, 210), (146, 92), (146, 228), 1.5, contorno=False)
    p.arco((150, 98, 52), (120, 92, 52, 136), -math.pi / 2, math.pi / 2, 6)
    p.linha(MADEIRA, (128, 160), (186, 160), 3)
    p.poli(ACO_CLARO, [(186, 154), (198, 160), (186, 166)])
    p.linha(tunica, (118, 126), (164, 158), 9)
    p.circ(PELE, (168, 160), 7)
    # Capuz
    p.poli(capa, [(84, 84), (62, 116), (90, 108)])
    p.circ(capa, (100, 98), 23)
    p.circ(PELE, (108, 102), 14)
    p.poli(capa, [(88, 80), (124, 82), (118, 92), (94, 94)], contorno=False)
    p.circ((40, 30, 50), (114, 100), 2.5, contorno=False)
    p.linha((200, 150, 120), (108, 110), (116, 110), 1.5, contorno=False)
    return p


def desenhar_goblin():
    p = Pincel(200, 240)
    verde = (110, 170, 74)
    verde_escuro = (70, 120, 50)
    p.ret(verde_escuro, (88, 198, 11, 26))
    p.ret(verde_escuro, (104, 198, 11, 26))
    p.elip(verde_escuro, (82, 216, 20, 12))
    p.elip(verde_escuro, (102, 216, 22, 12))
    p.elip(verde, (74, 148, 56, 62))
    p.poli(COURO, [(78, 188), (126, 188), (120, 212), (86, 212)])
    p.linha(verde, (118, 164), (140, 180), 8)
    p.poli(ACO_CLARO, [(138, 172), (174, 152), (146, 184)])
    p.linha(COURO, (134, 178), (142, 186), 6)
    # Cabeça
    p.poli(verde, [(78, 122), (30, 96), (82, 110)])
    p.poli(clarear(verde, 0.25), [(72, 116), (44, 102), (76, 112)], contorno=False)
    p.elip(verde, (70, 98, 66, 56))
    p.poli(verde, [(124, 112), (170, 86), (128, 104)])
    p.circ((255, 220, 60), (114, 120), 7)
    p.circ((20, 10, 10), (116, 120), 3, contorno=False)
    p.linha(verde_escuro, (104, 110), (122, 114), 3, contorno=False)
    p.linha((40, 20, 20), (104, 138), (128, 134), 3, contorno=False)
    p.poli((250, 250, 230), [(110, 137), (114, 137), (112, 143)], contorno=False)
    p.poli((250, 250, 230), [(120, 135), (124, 135), (122, 141)], contorno=False)
    p.circ(verde_escuro, (132, 128), 2.5, contorno=False)
    return p


def desenhar_orc():
    p = Pincel(250, 290)
    pele = (116, 146, 84)
    pele_escura = (74, 100, 56)
    metal = (92, 90, 104)
    # Machado (atrás do braço)
    p.linha(MADEIRA, (186, 260), (204, 66), 8)
    p.poli(ACO, [(198, 76), (244, 52), (248, 132), (202, 112)])
    p.poli(ACO_CLARO, [(236, 60), (244, 56), (246, 126), (238, 122)], contorno=False)
    # Pernas
    p.ret((72, 58, 46), (86, 210, 26, 48))
    p.ret((72, 58, 46), (130, 210, 26, 48))
    p.ret((40, 34, 30), (80, 252, 36, 18), raio=5)
    p.ret((40, 34, 30), (126, 252, 38, 18), raio=5)
    # Corpo
    p.poli(pele, [(70, 120), (176, 120), (164, 216), (80, 216)])
    p.poli(COURO, [(84, 120), (100, 120), (164, 196), (156, 210)], contorno=False)
    p.ret(COURO, (78, 196, 90, 18), raio=3)
    p.circ(OURO, (122, 205), 9)
    p.circ((60, 40, 30), (122, 205), 4, contorno=False)
    # Braço com machado
    p.elip(pele, (160, 124, 34, 70))
    p.circ(pele_escura, (190, 192), 13)
    # Ombreira com espinhos
    for dx in (-14, 0, 14):
        p.poli(ACO_CLARO, [(70 + dx - 6, 112), (70 + dx, 82), (70 + dx + 6, 112)])
    p.circ(metal, (70, 126), 24)
    p.circ(metal, (174, 122), 18)
    # Cabeça
    p.circ(pele, (124, 98), 32)
    p.ret(pele, (100, 104, 52, 30), raio=10)
    p.poli((250, 246, 220), [(126, 112), (122, 88), (134, 108)])
    p.poli((250, 246, 220), [(146, 110), (146, 86), (154, 108)])
    p.linha((40, 20, 20), (118, 120), (152, 118), 3, contorno=False)
    p.poli((255, 70, 50), [(128, 90), (146, 86), (144, 94)], contorno=False)
    p.linha((40, 30, 30), (124, 84), (150, 80), 4, contorno=False)
    # Elmo com chifres
    p.poli((236, 226, 196), [(98, 72), (60, 50), (70, 34), (94, 62)])
    p.poli((236, 226, 196), [(146, 64), (176, 34), (184, 50), (154, 72)])
    p.poli(metal, [(92, 82), (96, 66), (124, 56), (154, 66), (158, 80)])
    p.ret(escurecer(metal, 0.3), (92, 76, 66, 8), contorno=False, raio=3)
    return p


def desenhar_dragao():
    p = Pincel(400, 340)
    corpo = (176, 38, 44)
    escuro = (104, 18, 28)
    asa = (128, 22, 34)
    barriga = (238, 176, 96)
    chifre = (240, 228, 196)
    # Cauda
    cauda = [(120, 220), (70, 250), (30, 236), (12, 200), (24, 214), (40, 226),
             (70, 228), (104, 196)]
    p.poli(corpo, cauda)
    p.poli(chifre, [(12, 200), (2, 176), (26, 196)])
    # Asa de trás
    p.poli(escurecer(asa, 0.3), [(160, 140), (70, 24), (96, 74), (36, 52), (70, 106),
                                 (24, 112), (120, 160)])
    # Pernas de trás
    p.elip(escuro, (110, 200, 60, 90))
    p.poli(chifre, [(110, 286), (104, 300), (120, 290), (126, 302), (134, 290), (146, 300), (150, 284)])
    # Corpo
    p.elip(corpo, (96, 140, 190, 130))
    p.elip(barriga, (164, 186, 110, 76))
    for i in range(4):
        p.linha(escurecer(barriga, 0.2), (190 + i * 20, 196), (188 + i * 20, 250), 2, contorno=False)
    # Espinhos das costas
    for x, y in ((130, 146), (158, 138), (186, 136)):
        p.poli(chifre, [(x - 10, y + 6), (x - 2, y - 20), (x + 8, y + 4)])
    # Pescoço
    p.poli(corpo, [(220, 170), (246, 110), (282, 82), (300, 102), (270, 130), (260, 200)])
    p.poli(barriga, [(252, 196), (262, 140), (284, 108), (292, 116), (270, 140), (266, 200)], contorno=False)
    # Perna da frente
    p.elip(corpo, (222, 220, 52, 80))
    p.poli(chifre, [(222, 290), (216, 304), (232, 294), (240, 306), (248, 294), (260, 304), (266, 288)])
    # Cabeça
    p.poli(chifre, [(286, 72), (252, 30), (294, 64)])
    p.poli(chifre, [(304, 68), (296, 18), (316, 66)])
    p.poli(corpo, [(272, 72), (336, 76), (370, 96), (366, 108), (330, 114), (284, 116), (264, 96)])
    p.poli(escuro, [(290, 112), (360, 108), (352, 124), (296, 126)])
    for x in (304, 320, 336):
        p.poli((250, 248, 236), [(x, 112), (x + 6, 112), (x + 3, 120)], contorno=False)
    p.circ((255, 220, 70), (314, 88), 6)
    p.ret((30, 10, 10), (313, 82, 3, 12), contorno=False, raio=1)
    p.circ(escuro, (360, 96), 2.5, contorno=False)
    # Asa da frente
    p.poli(asa, [(150, 160), (160, 50), (220, 2), (208, 46), (246, 42), (220, 88),
                 (244, 102), (206, 168)])
    for ponta in ((220, 2), (246, 42), (244, 102)):
        p.linha(escurecer(asa, 0.35), (172, 150), ponta, 2, contorno=False)
    return p


# Pontos importantes de cada desenho: de onde saem ataques, brilhos animados...
DEFINICOES = {
    "guerreiro": {"desenho": desenhar_guerreiro, "classe": True, "escala": 1.12,
                  "arma": (178, 60), "brilhos": []},
    "mago": {"desenho": desenhar_mago, "classe": True, "escala": 1.12,
             "arma": (148, 66), "brilhos": [((148, 66), (110, 200, 255), 34)]},
    "arqueiro": {"desenho": desenhar_arqueiro, "classe": True, "escala": 1.12,
                 "arma": (192, 160), "brilhos": []},
    "goblin": {"desenho": desenhar_goblin, "classe": False, "escala": 1.15,
               "arma": (172, 154), "brilhos": [((114, 120), (255, 220, 60), 14)]},
    "orc": {"desenho": desenhar_orc, "classe": False, "escala": 1.05,
            "arma": (240, 70), "brilhos": [((138, 90), (255, 60, 40), 18)]},
    "dragao": {"desenho": desenhar_dragao, "classe": False, "escala": 1.12,
               "arma": (368, 104), "brilhos": [((314, 88), (255, 200, 40), 18)]},
}

_cache_desenhos = {}


def obter_imagem(tipo, cor_classe=None, escala=None):
    definicao = DEFINICOES[tipo]
    escala = escala or definicao["escala"]
    chave = (tipo, cor_classe, escala)
    if chave not in _cache_desenhos:
        if definicao["classe"]:
            pincel = definicao["desenho"](cor_classe)
        else:
            pincel = definicao["desenho"]()
        _cache_desenhos[chave] = pincel.finalizar(escala)
    return _cache_desenhos[chave]


def silhueta(imagem, cor=(255, 255, 255)):
    mascara = pygame.mask.from_surface(imagem)
    return mascara.to_surface(setcolor=(*cor, 255), unsetcolor=(0, 0, 0, 0))


class SpritePersonagem:
    """Um personagem na tela, com animações de ataque, dano, morte e fuga."""

    def __init__(self, tipo, x, y_chao, olhando_direita=True, cor_classe=None, escala=None):
        self.tipo = tipo
        self.definicao = DEFINICOES[tipo]
        self.escala = escala or self.definicao["escala"]
        imagem = obter_imagem(tipo, cor_classe, self.escala)
        self.olhando_direita = olhando_direita
        self.imagem = imagem if olhando_direita else pygame.transform.flip(imagem, True, False)
        self.branca = silhueta(self.imagem)
        self.vermelha = silhueta(self.imagem, (255, 60, 40))
        self.x, self.y_chao = x, y_chao

        self.tempo = random.uniform(0, 10)
        self.deslocamento = pygame.Vector2()
        self.animacao = None  # (nome, tempo, duracao, dados)
        self.flash = 0.0
        self.aura = 0.0
        self.alfa = 255
        self.morto = False
        self.inclinacao = 0.0

    @property
    def direcao(self):
        return 1 if self.olhando_direita else -1

    @property
    def ocupado(self):
        return self.animacao is not None

    @property
    def retangulo(self):
        return self.imagem.get_rect(midbottom=(self.x + self.deslocamento.x,
                                               self.y_chao + self.deslocamento.y))

    def ponto(self, nome):
        """Posição na tela de um ponto do desenho ("arma", "centro", "topo")."""
        ret = self.retangulo
        if nome == "centro":
            return pygame.Vector2(ret.centerx, ret.centery + ret.height * 0.08)
        if nome == "topo":
            return pygame.Vector2(ret.centerx, ret.top + ret.height * 0.12)
        px, py = self.definicao[nome]
        px *= self.escala
        py *= self.escala
        if not self.olhando_direita:
            px = ret.width - px
        return pygame.Vector2(ret.left + px, ret.top + py)

    # ------------------------------------------------------------------
    # Disparadores de animação
    # ------------------------------------------------------------------
    def investir(self, distancia=150, duracao=0.5):
        self.animacao = ("investida", 0.0, duracao, distancia)

    def conjurar(self, duracao=0.5):
        self.animacao = ("conjurar", 0.0, duracao, None)

    def sofrer_dano(self, forca=1.0):
        self.flash = 0.22
        self.animacao = ("recuo", 0.0, 0.35, forca)

    def curar(self):
        self.aura = 1.0

    def morrer(self):
        self.morto = True
        self.animacao = ("morte", 0.0, 1.2, None)

    def fugir(self):
        self.animacao = ("fuga", 0.0, 0.9, None)

    def comemorar(self):
        self.animacao = ("pulo", 0.0, 0.6, None)

    # ------------------------------------------------------------------
    def atualizar(self, dt):
        self.tempo += dt
        self.flash = max(0.0, self.flash - dt)
        self.aura = max(0.0, self.aura - dt * 0.8)

        if not self.animacao:
            return
        nome, t, duracao, dados = self.animacao
        t += dt
        progresso = min(1.0, t / duracao)
        d = self.direcao

        if nome == "investida":
            # Vai rápido até o alvo (40% do tempo) e volta devagar
            if progresso < 0.4:
                fator = 1 - (1 - progresso / 0.4) ** 3
            else:
                fator = 1 - ((progresso - 0.4) / 0.6) ** 2
            self.deslocamento.x = d * dados * fator
            self.deslocamento.y = -math.sin(progresso * math.pi) * 18
        elif nome == "conjurar":
            self.deslocamento.y = -math.sin(progresso * math.pi) * 14
            self.deslocamento.x = -d * math.sin(progresso * math.pi) * 8
        elif nome == "recuo":
            self.deslocamento.x = -d * math.sin(progresso * math.pi) * 26 * dados
        elif nome == "morte":
            self.inclinacao = -d * 80 * progresso ** 2
            self.deslocamento.y = 30 * progresso ** 2
            self.alfa = int(255 * (1 - progresso))
        elif nome == "fuga":
            self.deslocamento.x = -d * 700 * progresso ** 2
            self.deslocamento.y = -abs(math.sin(progresso * math.pi * 6)) * 12
        elif nome == "pulo":
            self.deslocamento.y = -abs(math.sin(progresso * math.pi * 2)) * 40

        if progresso >= 1.0:
            self.animacao = None
            if nome != "fuga":
                self.deslocamento.update(0, 0)
        else:
            self.animacao = (nome, t, duracao, dados)

    def desenhar_sombra(self, tela, deslocamento=(0, 0)):
        largura = self.imagem.get_width() * 0.62
        altura = 26
        sombra = pygame.Surface((largura, altura), pygame.SRCALPHA)
        alfa = int(110 * self.alfa / 255 * max(0.3, 1 - abs(self.deslocamento.y) / 120))
        pygame.draw.ellipse(sombra, (0, 0, 0, alfa), sombra.get_rect())
        tela.blit(sombra, (self.x + self.deslocamento.x - largura / 2 + deslocamento[0],
                           self.y_chao - altura / 2 + deslocamento[1]))

    def desenhar(self, tela, deslocamento=(0, 0)):
        if self.alfa <= 0:
            return
        self.desenhar_sombra(tela, deslocamento)

        respiracao = 1 + 0.018 * math.sin(self.tempo * 2.6) if not self.morto else 1
        imagens = [self.imagem]
        if self.flash > 0:
            imagens.append(self.branca)

        ret = self.retangulo.move(deslocamento)
        for i, imagem in enumerate(imagens):
            img = imagem
            if respiracao != 1:
                img = pygame.transform.smoothscale(
                    img, (img.get_width(), int(img.get_height() * respiracao)))
            if self.inclinacao:
                img = pygame.transform.rotate(img, self.inclinacao)
            if i == 0:
                img.set_alpha(self.alfa)
            else:
                img.set_alpha(int(210 * min(1.0, self.flash / 0.12)))
            tela.blit(img, img.get_rect(midbottom=ret.midbottom))

        if self.morto:
            return

        for (px, py), cor, raio in self.definicao["brilhos"]:
            px *= self.escala
            py *= self.escala
            if not self.olhando_direita:
                px = ret.width - px
            pulso = 0.65 + 0.35 * math.sin(self.tempo * 3.4)
            desenhar_brilho(tela, (ret.left + px, ret.bottom - (ret.height - py) * respiracao),
                            raio * (0.9 + 0.2 * pulso), cor, pulso)

        if self.aura > 0:
            centro = self.ponto("centro") + pygame.Vector2(deslocamento)
            desenhar_brilho(tela, centro, 150, (80, 255, 140), self.aura * 0.7)

    def desenhar_furia(self, tela, intensidade, deslocamento=(0, 0)):
        """Contorno vermelho pulsante (inimigo preparando a habilidade especial)."""
        if intensidade <= 0 or self.morto:
            return
        img = self.vermelha.copy()
        img.set_alpha(int(110 * intensidade))
        ret = self.retangulo.move(deslocamento)
        for dx, dy in ((-4, 0), (4, 0), (0, -4), (0, 4)):
            tela.blit(img, ret.move(dx, dy), special_flags=pygame.BLEND_ADD)
