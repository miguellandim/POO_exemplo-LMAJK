"""Componentes reutilizáveis da interface: botões, barras, painéis e ícones."""

import math

import pygame

from . import config as c
from .efeitos import desenhar_brilho
from .recursos import Fontes


def desenhar_texto(tela, texto, fonte, cor, pos, ancora="center", sombra=True, alfa=255):
    imagem = fonte.render(texto, True, cor)
    ret = imagem.get_rect(**{ancora: pos})
    if sombra:
        sombra_img = fonte.render(texto, True, (6, 4, 12))
        sombra_img.set_alpha(int(alfa * 0.7))
        tela.blit(sombra_img, ret.move(2, 2))
    if alfa < 255:
        imagem.set_alpha(alfa)
    tela.blit(imagem, ret)
    return ret


def quebrar_linhas(texto, fonte, largura_maxima):
    palavras = texto.split()
    linhas, atual = [], ""
    for palavra in palavras:
        tentativa = f"{atual} {palavra}".strip()
        if fonte.size(tentativa)[0] <= largura_maxima:
            atual = tentativa
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def desenhar_painel(tela, ret, alfa=215, cor=c.PAINEL, borda=c.PAINEL_BORDA, raio=16, brilho_borda=0.0):
    ret = pygame.Rect(ret)
    superficie = pygame.Surface(ret.size, pygame.SRCALPHA)
    pygame.draw.rect(superficie, (*cor, alfa), superficie.get_rect(), border_radius=raio)
    # Filete de luz na parte de cima, para dar volume
    pygame.draw.line(superficie, (255, 255, 255, 26), (raio, 2), (ret.width - raio, 2), 2)
    tela.blit(superficie, ret)
    cor_borda = tuple(int(b + (cc - b) * brilho_borda) for b, cc in zip(borda, c.OURO))
    pygame.draw.rect(tela, cor_borda, ret, 2, border_radius=raio)


def gradiente_vertical(tamanho, cor_cima, cor_baixo):
    largura, altura = tamanho
    superficie = pygame.Surface((largura, altura))
    for y in range(altura):
        t = y / max(1, altura - 1)
        cor = tuple(int(a + (b - a) * t) for a, b in zip(cor_cima, cor_baixo))
        superficie.fill(cor, (0, y, largura, 1))
    return superficie


# ----------------------------------------------------------------------
# Ícones desenhados por código (sem depender de emoji)
# ----------------------------------------------------------------------
def icone(tela, nome, centro, tamanho=22, cor=c.TEXTO):
    x, y = centro
    s = tamanho / 22
    if nome == "espada":
        pygame.draw.line(tela, cor, (x - 8 * s, y + 8 * s), (x + 9 * s, y - 9 * s), max(2, int(4 * s)))
        pygame.draw.line(tela, cor, (x - 9 * s, y + 1 * s), (x - 1 * s, y + 9 * s), max(2, int(3 * s)))
        pygame.draw.circle(tela, cor, (x - 10 * s, y + 10 * s), 3 * s)
    elif nome == "magia":
        pontos = []
        for i in range(10):
            r = (11 if i % 2 == 0 else 4.5) * s
            a = i * math.pi / 5 - math.pi / 2
            pontos.append((x + math.cos(a) * r, y + math.sin(a) * r))
        pygame.draw.polygon(tela, cor, pontos)
    elif nome == "pocao":
        pygame.draw.circle(tela, cor, (x, y + 4 * s), 8 * s)
        pygame.draw.rect(tela, cor, (x - 3 * s, y - 10 * s, 6 * s, 9 * s))
        pygame.draw.rect(tela, cor, (x - 5 * s, y - 11 * s, 10 * s, 3 * s), border_radius=1)
    elif nome == "fuga":
        pygame.draw.line(tela, cor, (x + 9 * s, y), (x - 7 * s, y), max(2, int(4 * s)))
        pygame.draw.polygon(tela, cor, [(x - 11 * s, y), (x - 3 * s, y - 8 * s), (x - 3 * s, y + 8 * s)])
    elif nome == "coracao":
        pygame.draw.circle(tela, cor, (x - 5 * s, y - 3 * s), 6 * s)
        pygame.draw.circle(tela, cor, (x + 5 * s, y - 3 * s), 6 * s)
        pygame.draw.polygon(tela, cor, [(x - 10.5 * s, y - 1 * s), (x + 10.5 * s, y - 1 * s), (x, y + 10 * s)])
    elif nome == "escudo":
        pygame.draw.polygon(tela, cor, [(x - 9 * s, y - 9 * s), (x + 9 * s, y - 9 * s),
                                        (x + 8 * s, y + 2 * s), (x, y + 10 * s), (x - 8 * s, y + 2 * s)])
    elif nome == "gota":
        pygame.draw.circle(tela, cor, (x, y + 3 * s), 7 * s)
        pygame.draw.polygon(tela, cor, [(x - 6.5 * s, y + 1 * s), (x + 6.5 * s, y + 1 * s), (x, y - 10 * s)])
    elif nome == "coroa":
        pygame.draw.polygon(tela, cor, [(x - 10 * s, y + 7 * s), (x - 10 * s, y - 6 * s), (x - 5 * s, y),
                                        (x, y - 9 * s), (x + 5 * s, y), (x + 10 * s, y - 6 * s),
                                        (x + 10 * s, y + 7 * s)])
    elif nome == "check":
        pygame.draw.lines(tela, cor, False, [(x - 8 * s, y), (x - 2 * s, y + 7 * s), (x + 9 * s, y - 7 * s)],
                          max(2, int(4 * s)))
    elif nome == "caveira":
        pygame.draw.circle(tela, cor, (x, y - 2 * s), 9 * s)
        pygame.draw.rect(tela, cor, (x - 5 * s, y + 4 * s, 10 * s, 6 * s), border_radius=2)
        pygame.draw.circle(tela, c.PAINEL, (x - 3.5 * s, y - 2 * s), 2.6 * s)
        pygame.draw.circle(tela, c.PAINEL, (x + 3.5 * s, y - 2 * s), 2.6 * s)


class Botao:
    """Botão com animação de hover, atalho de teclado e estado desabilitado."""

    def __init__(self, ret, texto, ao_clicar, atalho=None, icone=None, cor=c.OURO,
                 tamanho_fonte=24, dica="", sons=None):
        self.ret = pygame.Rect(ret)
        self.texto = texto
        self.ao_clicar = ao_clicar
        self.atalho = atalho
        self.icone = icone
        self.cor = cor
        self.tamanho_fonte = tamanho_fonte
        self.dica = dica
        self.sons = sons
        self.habilitado = True
        self.visivel = True
        self.hover = 0.0
        self.pressionado = 0.0
        self._mouse_em_cima = False

    def tratar_evento(self, evento):
        if not (self.visivel and self.habilitado):
            return False
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.ret.collidepoint(evento.pos):
            self._acionar()
            return True
        if evento.type == pygame.KEYDOWN and self.atalho is not None and evento.key == self.atalho:
            self._acionar()
            return True
        return False

    def _acionar(self):
        self.pressionado = 1.0
        if self.sons:
            self.sons.tocar("clique")
        self.ao_clicar()

    def atualizar(self, dt):
        em_cima = self.visivel and self.habilitado and self.ret.collidepoint(pygame.mouse.get_pos())
        if em_cima and not self._mouse_em_cima and self.sons:
            self.sons.tocar("hover")
        self._mouse_em_cima = em_cima
        alvo = 1.0 if em_cima else 0.0
        self.hover += (alvo - self.hover) * min(1.0, dt * 12)
        self.pressionado = max(0.0, self.pressionado - dt * 5)

    @property
    def mouse_em_cima(self):
        return self._mouse_em_cima

    def desenhar(self, tela):
        if not self.visivel:
            return
        h = self.hover
        ret = self.ret.move(0, -3 * h + 2 * self.pressionado)
        cor = self.cor if self.habilitado else (90, 86, 110)

        if self.habilitado and h > 0.02:
            desenhar_brilho(tela, ret.center, max(ret.width, ret.height) * 0.75, cor, h * 0.45)

        base = tuple(int(v * (0.22 + 0.16 * h)) for v in cor)
        topo = tuple(int(v * (0.38 + 0.2 * h)) for v in cor)
        superficie = gradiente_vertical(ret.size, topo, base)
        mascara = pygame.Surface(ret.size, pygame.SRCALPHA)
        pygame.draw.rect(mascara, (255, 255, 255, 255), mascara.get_rect(), border_radius=14)
        superficie = superficie.convert_alpha()
        superficie.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        tela.blit(superficie, ret)
        pygame.draw.rect(tela, tuple(int(v * (0.65 + 0.35 * h)) for v in cor), ret, 2, border_radius=14)

        cor_texto = c.TEXTO if self.habilitado else c.TEXTO_APAGADO
        fonte = Fontes.texto(self.tamanho_fonte, negrito=True)
        largura_texto = fonte.size(self.texto)[0]
        largura_total = largura_texto + (34 if self.icone else 0)
        rotulo_atalho = self.nome_atalho if self.habilitado else None
        fonte_atalho = Fontes.texto(12, negrito=True)
        largura_atalho = fonte_atalho.size(rotulo_atalho)[0] + 10 if rotulo_atalho else 0
        # O conteúdo é centralizado no espaço que sobra ao lado da etiqueta do atalho
        x = ret.centerx - largura_atalho / 2 - largura_total / 2
        if self.icone:
            icone(tela, self.icone, (x + 12, ret.centery), 22, cor if self.habilitado else c.TEXTO_APAGADO)
            x += 34
        desenhar_texto(tela, self.texto, fonte, cor_texto, (x, ret.centery), ancora="midleft")

        if rotulo_atalho:
            caixa = pygame.Rect(0, 0, largura_atalho, 18)
            caixa.topright = (ret.right - 7, ret.top + 7)
            pygame.draw.rect(tela, tuple(int(v * 0.45) for v in cor), caixa, border_radius=5)
            desenhar_texto(tela, rotulo_atalho, fonte_atalho, c.TEXTO, caixa.center, sombra=False)

    NOMES_TECLAS = {pygame.K_RETURN: "Enter", pygame.K_ESCAPE: "Esc", pygame.K_LEFT: "<", pygame.K_RIGHT: ">"}

    @property
    def nome_atalho(self):
        if self.atalho is None:
            return None
        return self.NOMES_TECLAS.get(self.atalho, pygame.key.name(self.atalho).upper())


class BarraStatus:
    """Barra de vida/mana com transição suave e "rastro" do dano recebido."""

    def __init__(self, ret, cor, cor_escura, maximo, valor, icone_nome="coracao"):
        self.ret = pygame.Rect(ret)
        self.cor = cor
        self.cor_escura = cor_escura
        self.maximo = maximo
        self.valor = valor
        self.exibido = float(valor)
        self.fantasma = float(valor)
        self.icone_nome = icone_nome
        self.atraso_fantasma = 0.0
        self.pulso = 0.0

    def definir(self, valor):
        if valor < self.valor:
            self.atraso_fantasma = 0.45
            self.pulso = 1.0
        elif valor > self.valor:
            self.fantasma = valor
            self.pulso = 1.0
        self.valor = valor

    def atualizar(self, dt):
        self.exibido += (self.valor - self.exibido) * min(1.0, dt * 9)
        if self.atraso_fantasma > 0:
            self.atraso_fantasma -= dt
        else:
            self.fantasma += (self.valor - self.fantasma) * min(1.0, dt * 3.5)
        self.pulso = max(0.0, self.pulso - dt * 2.5)

    def desenhar(self, tela):
        ret = self.ret
        maximo = max(self.maximo, self.valor, 1)
        pygame.draw.rect(tela, (12, 10, 22), ret.inflate(4, 4), border_radius=ret.height // 2 + 2)
        pygame.draw.rect(tela, self.cor_escura, ret, border_radius=ret.height // 2)

        def preencher(valor, cor):
            largura = int(ret.width * max(0.0, min(1.0, valor / maximo)))
            if largura > 0:
                pygame.draw.rect(tela, cor, (ret.x, ret.y, largura, ret.height),
                                 border_radius=ret.height // 2)
            return largura

        if self.fantasma > self.exibido:
            preencher(self.fantasma, c.FANTASMA)
        largura = preencher(self.exibido, self.cor)
        if largura > 12:
            brilho_ret = pygame.Rect(ret.x + 4, ret.y + 3, largura - 8, max(2, ret.height // 4))
            superficie = pygame.Surface(brilho_ret.size, pygame.SRCALPHA)
            superficie.fill((255, 255, 255, 70))
            tela.blit(superficie, brilho_ret)
        if self.pulso > 0:
            desenhar_brilho(tela, (ret.x + largura, ret.centery), 30, self.cor, self.pulso)

        icone(tela, self.icone_nome, (ret.x - 18, ret.centery), 18, self.cor)
        fonte = Fontes.texto(15, negrito=True)
        desenhar_texto(tela, f"{round(self.exibido)} / {self.maximo}", fonte, c.TEXTO, ret.center)


class PainelLog:
    """Histórico de mensagens da batalha, com as mais novas embaixo."""

    def __init__(self, ret, max_linhas=7):
        self.ret = pygame.Rect(ret)
        self.max_linhas = max_linhas
        self.mensagens = []  # [texto, cor, idade]

    def adicionar(self, texto, cor=c.TEXTO):
        fonte = Fontes.texto(16)
        for i, linha in enumerate(quebrar_linhas(texto, fonte, self.ret.width - 50)):
            self.mensagens.append([linha, cor, 0.0, i == 0])
        self.mensagens = self.mensagens[-40:]

    def atualizar(self, dt):
        for mensagem in self.mensagens:
            mensagem[2] += dt

    def desenhar(self, tela):
        desenhar_painel(tela, self.ret, alfa=200)
        fonte_titulo = Fontes.texto(13, negrito=True)
        desenhar_texto(tela, "REGISTRO DE BATALHA", fonte_titulo, c.TEXTO_SUAVE,
                       (self.ret.x + 18, self.ret.y + 12), ancora="topleft", sombra=False)
        fonte = Fontes.texto(16)
        altura_linha = 22
        visiveis = self.mensagens[-self.max_linhas:]
        y = self.ret.bottom - 14 - altura_linha * len(visiveis)
        for i, (texto, cor, idade, primeira) in enumerate(visiveis):
            antiguidade = len(visiveis) - 1 - i
            alfa = max(70, 255 - antiguidade * 28)
            entrada = min(1.0, idade / 0.25)
            x = self.ret.x + 18 + (1 - entrada) * 30
            alfa = int(alfa * entrada)
            if primeira:
                pygame.draw.circle(tela, cor, (x + 3, y + altura_linha / 2 + 1), 3)
            desenhar_texto(tela, texto, fonte, cor, (x + 14, y + altura_linha / 2 + 1),
                           ancora="midleft", sombra=False, alfa=alfa)
            y += altura_linha


class CampoTexto:
    """Caixa para digitar o nome do herói."""

    def __init__(self, ret, texto="", limite=18, placeholder="Digite o nome do herói"):
        self.ret = pygame.Rect(ret)
        self.texto = texto
        self.limite = limite
        self.placeholder = placeholder
        self.focado = True
        self.tempo = 0.0

    def tratar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self.focado = self.ret.collidepoint(evento.pos)
        if not self.focado:
            return False
        if evento.type == pygame.TEXTINPUT:
            if len(self.texto) < self.limite:
                self.texto += evento.text
            return True
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_BACKSPACE:
            self.texto = self.texto[:-1]
            return True
        return False

    def atualizar(self, dt):
        self.tempo += dt

    def desenhar(self, tela):
        desenhar_painel(tela, self.ret, alfa=230, cor=c.PAINEL_CLARO, raio=12,
                        brilho_borda=0.6 if self.focado else 0.0)
        fonte = Fontes.texto(24, negrito=True)
        if self.texto:
            ret_texto = desenhar_texto(tela, self.texto, fonte, c.TEXTO,
                                       (self.ret.x + 18, self.ret.centery), ancora="midleft")
            fim = ret_texto.right
        else:
            desenhar_texto(tela, self.placeholder, Fontes.texto(22), c.TEXTO_APAGADO,
                           (self.ret.x + 18, self.ret.centery), ancora="midleft", sombra=False)
            fim = self.ret.x + 16
        if self.focado and int(self.tempo * 2) % 2 == 0:
            pygame.draw.line(tela, c.OURO, (fim + 3, self.ret.centery - 13), (fim + 3, self.ret.centery + 13), 2)
