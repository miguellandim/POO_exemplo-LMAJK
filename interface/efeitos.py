"""Efeitos visuais: partículas, projéteis, números de dano e tremor de tela."""

import math
import random

import pygame

from .recursos import Fontes

_cache_brilho = {}


def brilho(raio, cor, intensidade=1.0):
    """Superfície com um círculo de luz suave (use com ``BLEND_ADD``).

    A intensidade é arredondada em 10 níveis para o cache não crescer demais.
    """
    raio = max(1, int(raio))
    nivel = round(max(0.0, min(1.0, intensidade)) * 10)
    chave = (raio, cor, nivel)
    if chave not in _cache_brilho:
        if len(_cache_brilho) > 3000:
            _cache_brilho.clear()
        tamanho = raio * 2
        superficie = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        for r in range(raio, 0, -1):
            forca = (1 - r / raio) ** 1.8 * nivel / 10
            c = tuple(int(canal * forca) for canal in cor)
            pygame.draw.circle(superficie, c, (raio, raio), r)
        _cache_brilho[chave] = superficie
    return _cache_brilho[chave]


def desenhar_brilho(tela, pos, raio, cor, intensidade=1.0):
    imagem = brilho(raio, cor, intensidade)
    tela.blit(imagem, (pos[0] - imagem.get_width() / 2, pos[1] - imagem.get_height() / 2),
              special_flags=pygame.BLEND_ADD)


class Particula:

    def __init__(self, x, y, vx, vy, vida, cor, tamanho, gravidade=0.0,
                 arrasto=0.0, brilhante=True):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.vida = self.vida_total = vida
        self.cor = cor
        self.tamanho = tamanho
        self.gravidade = gravidade
        self.arrasto = arrasto
        self.brilhante = brilhante

    @property
    def viva(self):
        return self.vida > 0

    def atualizar(self, dt):
        self.vida -= dt
        self.vy += self.gravidade * dt
        fator = max(0.0, 1 - self.arrasto * dt)
        self.vx *= fator
        self.vy *= fator
        self.x += self.vx * dt
        self.y += self.vy * dt

    def desenhar(self, tela):
        progresso = max(0.0, self.vida / self.vida_total)
        raio = self.tamanho * (0.4 + 0.6 * progresso)
        if self.brilhante:
            desenhar_brilho(tela, (self.x, self.y), raio * 2.2, self.cor, progresso)
        else:
            pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), max(1, int(raio)))


class Confete(Particula):
    """Particula retangular que gira enquanto cai (comemoração de vitória)."""

    def __init__(self, x, y, cor):
        super().__init__(
            x, y, random.uniform(-260, 260), random.uniform(-620, -260),
            random.uniform(2.0, 3.5), cor, random.uniform(5, 9),
            gravidade=520, arrasto=1.2, brilhante=False,
        )
        self.angulo = random.uniform(0, 360)
        self.giro = random.uniform(-540, 540)

    def atualizar(self, dt):
        super().atualizar(dt)
        self.angulo += self.giro * dt

    def desenhar(self, tela):
        largura = abs(math.cos(math.radians(self.angulo))) * self.tamanho + 1
        retangulo = pygame.Surface((largura, self.tamanho * 0.6 + 1), pygame.SRCALPHA)
        retangulo.fill(self.cor)
        tela.blit(retangulo, (self.x, self.y))


class SistemaParticulas:

    def __init__(self):
        self.particulas = []

    def adicionar(self, particula):
        self.particulas.append(particula)

    def explosao(self, x, y, cor, quantidade=24, velocidade=260, vida=0.7,
                 tamanho=6, gravidade=300):
        for _ in range(quantidade):
            angulo = random.uniform(0, math.tau)
            v = random.uniform(velocidade * 0.3, velocidade)
            self.adicionar(Particula(
                x, y, math.cos(angulo) * v, math.sin(angulo) * v,
                random.uniform(vida * 0.5, vida), cor,
                random.uniform(tamanho * 0.5, tamanho), gravidade, arrasto=2.5,
            ))

    def subir(self, x, y, cor, quantidade=20, largura=60, vida=1.2, tamanho=5):
        """Partículas que sobem (cura, aura de poder)."""
        for _ in range(quantidade):
            self.adicionar(Particula(
                x + random.uniform(-largura, largura), y + random.uniform(-20, 40),
                random.uniform(-15, 15), random.uniform(-160, -60),
                random.uniform(vida * 0.5, vida), cor,
                random.uniform(tamanho * 0.5, tamanho), arrasto=0.5,
            ))

    def confetes(self, largura, quantidade=140):
        cores = [(255, 210, 90), (255, 110, 120), (120, 200, 255), (140, 255, 160), (210, 140, 255)]
        for _ in range(quantidade):
            self.adicionar(Confete(random.uniform(0, largura), random.uniform(380, 520),
                                   random.choice(cores)))

    def atualizar(self, dt):
        for particula in self.particulas:
            particula.atualizar(dt)
        self.particulas = [p for p in self.particulas if p.viva]

    def desenhar(self, tela):
        for particula in self.particulas:
            particula.desenhar(tela)


class Ambiente:
    """Partículas de ambiente que flutuam pela tela (vagalumes, brasas)."""

    def __init__(self, largura, altura, cor, quantidade=40, subindo=True):
        self.largura, self.altura = largura, altura
        self.cor = cor
        self.subindo = subindo
        self.itens = [self._novo(aleatorio=True) for _ in range(quantidade)]

    def _novo(self, aleatorio=False):
        y = random.uniform(0, self.altura) if aleatorio else self.altura + 10
        return {
            "x": random.uniform(0, self.largura),
            "y": y,
            "v": random.uniform(12, 45),
            "fase": random.uniform(0, math.tau),
            "tamanho": random.uniform(2, 5),
        }

    def atualizar(self, dt):
        for i, item in enumerate(self.itens):
            item["y"] -= item["v"] * dt if self.subindo else -item["v"] * dt * 0.3
            item["fase"] += dt * 1.6
            item["x"] += math.sin(item["fase"]) * 14 * dt
            if item["y"] < -10:
                self.itens[i] = self._novo()

    def desenhar(self, tela):
        for item in self.itens:
            intensidade = 0.55 + 0.45 * math.sin(item["fase"] * 2.1)
            desenhar_brilho(tela, (item["x"], item["y"]), item["tamanho"] * 3, self.cor, intensidade)


class TextoFlutuante:
    """Número de dano/cura que salta e sobe desaparecendo."""

    def __init__(self, texto, x, y, cor, tamanho=46, duracao=1.2):
        self.texto = texto
        self.x, self.y = x, max(230, y)
        self.cor = cor
        self.duracao = duracao
        self.tempo = 0.0
        fonte = Fontes.titulo(tamanho)
        self.imagem = fonte.render(texto, True, cor)
        self.sombra = fonte.render(texto, True, (10, 6, 16))

    @property
    def vivo(self):
        return self.tempo < self.duracao

    def atualizar(self, dt):
        self.tempo += dt

    def desenhar(self, tela):
        t = self.tempo / self.duracao
        escala = 1.6 - 0.6 * min(1.0, t * 6) if t < 0.17 else 1.0
        y = self.y - 70 * (1 - (1 - t) ** 2)
        alfa = 255 if t < 0.7 else int(255 * (1 - (t - 0.7) / 0.3))

        contorno = [(-2, 0), (2, 0), (0, -2), (0, 2), (3, 3)]
        for imagem, deslocamento in [(self.sombra, d) for d in contorno] + [(self.imagem, (0, 0))]:
            img = imagem
            if escala != 1.0:
                img = pygame.transform.smoothscale_by(imagem, escala)
            img.set_alpha(alfa)
            tela.blit(img, img.get_rect(center=(self.x + deslocamento[0], y + deslocamento[1])))


class Projetil:
    """Objeto que voa de um ponto a outro e chama ``ao_chegar`` no impacto."""

    def __init__(self, tipo, origem, destino, duracao, ao_chegar, particulas):
        self.tipo = tipo  # "flecha", "fogo", "arcano"
        self.origem = pygame.Vector2(origem)
        self.destino = pygame.Vector2(destino)
        self.duracao = duracao
        self.ao_chegar = ao_chegar
        self.particulas = particulas
        self.tempo = 0.0
        self.ativo = True

    @property
    def posicao(self):
        t = min(1.0, self.tempo / self.duracao)
        pos = self.origem.lerp(self.destino, t)
        altura_arco = 60 if self.tipo == "flecha" else 25
        pos.y -= math.sin(t * math.pi) * altura_arco
        return pos

    def atualizar(self, dt):
        if not self.ativo:
            return
        self.tempo += dt
        pos = self.posicao
        if self.tipo == "fogo":
            for _ in range(3):
                self.particulas.adicionar(Particula(
                    pos.x, pos.y, random.uniform(-40, 40), random.uniform(-40, 40),
                    random.uniform(0.2, 0.45), random.choice([(255, 150, 40), (255, 90, 30), (255, 220, 120)]),
                    random.uniform(5, 10), arrasto=3,
                ))
        elif self.tipo == "arcano":
            self.particulas.adicionar(Particula(
                pos.x, pos.y, random.uniform(-30, 30), random.uniform(-30, 30),
                0.35, (150, 120, 255), 5, arrasto=3,
            ))
        if self.tempo >= self.duracao:
            self.ativo = False
            self.ao_chegar()

    def desenhar(self, tela):
        if not self.ativo:
            return
        pos = self.posicao
        if self.tipo == "flecha":
            t = min(1.0, self.tempo / self.duracao)
            direcao = pygame.Vector2(self.destino - self.origem).normalize()
            direcao.y -= math.cos(t * math.pi) * 0.35
            direcao = direcao.normalize()
            cauda = pos - direcao * 46
            pygame.draw.line(tela, (110, 74, 40), cauda, pos, 4)
            normal = pygame.Vector2(-direcao.y, direcao.x)
            ponta = [pos + direcao * 12, pos + normal * 6, pos - normal * 6]
            pygame.draw.polygon(tela, (220, 226, 236), ponta)
            for lado in (1, -1):
                pena = [cauda, cauda + direcao * 12 + normal * 8 * lado, cauda + direcao * 16]
                pygame.draw.polygon(tela, (230, 70, 70), pena)
        elif self.tipo == "fogo":
            desenhar_brilho(tela, pos, 46, (255, 120, 30))
            pygame.draw.circle(tela, (255, 230, 160), pos, 11)
        else:
            desenhar_brilho(tela, pos, 30, (140, 110, 255))
            pygame.draw.circle(tela, (230, 220, 255), pos, 7)


class Corte:
    """Arco luminoso de golpe de espada/garra."""

    def __init__(self, x, y, cor=(255, 255, 255), raio=90, duracao=0.28, espelhado=False, garras=1):
        self.x, self.y = x, y
        self.cor = cor
        self.raio = raio
        self.duracao = duracao
        self.espelhado = espelhado
        self.garras = garras
        self.tempo = 0.0

    @property
    def vivo(self):
        return self.tempo < self.duracao

    def atualizar(self, dt):
        self.tempo += dt

    def desenhar(self, tela):
        t = self.tempo / self.duracao
        superficie = pygame.Surface((self.raio * 3, self.raio * 3), pygame.SRCALPHA)
        centro = self.raio * 1.5
        alfa = int(255 * (1 - t))
        for garra in range(self.garras):
            deslocamento = (garra - (self.garras - 1) / 2) * 26
            inicio = -2.4 + t * 0.4
            fim = inicio + 0.4 + 1.9 * min(1.0, t * 3)
            pontos_externos, pontos_internos = [], []
            passos = 18
            for i in range(passos + 1):
                a = inicio + (fim - inicio) * i / passos
                espessura = math.sin(i / passos * math.pi) * 14 + 1
                r = self.raio + deslocamento
                pontos_externos.append((centro + math.cos(a) * r, centro + math.sin(a) * r))
                pontos_internos.append((centro + math.cos(a) * (r - espessura),
                                        centro + math.sin(a) * (r - espessura)))
            pygame.draw.polygon(superficie, (*self.cor, alfa), pontos_externos + pontos_internos[::-1])
        if self.espelhado:
            superficie = pygame.transform.flip(superficie, True, False)
        tela.blit(superficie, (self.x - centro, self.y - centro), special_flags=pygame.BLEND_ADD)


class Anel:
    """Onda circular que se expande (cura, impacto de magia)."""

    def __init__(self, x, y, cor, raio_final=120, duracao=0.6, espessura=6):
        self.x, self.y = x, y
        self.cor = cor
        self.raio_final = raio_final
        self.duracao = duracao
        self.espessura = espessura
        self.tempo = 0.0

    @property
    def vivo(self):
        return self.tempo < self.duracao

    def atualizar(self, dt):
        self.tempo += dt

    def desenhar(self, tela):
        t = self.tempo / self.duracao
        raio = int(self.raio_final * (1 - (1 - t) ** 3))
        if raio < 2:
            return
        superficie = pygame.Surface((raio * 2 + 4, raio * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(superficie, (*self.cor, int(255 * (1 - t))), (raio + 2, raio + 2), raio,
                           max(1, int(self.espessura * (1 - t)) + 1))
        tela.blit(superficie, (self.x - raio - 2, self.y - raio - 2), special_flags=pygame.BLEND_ADD)


class Tremor:
    """Tremor de câmera que diminui com o tempo."""

    def __init__(self):
        self.intensidade = 0.0

    def adicionar(self, intensidade):
        self.intensidade = max(self.intensidade, intensidade)

    def atualizar(self, dt):
        self.intensidade = max(0.0, self.intensidade - dt * 40)

    @property
    def deslocamento(self):
        if self.intensidade <= 0:
            return 0, 0
        i = self.intensidade
        return random.uniform(-i, i), random.uniform(-i, i)
