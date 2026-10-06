from abc import ABC, abstractmethod


class Personagem(ABC):

    def __init__(self, nome, vida, ataque, defesa):
        self.nome = nome
        self.vida = vida
        self.ataque = ataque
        self.defesa = defesa
        self.inventario = []

    def esta_vivo(self):
        return self.vida > 0

    def receber_dano(self, dano):
        # TODO: calcular o dano considerando a defesa
        pass

    def adicionar_item(self, item):
        """Guarda um item no inventário do personagem."""
        self.inventario.append(item)

    def usar_item(self, indice):
        """Usa (e consome) o item na posição `indice` do inventário.

        Retorna True se o item foi usado e False se o índice for inválido.
        """
        if not 0 <= indice < len(self.inventario):
            return False

        item = self.inventario.pop(indice)
        item.usar(self)
        return True

    @abstractmethod
    def atacar(self, alvo):
        pass

    def mostrar_status(self):
        print(
            f"{self.nome} | "
            f"Vida: {self.vida} | "
            f"Ataque: {self.ataque} | "
            f"Defesa: {self.defesa}"
        )
