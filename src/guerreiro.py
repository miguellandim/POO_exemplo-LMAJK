from personagem import Personagem


class Guerreiro(Personagem):

    def __init__(self, nome):
        super().__init__(
            nome=nome,
            vida=120,
            ataque=20,
            defesa=15
        )

    def atacar(self, alvo):
          def atacar(self, alvo):
        dano_real = alvo.receber_dano(self.ataque)
        print(f"{self.nome} atacou {alvo.nome} e causou {dano_real} de dano!")
       
        return dano_real
        pass
