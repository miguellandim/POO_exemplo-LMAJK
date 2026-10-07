import math
import random

import pygame

from .. import config as c
from ..cenario import Cenario
from ..componentes import Botao, desenhar_texto
from ..efeitos import desenhar_brilho
from ..recursos import Fontes
from ..sprites import SpritePersonagem
from .base import Cena


class CenaMenu(Cena):
    """Tela inicial com o título animado."""

    def __init__(self, jogo):
        super().__init__(jogo)
        self.cenario = Cenario("menu")
        chao = c.ALTURA - 70
        self.personagens = [
            SpritePersonagem("guerreiro", 150, chao, True, c.CORES_CLASSE["guerreiro"], escala=0.95),
            SpritePersonagem("mago", 290, chao, True, c.CORES_CLASSE["mago"], escala=0.95),
            SpritePersonagem("arqueiro", 420, chao, True, c.CORES_CLASSE["arqueiro"], escala=0.95),
            SpritePersonagem("dragao", 1070, chao + 4, False, escala=0.95),
        ]

        self.proximo_pulo = 1.5

        largura, altura = 340, 60
        x = c.LARGURA // 2 - largura // 2
        self.botoes = [
            Botao((x, 330, largura, altura), "Novo Jogo", self._novo_jogo, pygame.K_RETURN,
                  icone="espada", sons=self.sons),
            Botao((x, 408, largura, altura), "Como Jogar", self._como_jogar, pygame.K_h,
                  icone="magia", cor=c.ROXO, sons=self.sons),
            Botao((x, 486, largura, altura), "Sair", self.jogo.sair, pygame.K_ESCAPE,
                  icone="fuga", cor=(200, 90, 100), sons=self.sons),
        ]

    def _novo_jogo(self):
        from .selecao import CenaSelecao
        self.jogo.trocar_cena(CenaSelecao)

    def _como_jogar(self):
        from .ajuda import CenaAjuda
        self.jogo.trocar_cena(CenaAjuda)

    def atualizar(self, dt):
        super().atualizar(dt)
        self.cenario.atualizar(dt)
        for personagem in self.personagens:
            personagem.atualizar(dt)
        # De tempos em tempos um dos heróis dá um pulinho
        if self.tempo >= self.proximo_pulo:
            random.choice(self.personagens[:3]).comemorar()
            self.proximo_pulo = self.tempo + random.uniform(1.2, 2.8)

    def desenhar(self, tela):
        self.cenario.desenhar(tela)
        for personagem in self.personagens:
            personagem.desenhar(tela)

        # Título
        flutuar = math.sin(self.tempo * 1.6) * 6
        centro = (c.LARGURA // 2, 150 + flutuar)
        desenhar_brilho(tela, centro, 300, (120, 70, 20), 0.6 + 0.2 * math.sin(self.tempo * 2))
        fonte_titulo = Fontes.titulo(84)
        for deslocamento, cor in ((6, (40, 18, 6)), (3, c.OURO_ESCURO)):
            desenhar_texto(tela, "JOGO DE BATALHA", fonte_titulo, cor,
                           (centro[0], centro[1] + deslocamento), sombra=False)
        desenhar_texto(tela, "JOGO DE BATALHA", fonte_titulo, c.OURO, centro, sombra=False)

        fonte_sub = Fontes.texto(22)
        desenhar_texto(tela, "Um RPG por turnos feito com Programação Orientada a Objetos",
                       fonte_sub, c.TEXTO_SUAVE, (c.LARGURA // 2, 228 + flutuar * 0.5))
        largura_linha = 180
        for lado in (-1, 1):
            x0 = c.LARGURA // 2 + lado * 60
            x1 = c.LARGURA // 2 + lado * (60 + largura_linha)
            pygame.draw.line(tela, c.OURO_ESCURO, (x0, 270), (x1, 270), 2)
        pygame.draw.polygon(tela, c.OURO, [(640, 262), (650, 270), (640, 278), (630, 270)])

        self.desenhar_botoes(tela)

        rodape = "Enter: jogar  •  H: como jogar  •  M: som  •  F11: tela cheia"
        if not self.sons.ativo:
            rodape = rodape.replace("M: som", "M: som (mudo)")
        desenhar_texto(tela, rodape, Fontes.texto(16), c.TEXTO_SUAVE, (c.LARGURA // 2, c.ALTURA - 22))
