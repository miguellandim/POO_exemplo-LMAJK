from personagem import Personagem

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
        print("O",self.nome,"lançou deu um ataque comum em", alvo.nome)
        alvo.receber_dano(self.ataque)
    

    def usar_magia(self, alvo):
        print(f"{self.nome} lança uma magia em {alvo.nome}!")
        self.mana -= 20
        alvo.receber_dano(self.ataque * 1.5)
        
        pass

        if self.mana <= 0:
            print("O mago não possui mana suficiente.")
            return

        pass
