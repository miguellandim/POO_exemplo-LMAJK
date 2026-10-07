from .personagem import Personagem

class Mago(Personagem):

    def __init__(self, nome):
        super().__init__(
            nome=nome,
            vida=80,
            ataque=30,
            defesa=5
        )

        self.mana = 100

    def atacar(self, alvo):
        print("O",self.nome,"lançou um ataque comum em", alvo.nome)
        alvo.receber_dano(self.ataque)
    

    def usar_magia(self, alvo):
        custo_mana = 20

        if self.mana < custo_mana:
            print("O mago não possui mana suficiente.")
            return

        # A magia ignora a defesa do alvo
        dano = int(self.ataque * 1.5)

        self.mana -= custo_mana
        alvo.vida = max(0, alvo.vida - dano)

        print(
            f"{self.nome} lançou uma magia em {alvo.nome} e causou {dano} de dano! "
            f"(Vida de {alvo.nome}: {alvo.vida} | Mana de {self.nome}: {self.mana})"
        )