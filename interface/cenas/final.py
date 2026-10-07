import math
import random

import pygame

from .. import config as c
from ..cenario import Cenario
from ..componentes import Botao, desenhar_painel, desenhar_texto, icone
from ..efeitos import SistemaParticulas, desenhar_brilho
from ..recursos import Fontes
from ..sprites import SpritePersonagem
from .base import Cena
from .mapa import chave_do_heroi


class CenaFinal(Cena):
    """Tela de vitória da campanha, com fogos de artifício e estatísticas."""

    def __init__(self, jogo):
        super().__init__(jogo)
        self.campanha = jogo.campanha
        self.cenario = Cenario("menu")
        self.particulas = SistemaParticulas()
        self.info = chave_do_heroi(self.campanha.heroi)
        self.heroi = SpritePersonagem(self.info.chave, c.LARGURA // 2, 430, True,
                                      c.CORES_CLASSE[self.info.chave], escala=1.2)
        self.proximo_fogo = 0.0
        self.particulas.confetes(c.LARGURA, 180)
        self.sons.tocar("vitoria")
        self.botoes = [
            Botao((c.LARGURA // 2 - 310, c.ALTURA - 92, 300, 60), "Jogar de novo", self._jogar_de_novo,
                  pygame.K_RETURN, "espada", sons=self.sons),
            Botao((c.LARGURA // 2 + 10, c.ALTURA - 92, 300, 60), "Menu principal", self._menu,
                  pygame.K_ESCAPE, "fuga", cor=c.ROXO, sons=self.sons),
        ]

    def _jogar_de_novo(self):
        from .selecao import CenaSelecao
        self.jogo.trocar_cena(CenaSelecao)

    def _menu(self):
        from .menu import CenaMenu
        self.jogo.trocar_cena(CenaMenu)

    def atualizar(self, dt):
        super().atualizar(dt)
        self.cenario.atualizar(dt)
        self.particulas.atualizar(dt)
        self.heroi.atualizar(dt)
        if not self.heroi.ocupado:
            self.heroi.comemorar()
        if self.tempo >= self.proximo_fogo:
            self.proximo_fogo = self.tempo + random.uniform(0.35, 0.8)
            cor = random.choice([(255, 210, 90), (255, 110, 140), (120, 200, 255), (150, 255, 170), (210, 150, 255)])
            x, y = random.uniform(150, c.LARGURA - 150), random.uniform(90, 300)
            self.particulas.explosao(x, y, cor, 50, 300, 1.3, 6, 90)
            self.sons.tocar("explosao", 0.25)

    def desenhar(self, tela):
        self.cenario.desenhar(tela)
        self.particulas.desenhar(tela)
        centro = (c.LARGURA // 2, 110 + math.sin(self.tempo * 2) * 5)
        desenhar_brilho(tela, centro, 260, (140, 90, 20), 0.7)
        icone(tela, "coroa", (centro[0], centro[1] - 62), 44, c.OURO)
        desenhar_texto(tela, "O REINO ESTÁ SALVO!", Fontes.titulo(68), c.OURO, centro)
        desenhar_texto(tela, f"{self.campanha.heroi.nome}, o {self.info.titulo}, derrotou o Dragão Ancestral!",
                       Fontes.texto(22), c.TEXTO, (c.LARGURA // 2, 172))
        self.heroi.desenhar(tela)

        caixa = pygame.Rect(0, 0, 760, 120)
        caixa.midtop = (c.LARGURA // 2, 470)
        desenhar_painel(tela, caixa, alfa=220, brilho_borda=0.5)
        estatisticas = [
            ("Vitórias", self.campanha.vitorias, c.OURO),
            ("Turnos", self.campanha.total_turnos, c.TEXTO),
            ("Dano causado", self.campanha.total_dano_causado, c.FOGO),
            ("Dano recebido", self.campanha.total_dano_recebido, c.DANO),
            ("Poções usadas", self.campanha.total_itens_usados, c.CURA),
        ]
        largura = caixa.width / len(estatisticas)
        for i, (rotulo, valor, cor) in enumerate(estatisticas):
            x = caixa.x + largura * (i + 0.5)
            desenhar_texto(tela, str(valor), Fontes.titulo(40), cor, (x, caixa.y + 48))
            desenhar_texto(tela, rotulo, Fontes.texto(15, negrito=True), c.TEXTO_SUAVE, (x, caixa.y + 92),
                           sombra=False)
        self.desenhar_botoes(tela)
