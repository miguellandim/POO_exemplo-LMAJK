class Item:

    def __init__(self, nome, valor):
        self.nome = nome
        self.valor = valor

    def usar(self, personagem):
        # TODO: implementar efeito do item
        pass

class PocaoDeVida(Item):

    def __init__(self, nome="Poção de Vida", valor=30):
        super().__init__(nome, valor)

    def usar(self, personagem):
        # valor = pontos de vida restaurados
        personagem.vida += self.valor

        print(
            f"{personagem.nome} usou {self.nome} e recuperou {self.valor} de vida! "
            f"(Vida atual: {personagem.vida})"
        )