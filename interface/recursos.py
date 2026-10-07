"""Fontes e efeitos sonoros.

Os sons são sintetizados em tempo de execução (ondas senoidais, quadradas e
ruído), então o projeto não depende de nenhum arquivo de áudio externo.
"""

import math
import random
from array import array

import pygame

FONTES_TITULO = "georgia,cambria,palatinolinotype,bookantiqua,dejavuserif,serif"
FONTES_TEXTO = "segoeui,inter,helveticaneue,arial,dejavusans,freesans"


class Fontes:
    """Cria (e guarda em cache) as fontes usadas na interface."""

    _cache = {}

    @classmethod
    def titulo(cls, tamanho):
        return cls._obter(FONTES_TITULO, tamanho, True)

    @classmethod
    def texto(cls, tamanho, negrito=False):
        return cls._obter(FONTES_TEXTO, tamanho, negrito)

    @classmethod
    def _obter(cls, nomes, tamanho, negrito):
        chave = (nomes, tamanho, negrito)
        if chave not in cls._cache:
            cls._cache[chave] = pygame.font.SysFont(nomes, tamanho, bold=negrito)
        return cls._cache[chave]


class Sons:
    """Biblioteca de efeitos sonoros gerados por código."""

    def __init__(self):
        self.ativo = True
        self.sons = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.frequencia, _, self.canais = pygame.mixer.get_init()
            self._criar_sons()
        except (pygame.error, TypeError):
            # Sem placa de som (ou mixer indisponível): o jogo segue mudo.
            self.ativo = False

    def tocar(self, nome, volume=1.0):
        if self.ativo and nome in self.sons:
            som = self.sons[nome]
            som.set_volume(volume)
            som.play()

    def alternar(self):
        if self.sons:
            self.ativo = not self.ativo
            if not self.ativo:
                pygame.mixer.stop()
        return self.ativo

    # ------------------------------------------------------------------
    # Síntese
    # ------------------------------------------------------------------
    def _onda(self, duracao, freq_ini, freq_fim=None, forma="seno",
              volume=0.5, ataque=0.005, ruido=0.0, vibrato=0.0):
        freq_fim = freq_fim if freq_fim is not None else freq_ini
        total = max(1, int(self.frequencia * duracao))
        amostras = []
        fase = 0.0
        for i in range(total):
            t = i / total
            freq = freq_ini + (freq_fim - freq_ini) * t
            if vibrato:
                freq *= 1 + 0.03 * math.sin(i / self.frequencia * vibrato * math.tau)
            fase += freq / self.frequencia
            if forma == "quadrada":
                valor = 1.0 if (fase % 1.0) < 0.5 else -1.0
            elif forma == "serra":
                valor = 2.0 * (fase % 1.0) - 1.0
            else:
                valor = math.sin(fase * math.tau)
            if ruido:
                valor = valor * (1 - ruido) + random.uniform(-1, 1) * ruido

            envelope = min(1.0, (i / self.frequencia) / ataque) * (1 - t) ** 2
            amostras.append(valor * envelope * volume)
        return amostras

    @staticmethod
    def _mixar(*faixas):
        tamanho = max(len(f) for f in faixas)
        resultado = [0.0] * tamanho
        for faixa in faixas:
            for i, valor in enumerate(faixa):
                resultado[i] += valor
        return resultado

    def _sequencia(self, notas, duracao_nota, forma="seno", volume=0.35):
        amostras = []
        for freq in notas:
            amostras.extend(self._onda(duracao_nota, freq, forma=forma, volume=volume))
        return amostras

    def _para_som(self, amostras):
        dados = array("h")
        for valor in amostras:
            inteiro = int(max(-1.0, min(1.0, valor)) * 32000)
            dados.extend([inteiro] * self.canais)
        return pygame.mixer.Sound(buffer=dados.tobytes())

    def _criar_sons(self):
        receitas = {
            "clique": lambda: self._onda(0.05, 900, 1200, volume=0.25),
            "hover": lambda: self._onda(0.03, 1400, 1600, volume=0.08),
            "golpe": lambda: self._mixar(
                self._onda(0.18, 400, 60, ruido=0.8, volume=0.55),
                self._onda(0.2, 140, 60, volume=0.5),
            ),
            "flecha": lambda: self._mixar(
                self._onda(0.22, 1800, 500, ruido=0.6, volume=0.3),
                self._onda(0.1, 220, 180, forma="quadrada", volume=0.12),
            ),
            "magia": lambda: self._mixar(
                self._onda(0.5, 260, 980, vibrato=14, volume=0.35),
                self._onda(0.5, 520, 1960, volume=0.12),
            ),
            "explosao": lambda: self._mixar(
                self._onda(0.5, 220, 40, ruido=0.9, volume=0.6),
                self._onda(0.4, 90, 40, volume=0.5),
            ),
            "dano": lambda: self._onda(0.2, 220, 70, forma="quadrada", volume=0.25),
            "cura": lambda: self._sequencia([523, 659, 784, 1047], 0.09, volume=0.3),
            "rugido": lambda: self._mixar(
                self._onda(0.9, 120, 60, forma="serra", ruido=0.5, vibrato=9, volume=0.4),
                self._onda(0.9, 80, 50, ruido=0.7, volume=0.4),
            ),
            "vitoria": lambda: self._sequencia(
                [523, 659, 784, 659, 784, 1047, 1047], 0.13, forma="quadrada", volume=0.18
            ),
            "derrota": lambda: self._sequencia(
                [392, 370, 349, 330, 262], 0.22, forma="serra", volume=0.18
            ),
            "fuga": lambda: self._onda(0.35, 700, 200, forma="quadrada", volume=0.15),
        }
        for nome, receita in receitas.items():
            self.sons[nome] = self._para_som(receita())
