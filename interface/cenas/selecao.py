import math

import pygame

from .. import config as c
from ..cenario import Cenario
from ..componentes import (Botao, CampoTexto, desenhar_painel, desenhar_texto,
                           icone, quebrar_linhas)
from ..efeitos import SistemaParticulas, desenhar_brilho
from ..logica import CLASSES_HEROI, Campanha
from ..recursos import Fontes
from ..sprites import SpritePersonagem
from .base import Cena

# Valores usados como 100% nas barrinhas de atributos
MAXIMOS = {"vida": 130, "ataque": 32, "defesa": 18}


class CartaoHeroi:
    """Cartão clicável que mostra os atributos lidos da classe do herói."""

    def __init__(self, info, ret):
        self.info = info
        self.ret = pygame.Rect(ret)
        self.cor = c.CORES_CLASSE[info.chave]
        # Instancia a classe só para ler os atributos reais (vida, ataque, defesa...)
        exemplo = info.classe("exemplo")
        self.atributos = [
            ("Vida", exemplo.vida, MAXIMOS["vida"], "coracao", c.VIDA),
            ("Ataque", exemplo.ataque, MAXIMOS["ataque"], "espada", c.FOGO),
            ("Defesa", exemplo.defesa, MAXIMOS["defesa"], "escudo", c.MANA),
        ]
        if hasattr(exemplo, "mana"):
            self.atributos.append(("Mana", exemplo.mana, 100, "gota", (120, 200, 255)))
        self.sprite = SpritePersonagem(info.chave, self.ret.centerx, self.ret.y + 236, True, self.cor, escala=0.92)
        self.hover = 0.0
        self.selecionado = False

    def atualizar(self, dt):
        alvo = 1.0 if self.ret.collidepoint(pygame.mouse.get_pos()) or self.selecionado else 0.0
        self.hover += (alvo - self.hover) * min(1.0, dt * 10)
        self.sprite.atualizar(dt)

    def desenhar(self, tela, tempo):
        ret = self.ret.move(0, -10 * self.hover)
        if self.selecionado:
            desenhar_brilho(tela, ret.center, 260, self.cor, 0.55 + 0.15 * math.sin(tempo * 4))
        desenhar_painel(tela, ret, alfa=230, borda=self.cor if self.hover > 0.5 else c.PAINEL_BORDA,
                        brilho_borda=1.0 if self.selecionado else 0.0)

        # Palco do personagem
        palco = pygame.Rect(ret.x + 14, ret.y + 14, ret.width - 28, 230)
        superficie = pygame.Surface(palco.size, pygame.SRCALPHA)
        for y in range(palco.height):
            alfa = int(70 * (y / palco.height))
            superficie.fill((*self.cor, alfa), (0, y, palco.width, 1))
        tela.blit(superficie, palco)
        self.sprite.y_chao = ret.y + 236
        self.sprite.desenhar(tela)

        desenhar_texto(tela, self.info.titulo.upper(), Fontes.titulo(30), self.cor,
                       (ret.centerx, ret.y + 272))
        fonte = Fontes.texto(16)
        for i, linha in enumerate(quebrar_linhas(self.info.descricao, fonte, ret.width - 40)):
            desenhar_texto(tela, linha, fonte, c.TEXTO_SUAVE, (ret.centerx, ret.y + 304 + i * 20), sombra=False)

        y = ret.y + 352
        fonte_attr = Fontes.texto(15, negrito=True)
        for nome, valor, maximo, nome_icone, cor in self.atributos:
            icone(tela, nome_icone, (ret.x + 30, y + 8), 16, cor)
            desenhar_texto(tela, nome, fonte_attr, c.TEXTO, (ret.x + 46, y + 8), ancora="midleft", sombra=False)
            barra = pygame.Rect(ret.x + 118, y + 2, ret.width - 180, 12)
            pygame.draw.rect(tela, (14, 12, 26), barra, border_radius=6)
            largura = int(barra.width * min(1.0, valor / maximo) * min(1.0, 0.4 + self.hover))
            pygame.draw.rect(tela, cor, (barra.x, barra.y, largura, barra.height), border_radius=6)
            desenhar_texto(tela, str(valor), fonte_attr, c.TEXTO, (ret.right - 26, y + 8), sombra=False)
            y += 24
        desenhar_texto(tela, f"Especial: {self.info.especial}", Fontes.texto(14, negrito=True), c.OURO,
                       (ret.centerx, ret.bottom - 18), sombra=False)


class CenaSelecao(Cena):
    """Escolha da classe (Guerreiro, Mago ou Arqueiro) e do nome do herói."""

    captura_texto = True

    def __init__(self, jogo):
        super().__init__(jogo)
        self.cenario = Cenario("menu")
        self.particulas = SistemaParticulas()
        largura, altura, espaco = 330, 470, 36
        inicio = (c.LARGURA - (largura * 3 + espaco * 2)) // 2
        self.cartoes = [
            CartaoHeroi(info, (inicio + i * (largura + espaco), 96, largura, altura))
            for i, info in enumerate(CLASSES_HEROI)
        ]
        self.selecionado = None
        self.campo = CampoTexto((c.LARGURA // 2 - 330, 612, 360, 58))
        self.botao_comecar = Botao((c.LARGURA // 2 + 46, 612, 284, 58), "Começar!", self._comecar,
                                   pygame.K_RETURN, icone="espada", sons=self.sons)
        self.botao_voltar = Botao((40, c.ALTURA - 82, 150, 52), "Voltar", self._voltar, pygame.K_ESCAPE,
                                  icone="fuga", cor=(200, 90, 100), tamanho_fonte=20, sons=self.sons)
        self.botoes = [self.botao_comecar, self.botao_voltar]
        self._selecionar(0)

    def _selecionar(self, indice):
        self.selecionado = indice
        for i, cartao in enumerate(self.cartoes):
            cartao.selecionado = i == indice
        cartao = self.cartoes[indice]
        cartao.sprite.comemorar()
        self.particulas.subir(cartao.ret.centerx, cartao.ret.y + 200, cartao.cor, 22, 90)

    def _comecar(self):
        info = self.cartoes[self.selecionado].info
        nome = self.campo.texto.strip() or info.titulo
        self.jogo.campanha = Campanha(info.classe, nome)
        from .mapa import CenaMapa
        self.jogo.trocar_cena(CenaMapa)

    def _voltar(self):
        from .menu import CenaMenu
        self.jogo.trocar_cena(CenaMenu)

    def tratar_evento(self, evento):
        if super().tratar_evento(evento):
            return True
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for i, cartao in enumerate(self.cartoes):
                if cartao.ret.collidepoint(evento.pos):
                    self.sons.tocar("clique")
                    self._selecionar(i)
                    return True
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_TAB):
            passo = -1 if evento.key == pygame.K_LEFT else 1
            self.sons.tocar("clique")
            self._selecionar((self.selecionado + passo) % len(self.cartoes))
            return True
        return self.campo.tratar_evento(evento)

    def atualizar(self, dt):
        super().atualizar(dt)
        self.cenario.atualizar(dt)
        self.particulas.atualizar(dt)
        self.campo.atualizar(dt)
        for cartao in self.cartoes:
            cartao.atualizar(dt)

    def desenhar(self, tela):
        self.cenario.desenhar(tela)
        desenhar_texto(tela, "ESCOLHA SEU HERÓI", Fontes.titulo(44), c.OURO, (c.LARGURA // 2, 52))
        for cartao in self.cartoes:
            cartao.desenhar(tela, self.tempo)
        self.particulas.desenhar(tela)
        desenhar_texto(tela, "Nome do herói", Fontes.texto(15, negrito=True), c.TEXTO_SUAVE,
                       (self.campo.ret.x + 4, self.campo.ret.y - 4), ancora="bottomleft", sombra=False)
        self.campo.desenhar(tela)
        self.desenhar_botoes(tela)
        desenhar_texto(tela, "Setas: trocar herói  •  Enter: começar", Fontes.texto(15), c.TEXTO_SUAVE,
                       (c.LARGURA - 40, c.ALTURA - 22), ancora="midright", sombra=False)
