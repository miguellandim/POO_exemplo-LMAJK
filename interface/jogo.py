"""Janela principal e gerenciador de cenas."""

import pygame

from . import config as c
from .recursos import Sons


class Jogo:
    """Cria a janela, roda o loop principal e faz a transição entre cenas."""

    DURACAO_TRANSICAO = 0.28

    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((c.LARGURA, c.ALTURA), pygame.SCALED | pygame.RESIZABLE)
        pygame.display.set_caption(c.TITULO)
        pygame.display.set_icon(self._criar_icone())
        pygame.key.set_repeat(400, 40)

        self.relogio = pygame.time.Clock()
        self.sons = Sons()
        self.campanha = None
        self.rodando = True

        self.cena = None
        self._proxima = None
        self._transicao = 0.0  # 0 = sem véu, 1 = tela preta
        self._saindo = False

        from .cenas.menu import CenaMenu
        self.cena = CenaMenu(self)

    @staticmethod
    def _criar_icone():
        icone = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.line(icone, c.OURO, (6, 26), (26, 6), 5)
        pygame.draw.line(icone, c.OURO_ESCURO, (4, 18), (14, 28), 4)
        pygame.draw.line(icone, c.OURO, (26, 26), (6, 6), 5)
        return icone

    def trocar_cena(self, classe_cena, *args, **kwargs):
        """Escurece a tela, cria a nova cena e clareia de novo."""
        if self._proxima is None:
            self._proxima = (classe_cena, args, kwargs)
            self._saindo = True

    def sair(self):
        self.rodando = False

    def _tratar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.sair()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_m and not getattr(
                    self.cena, "captura_texto", False):
                self.sons.alternar()
            elif not self._saindo:
                self.cena.tratar_evento(evento)

    def _atualizar_transicao(self, dt):
        velocidade = dt / self.DURACAO_TRANSICAO
        if self._saindo:
            self._transicao = min(1.0, self._transicao + velocidade)
            if self._transicao >= 1.0:
                classe_cena, args, kwargs = self._proxima
                self.cena = classe_cena(self, *args, **kwargs)
                self._proxima = None
                self._saindo = False
        else:
            self._transicao = max(0.0, self._transicao - velocidade)

    def executar(self):
        while self.rodando:
            dt = min(self.relogio.tick(c.FPS) / 1000, 0.05)
            self._tratar_eventos()
            self.cena.atualizar(dt)
            self._atualizar_transicao(dt)

            self.cena.desenhar(self.tela)
            if self._transicao > 0:
                veu = pygame.Surface(self.tela.get_size())
                veu.fill(c.FUNDO)
                veu.set_alpha(int(255 * self._transicao))
                self.tela.blit(veu, (0, 0))
            pygame.display.flip()
        pygame.quit()


def main():
    Jogo().executar()
