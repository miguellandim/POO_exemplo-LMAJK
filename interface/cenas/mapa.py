import math

import pygame

from .. import config as c
from ..cenario import Cenario
from ..componentes import Botao, desenhar_painel, desenhar_texto, icone, quebrar_linhas
from ..efeitos import SistemaParticulas, desenhar_brilho
from ..logica import CLASSES_HEROI
from ..recursos import Fontes
from ..sprites import SpritePersonagem
from .base import Cena

NOS_Y = 330


def chave_do_heroi(heroi):
    for info in CLASSES_HEROI:
        if isinstance(heroi, info.classe):
            return info
    return CLASSES_HEROI[0]


class CenaMapa(Cena):
    """Mapa da jornada: mostra as fases, o inventário e leva para a batalha."""

    def __init__(self, jogo, mensagem=None):
        super().__init__(jogo)
        self.campanha = jogo.campanha
        self.mensagem = mensagem
        self.cenario = Cenario("menu")
        self.particulas = SistemaParticulas()
        quantidade = len(self.campanha.fases)
        self.posicoes = [c.LARGURA * (i + 1) / (quantidade + 1) for i in range(quantidade)]
        self.inimigos = [
            SpritePersonagem(fase.chave, x, NOS_Y - 46, False, escala=0.42 if fase.chave == "dragao" else 0.55)
            for fase, x in zip(self.campanha.fases, self.posicoes)
        ]

        self.info = chave_do_heroi(self.campanha.heroi)
        indice = self.campanha.indice_fase
        destino = self.posicoes[indice] - 90
        origem = self.posicoes[indice - 1] - 90 if mensagem and indice > 0 else destino
        self.heroi = SpritePersonagem(self.info.chave, origem, NOS_Y + 60, True,
                                      c.CORES_CLASSE[self.info.chave], escala=0.55)
        self.caminhada = (origem, destino, 0.0)

        self.botoes = [
            Botao((c.LARGURA // 2 - 150, c.ALTURA - 96, 300, 62), "Batalhar!", self._batalhar,
                  pygame.K_RETURN, icone="espada", tamanho_fonte=26, sons=self.sons),
            Botao((40, c.ALTURA - 82, 150, 52), "Menu", self._menu, pygame.K_ESCAPE,
                  icone="fuga", cor=(200, 90, 100), tamanho_fonte=20, sons=self.sons),
        ]
        if mensagem:
            self.sons.tocar("cura")

    def _batalhar(self):
        from .batalha import CenaBatalha
        self.jogo.trocar_cena(CenaBatalha, self.campanha.nova_batalha())

    def _menu(self):
        from .menu import CenaMenu
        self.jogo.trocar_cena(CenaMenu)

    def atualizar(self, dt):
        super().atualizar(dt)
        self.cenario.atualizar(dt)
        self.particulas.atualizar(dt)
        for sprite in self.inimigos:
            sprite.atualizar(dt)
        self.heroi.atualizar(dt)

        origem, destino, t = self.caminhada
        if t < 1.0:
            t = min(1.0, t + dt / 1.4)
            self.heroi.x = origem + (destino - origem) * (1 - (1 - t) ** 2)
            self.heroi.deslocamento.y = -abs(math.sin(t * math.pi * 5)) * 8 if t < 1 else 0
            self.caminhada = (origem, destino, t)
            if t >= 1.0 and origem != destino:
                self.heroi.comemorar()

    def desenhar(self, tela):
        self.cenario.desenhar(tela)
        campanha = self.campanha
        desenhar_texto(tela, f"A JORNADA DE {campanha.heroi.nome.upper()}", Fontes.titulo(40), c.OURO,
                       (c.LARGURA // 2, 60))
        desenhar_texto(tela, f"{self.info.titulo}  •  Fase {campanha.indice_fase + 1} de {len(campanha.fases)}",
                       Fontes.texto(20), c.TEXTO_SUAVE, (c.LARGURA // 2, 104))

        # Caminho tracejado entre as fases
        for i in range(len(self.posicoes) - 1):
            x0, x1 = self.posicoes[i] + 50, self.posicoes[i + 1] - 50
            concluido = i < campanha.indice_fase
            cor = c.OURO if concluido else c.TEXTO_APAGADO
            for x in range(int(x0), int(x1), 22):
                pygame.draw.line(tela, cor, (x, NOS_Y + 60), (min(x + 12, x1), NOS_Y + 60), 4)

        for i, (fase, x) in enumerate(zip(campanha.fases, self.posicoes)):
            concluida = i < campanha.indice_fase
            atual = i == campanha.indice_fase
            centro = (x, NOS_Y + 60)
            if atual:
                desenhar_brilho(tela, centro, 120, c.OURO, 0.5 + 0.3 * math.sin(self.tempo * 3))
            cor = c.CURA if concluida else (c.OURO if atual else c.TEXTO_APAGADO)
            pygame.draw.circle(tela, (24, 20, 44), centro, 42)
            pygame.draw.circle(tela, cor, centro, 42, 4)
            if concluida:
                icone(tela, "check", centro, 34, c.CURA)
            elif atual:
                icone(tela, "espada", centro, 34, c.OURO)
            else:
                icone(tela, "caveira", centro, 34, c.TEXTO_APAGADO)

            sprite = self.inimigos[i]
            sprite.alfa = 90 if concluida else 255
            if not concluida:
                sprite.desenhar(tela)

            desenhar_texto(tela, fase.titulo, Fontes.titulo(24), cor, (x, NOS_Y + 128))
            fonte = Fontes.texto(15)
            for j, linha in enumerate(quebrar_linhas(fase.descricao, fonte, 300)):
                desenhar_texto(tela, linha, fonte, c.TEXTO_SUAVE, (x, NOS_Y + 158 + j * 19), sombra=False)
        self.heroi.desenhar(tela)

        self._desenhar_inventario(tela)
        if self.mensagem:
            fonte = Fontes.texto(19, negrito=True)
            caixa = pygame.Rect(0, 0, fonte.size(self.mensagem)[0] + 90, 50)
            caixa.center = (c.LARGURA // 2, c.ALTURA - 140)
            desenhar_painel(tela, caixa, alfa=230, borda=c.CURA, raio=25)
            icone(tela, "pocao", (caixa.x + 34, caixa.centery), 22, c.CURA)
            desenhar_texto(tela, self.mensagem, fonte, c.TEXTO,
                           (caixa.centerx + 14, caixa.centery))
        self.desenhar_botoes(tela)

    def _desenhar_inventario(self, tela):
        heroi = self.campanha.heroi
        caixa = pygame.Rect(c.LARGURA - 336, c.ALTURA - 156, 300, 128)
        desenhar_painel(tela, caixa, alfa=215)
        desenhar_texto(tela, "MOCHILA", Fontes.texto(14, negrito=True), c.TEXTO_SUAVE,
                       (caixa.x + 18, caixa.y + 14), ancora="topleft", sombra=False)
        desenhar_texto(tela, f"Vida {self.campanha.vida_maxima}  •  ATQ {heroi.ataque}  •  DEF {heroi.defesa}",
                       Fontes.texto(14, negrito=True), c.OURO, (caixa.right - 18, caixa.y + 14),
                       ancora="topright", sombra=False)
        if not heroi.inventario:
            desenhar_texto(tela, "Vazia", Fontes.texto(18), c.TEXTO_APAGADO, caixa.center, sombra=False)
            return
        contagem = {}
        for item in heroi.inventario:
            contagem.setdefault((item.nome, item.valor), 0)
            contagem[(item.nome, item.valor)] += 1
        for i, ((nome, valor), quantidade) in enumerate(contagem.items()):
            y = caixa.y + 52 + i * 32
            icone(tela, "pocao", (caixa.x + 32, y), 22, c.CURA)
            desenhar_texto(tela, f"{quantidade}x {nome}", Fontes.texto(18, negrito=True), c.TEXTO,
                           (caixa.x + 54, y), ancora="midleft", sombra=False)
            desenhar_texto(tela, f"+{valor} vida", Fontes.texto(16), c.CURA, (caixa.right - 20, y),
                           ancora="midright", sombra=False)
