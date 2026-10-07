import inspect

import pygame

from src.arqueiro import Arqueiro
from src.batalha import Batalha
from src.guerreiro import Guerreiro
from src.inimigo import ChefeFinal, Inimigo, InimigoEspecial
from src.item import Item
from src.mago import Mago
from src.personagem import Personagem
from src.pocaodevida import PocaoDeVida

from .. import config as c
from ..cenario import Cenario
from ..componentes import Botao, desenhar_painel, desenhar_texto, icone, quebrar_linhas
from ..recursos import Fontes
from .base import Cena

REGRAS = [
    ("espada", "Atacar", "Golpeia o inimigo. O dano depende do ATAQUE do herói e da DEFESA do alvo."),
    ("magia", "Magia", "Exclusiva do Mago: gasta 20 de mana e causa 1,5x o ataque, ignorando a defesa."),
    ("pocao", "Itens", "Poções recuperam vida. Usar um item gasta o seu turno."),
    ("fuga", "Fugir", "Abandona a batalha e volta ao mapa (os itens usados não voltam)."),
    ("caveira", "Inimigos", "Inimigos especiais usam a habilidade a cada 3 turnos. O Chefe Final causa dano triplo!"),
    ("coroa", "Objetivo", "Vença as 3 fases. A cada vitória você ganha uma poção e recupera a vida."),
]

ATALHOS = "Teclas: 1 Atacar  •  2 Magia  •  3 Itens  •  4 Fugir  •  M som  •  F11 tela cheia"

# Posição (centro x, topo y) de cada classe no diagrama
DIAGRAMA = {
    Personagem: (520, 128),
    Guerreiro: (150, 308),
    Mago: (360, 308),
    Arqueiro: (570, 308),
    Inimigo: (800, 308),
    InimigoEspecial: (800, 404),
    ChefeFinal: (800, 500),
    Item: (1110, 128),
    PocaoDeVida: (1110, 308),
    Batalha: (190, 140),
}


def metodos_proprios(classe):
    """Métodos definidos na própria classe (lidos do código de ``src``)."""
    nomes = []
    for nome, valor in vars(classe).items():
        if inspect.isfunction(valor) and (not nome.startswith("_") or nome == "__init__"):
            nomes.append(f"{nome}()")
    return nomes


class CenaAjuda(Cena):
    """Explica as regras e mostra o diagrama de classes do projeto."""

    def __init__(self, jogo):
        super().__init__(jogo)
        self.cenario = Cenario("menu")
        self.aba = 0
        self.botoes = [
            Botao((c.LARGURA // 2 - 250, 32, 240, 50), "Como jogar", lambda: self._trocar_aba(0),
                  pygame.K_LEFT, icone="espada", tamanho_fonte=21, sons=self.sons),
            Botao((c.LARGURA // 2 + 10, 32, 240, 50), "Classes (POO)", lambda: self._trocar_aba(1),
                  pygame.K_RIGHT, icone="escudo", cor=c.ROXO, tamanho_fonte=21, sons=self.sons),
            Botao((c.LARGURA // 2 - 120, c.ALTURA - 76, 240, 54), "Voltar", self._voltar,
                  pygame.K_ESCAPE, icone="fuga", cor=(200, 90, 100), sons=self.sons),
        ]

    def _trocar_aba(self, aba):
        self.aba = aba

    def _voltar(self):
        from .menu import CenaMenu
        self.jogo.trocar_cena(CenaMenu)

    def atualizar(self, dt):
        super().atualizar(dt)
        self.cenario.atualizar(dt)

    def desenhar(self, tela):
        self.cenario.desenhar(tela)
        painel = pygame.Rect(60, 100, c.LARGURA - 120, c.ALTURA - 196)
        desenhar_painel(tela, painel, alfa=225)
        if self.aba == 0:
            self._desenhar_regras(tela, painel)
        else:
            self._desenhar_diagrama(tela)
        for i, botao in enumerate(self.botoes[:2]):
            botao.hover = max(botao.hover, 0.9 if i == self.aba else 0.0)
        self.desenhar_botoes(tela)

    def _desenhar_regras(self, tela, painel):
        fonte_titulo = Fontes.texto(22, negrito=True)
        fonte = Fontes.texto(18)
        colunas = 2
        largura = (painel.width - 90) // colunas
        for i, (nome_icone, titulo, texto) in enumerate(REGRAS):
            coluna, linha = i % colunas, i // colunas
            x = painel.x + 40 + coluna * (largura + 10)
            y = painel.y + 34 + linha * 120
            caixa = pygame.Rect(x, y, largura, 104)
            desenhar_painel(tela, caixa, alfa=200, cor=c.PAINEL_CLARO, raio=12)
            pygame.draw.circle(tela, (50, 44, 86), (x + 44, y + 52), 28)
            icone(tela, nome_icone, (x + 44, y + 52), 28, c.OURO)
            desenhar_texto(tela, titulo, fonte_titulo, c.OURO, (x + 92, y + 18), ancora="topleft")
            for j, linha_texto in enumerate(quebrar_linhas(texto, fonte, largura - 110)):
                desenhar_texto(tela, linha_texto, fonte, c.TEXTO, (x + 92, y + 50 + j * 24),
                               ancora="topleft", sombra=False)
        desenhar_texto(tela, ATALHOS, Fontes.texto(18, negrito=True), c.TEXTO_SUAVE,
                       (c.LARGURA // 2, painel.bottom - 34))

    def _desenhar_diagrama(self, tela):
        fonte_nome = Fontes.texto(17, negrito=True)
        fonte_metodo = Fontes.texto(14)
        caixas = {}
        for classe, (cx, topo) in DIAGRAMA.items():
            metodos = metodos_proprios(classe)
            largura = max(fonte_nome.size(self._titulo(classe))[0],
                          *(fonte_metodo.size(m)[0] for m in metodos)) + 36
            altura = 38 + 17 * len(metodos)
            caixas[classe] = pygame.Rect(cx - largura // 2, topo, largura, altura)

        # Setas de herança (filha -> mãe), lidas de __bases__
        for classe, caixa in caixas.items():
            for mae in classe.__bases__:
                if mae in caixas:
                    self._seta_heranca(tela, caixa.midtop, caixas[mae].midbottom)
        # Associação: a Batalha usa dois Personagens (jogador e inimigo)
        inicio = caixas[Batalha].midright
        fim = (caixas[Personagem].left, inicio[1])
        pygame.draw.line(tela, c.TEXTO_SUAVE, inicio, fim, 2)
        pygame.draw.polygon(tela, c.TEXTO_SUAVE, [fim, (fim[0] - 12, fim[1] - 6), (fim[0] - 12, fim[1] + 6)])
        desenhar_texto(tela, "jogador, inimigo", Fontes.texto(13), c.TEXTO_SUAVE,
                       ((inicio[0] + fim[0]) / 2, inicio[1] - 12), sombra=False)

        self._desenhar_legenda(tela)

        for classe, caixa in caixas.items():
            abstrata = inspect.isabstract(classe)
            cor = c.ROXO if abstrata else (c.DANO if issubclass(classe, Inimigo) else c.OURO)
            if issubclass(classe, Item) or classe is Batalha:
                cor = c.CURA if issubclass(classe, Item) else c.MANA
            desenhar_painel(tela, caixa, alfa=240, cor=c.PAINEL_CLARO, borda=cor, raio=8)
            pygame.draw.rect(tela, cor, (caixa.x, caixa.y, caixa.width, 30),
                             border_top_left_radius=8, border_top_right_radius=8)
            desenhar_texto(tela, self._titulo(classe), fonte_nome, c.FUNDO, (caixa.centerx, caixa.y + 15),
                           sombra=False)
            for i, metodo in enumerate(metodos_proprios(classe)):
                desenhar_texto(tela, metodo, fonte_metodo, c.TEXTO, (caixa.x + 14, caixa.y + 35 + i * 17),
                               ancora="topleft", sombra=False)

        legenda = "Diagrama gerado automaticamente lendo as classes da pasta src (herança via __bases__)"
        desenhar_texto(tela, legenda, Fontes.texto(15), c.TEXTO_SUAVE, (c.LARGURA // 2, 600), sombra=False)

    @staticmethod
    def _titulo(classe):
        return classe.__name__ + (" (abstrata)" if inspect.isabstract(classe) else "")

    @staticmethod
    def _desenhar_legenda(tela):
        caixa = pygame.Rect(90, 430, 330, 130)
        desenhar_painel(tela, caixa, alfa=160, raio=10)
        itens = [(c.ROXO, "Classe abstrata (ABC)"), (c.OURO, "Heróis"), (c.DANO, "Inimigos"),
                 (c.CURA, "Itens"), (c.MANA, "Controle da batalha")]
        fonte = Fontes.texto(14)
        for i, (cor, texto) in enumerate(itens):
            y = caixa.y + 16 + i * 22
            pygame.draw.rect(tela, cor, (caixa.x + 16, y + 2, 14, 14), border_radius=3)
            desenhar_texto(tela, texto, fonte, c.TEXTO, (caixa.x + 40, y), ancora="topleft", sombra=False)
        x = caixa.x + 196
        pygame.draw.line(tela, c.TEXTO_SUAVE, (x, caixa.y + 64), (x + 40, caixa.y + 64), 2)
        pygame.draw.polygon(tela, c.TEXTO_SUAVE, [(x + 52, caixa.y + 64), (x + 40, caixa.y + 57),
                                                  (x + 40, caixa.y + 71)], 2)
        desenhar_texto(tela, "herda de", fonte, c.TEXTO_SUAVE, (x + 30, caixa.y + 84), sombra=False)

    @staticmethod
    def _seta_heranca(tela, inicio, fim):
        meio_y = (inicio[1] + fim[1]) / 2
        pontos = [inicio, (inicio[0], meio_y), (fim[0], meio_y), (fim[0], fim[1] + 12)]
        pygame.draw.lines(tela, c.TEXTO_SUAVE, False, pontos, 2)
        x, y = fim
        pygame.draw.polygon(tela, c.PAINEL, [(x, y), (x - 9, y + 13), (x + 9, y + 13)])
        pygame.draw.polygon(tela, c.TEXTO_SUAVE, [(x, y), (x - 9, y + 13), (x + 9, y + 13)], 2)
