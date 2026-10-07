from abc import ABC, abstractmethod


class Cena(ABC):
    """Classe base de todas as telas do jogo (menu, seleção, batalha...)."""

    # Quando True, a tecla M é usada para digitar e não para silenciar o som
    captura_texto = False

    def __init__(self, jogo):
        self.jogo = jogo
        self.botoes = []
        self.tempo = 0.0

    @property
    def sons(self):
        return self.jogo.sons

    def tratar_evento(self, evento):
        for botao in self.botoes:
            if botao.tratar_evento(evento):
                return True
        return False

    def atualizar(self, dt):
        self.tempo += dt
        for botao in self.botoes:
            botao.atualizar(dt)

    def desenhar_botoes(self, tela):
        for botao in self.botoes:
            botao.desenhar(tela)

    @abstractmethod
    def desenhar(self, tela):
        ...
