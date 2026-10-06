from abc import ABC, abstractmethod


class Personagem(ABC):

    def __init__(self, nome, vida, ataque, defesa):
        self.nome = nome
        self.vida = vida
        self.ataque = ataque
        self.defesa = defesa

    def esta_vivo(self):
        return self.vida > 0

    def receber_dano(self, dano):
        if dano < 0:
            raise ValueError("O dano não pode ser negativo.")

        dano_real = max(1, int(dano - self.defesa))
        self.vida = max(0, self.vida - dano_real)

        print(f"{self.nome} recebeu {dano_real} de dano!")
        return dano_real

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
