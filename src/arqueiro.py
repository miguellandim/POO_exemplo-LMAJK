from personagem import Personagem


class Arqueiro(Personagem):

    def __init__(self, nome):
        super().__init__(
            nome=nome,
            vida=90,
            ataque=25,
            defesa=8
        )

    def atacar(self, alvo):
        dano = max(0, self.ataque - alvo.defesa)
        alvo.vida = max(0, alvo.vida - dano)

        print(
            f"{self.nome} atirou uma flecha em {alvo.nome} e causou {dano} de dano! "
            f"(Vida de {alvo.nome}: {alvo.vida})"
        )