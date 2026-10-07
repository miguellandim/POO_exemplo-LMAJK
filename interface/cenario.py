"""Cenários de fundo gerados por código (céu, montanhas, árvores, castelo...)."""

import math
import random

import pygame

from . import config as c
from .componentes import gradiente_vertical
from .efeitos import Ambiente, desenhar_brilho
from .sprites import clarear, escurecer


def _perfil(largura, base, amplitude, semente, suavidade=1.0):
    gerador = random.Random(semente)
    ondas = [(gerador.uniform(0.002, 0.012) / suavidade, gerador.uniform(0, math.tau),
              gerador.uniform(0.3, 1.0)) for _ in range(4)]
    total = sum(o[2] for o in ondas)
    pontos = []
    for x in range(0, largura + 9, 8):
        y = sum(math.sin(x * f + fase) * peso for f, fase, peso in ondas) / total
        pontos.append((x, base - (y + 1) / 2 * amplitude))
    return pontos


def _camada_montanhas(tela, largura, altura, base, amplitude, cor, semente, suavidade=1.0):
    pontos = _perfil(largura, base, amplitude, semente, suavidade)
    pygame.draw.polygon(tela, cor, [(0, altura)] + pontos + [(largura, altura)])


def _pinheiro(tela, x, y_base, altura, cor):
    largura = altura * 0.42
    pygame.draw.rect(tela, escurecer(cor, 0.3), (x - 3, y_base - altura * 0.15, 6, altura * 0.15))
    for i in range(3):
        topo = y_base - altura + i * altura * 0.22
        base = y_base - altura * 0.12 - (2 - i) * altura * 0.18
        meia = largura * (0.55 + i * 0.22)
        pygame.draw.polygon(tela, cor, [(x, topo), (x - meia, base), (x + meia, base)])


def _castelo(tela, x, y_base, cor, janela):
    def torre(tx, largura, altura):
        pygame.draw.rect(tela, cor, (tx, y_base - altura, largura, altura))
        for i in range(0, largura, 14):
            pygame.draw.rect(tela, cor, (tx + i, y_base - altura - 10, 8, 10))
        pygame.draw.rect(tela, janela, (tx + largura / 2 - 4, y_base - altura + 26, 8, 14),
                         border_radius=4)

    pygame.draw.rect(tela, cor, (x, y_base - 120, 300, 120))
    for i in range(0, 300, 18):
        pygame.draw.rect(tela, cor, (x + i, y_base - 132, 10, 12))
    torre(x - 40, 70, 210)
    torre(x + 120, 60, 170)
    torre(x + 270, 80, 240)
    pygame.draw.polygon(tela, cor, [(x - 46, y_base - 210), (x - 5, y_base - 290), (x + 36, y_base - 210)])
    pygame.draw.polygon(tela, cor, [(x + 264, y_base - 240), (x + 310, y_base - 330), (x + 356, y_base - 240)])
    pygame.draw.rect(tela, (20, 8, 8), (x + 130, y_base - 60, 40, 60), border_top_left_radius=20,
                     border_top_right_radius=20)
    for jx, jy in ((x + 40, y_base - 90), (x + 220, y_base - 80), (x + 80, y_base - 70)):
        pygame.draw.rect(tela, janela, (jx, jy, 8, 12), border_radius=3)


class Cenario:
    """Fundo animado de uma cena. ``chave`` escolhe as cores e os elementos."""

    def __init__(self, chave, largura=c.LARGURA, altura=c.ALTURA):
        self.chave = chave
        self.largura, self.altura = largura, altura
        ceu_cima, ceu_baixo, montanha, chao, cor_particula = c.CENARIOS[chave]
        self.cor_particula = cor_particula
        self.tempo = 0.0
        gerador = random.Random(7)
        self.estrelas = [(gerador.uniform(0, largura), gerador.uniform(0, altura * 0.55),
                          gerador.uniform(0.6, 2.0), gerador.uniform(0, math.tau)) for _ in range(110)]

        fundo = gradiente_vertical((largura, altura), ceu_cima, ceu_baixo)
        self.lua = None

        if chave == "menu":
            self.lua = (largura * 0.91, altura * 0.085, 34)
        elif chave == "goblin":
            self.lua = (largura * 0.62, altura * 0.3, 46)
        elif chave == "orc":
            self.lua = (largura * 0.5, altura * 0.55, 110)  # sol se pondo

        if self.lua:
            lx, ly, raio = self.lua
            cor_lua = (255, 236, 200) if chave != "orc" else (255, 170, 90)
            desenhar_brilho(fundo, (lx, ly), raio * 4, escurecer(cor_lua, 0.55))
            pygame.draw.circle(fundo, cor_lua, (lx, ly), raio)
            if chave != "orc":
                pygame.draw.circle(fundo, escurecer(cor_lua, 0.08), (lx - 14, ly + 10), raio * 0.22)
                pygame.draw.circle(fundo, escurecer(cor_lua, 0.08), (lx + 16, ly - 14), raio * 0.14)

        # As estrelas ficam entre o céu e a camada da frente (montanhas, chão)
        self.ceu = fundo.convert() if pygame.display.get_surface() else fundo
        fundo = pygame.Surface((largura, altura), pygame.SRCALPHA)

        horizonte = c.CHAO_Y - 70
        _camada_montanhas(fundo, largura, altura, horizonte - 60, 220,
                          misturar_cor(montanha, ceu_baixo, 0.45), 11, 1.2)
        _camada_montanhas(fundo, largura, altura, horizonte - 10, 160, montanha, 23)

        if chave == "goblin":
            gerador = random.Random(3)
            for _ in range(36):
                x = gerador.uniform(-20, largura + 20)
                _pinheiro(fundo, x, horizonte + 20, gerador.uniform(120, 230), escurecer(montanha, 0.35))
        elif chave == "orc":
            _castelo(fundo, largura * 0.56, horizonte + 10, escurecer(montanha, 0.4), (255, 170, 70))
        elif chave == "dragao":
            gerador = random.Random(5)
            for _ in range(14):
                x = gerador.uniform(0, largura)
                h = gerador.uniform(140, 300)
                w = gerador.uniform(30, 70)
                pygame.draw.polygon(fundo, escurecer(montanha, 0.3),
                                    [(x - w, horizonte + 20), (x, horizonte - h), (x + w, horizonte + 20)])
            for _ in range(22):
                x = gerador.uniform(0, largura)
                h = gerador.uniform(40, 130)
                pygame.draw.polygon(fundo, escurecer(montanha, 0.5),
                                    [(x - 18, 0), (x, h), (x + 18, 0)])
        elif chave == "menu":
            gerador = random.Random(9)
            for _ in range(22):
                x = gerador.uniform(-20, largura + 20)
                _pinheiro(fundo, x, horizonte + 30, gerador.uniform(90, 170), escurecer(montanha, 0.45))

        # Chão
        chao_sup = gradiente_vertical((largura, altura - horizonte), clarear(chao, 0.08), escurecer(chao, 0.5))
        fundo.blit(chao_sup, (0, horizonte))
        pygame.draw.line(fundo, clarear(chao, 0.2), (0, horizonte), (largura, horizonte), 2)
        if chave == "dragao":
            for i in range(9):
                x = 60 + i * 150
                pontos = [(x, horizonte + 30 + (i % 3) * 40)]
                for _ in range(5):
                    px, py = pontos[-1]
                    pontos.append((px + random.Random(i).uniform(-30, 30) + 20, py + 18))
                pygame.draw.lines(fundo, (255, 110, 30), False, pontos, 3)
                desenhar_brilho(fundo, pontos[2], 60, (120, 40, 10))

        # Vinheta escurecendo as bordas
        vinheta = pygame.Surface((largura, altura), pygame.SRCALPHA)
        for i in range(60):
            alfa = int(150 * (1 - i / 60) ** 2)
            pygame.draw.rect(vinheta, (0, 0, 0, alfa), (i * 3, i * 2, largura - i * 6, altura - i * 4), 3)
        fundo.blit(vinheta, (0, 0))

        self.frente = fundo.convert_alpha() if pygame.display.get_surface() else fundo
        subindo = chave != "goblin"
        quantidade = 26 if chave == "goblin" else 45
        self.ambiente = Ambiente(largura, altura, cor_particula, quantidade, subindo=subindo)

    def atualizar(self, dt):
        self.tempo += dt
        self.ambiente.atualizar(dt)

    def desenhar(self, tela, deslocamento=(0, 0)):
        tela.blit(self.ceu, deslocamento)
        if self.chave in ("menu", "goblin"):
            for x, y, tamanho, fase in self.estrelas:
                intensidade = 0.5 + 0.5 * math.sin(self.tempo * 2 + fase)
                cor = tuple(int(v * (0.4 + 0.6 * intensidade)) for v in (230, 230, 255))
                pygame.draw.circle(tela, cor, (x + deslocamento[0], y + deslocamento[1]), tamanho)
        tela.blit(self.frente, deslocamento)
        self.ambiente.desenhar(tela)


def misturar_cor(a, b, fator):
    return tuple(int(x + (y - x) * fator) for x, y in zip(a, b))
