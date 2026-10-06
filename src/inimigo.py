from .personagem import Personagem


class Inimigo(Personagem):

    def __init__(self, nome, vida, ataque, defesa):
        super().__init__(
            nome=nome,
            vida=vida,
            ataque=ataque,
            defesa=defesa
        )

    def atacar(self, alvo):
        print(f"{self.nome} está atacando {alvo.nome}!")
        alvo.receber_dano(self.ataque)



class InimigoEspecial(Inimigo):

    def __init__(self, nome, vida, ataque, defesa, habilidade_especial):
        super().__init__(nome, vida, ataque, defesa)
        self.habilidade_especial = habilidade_especial

    def usar_habilidade_especial(self, alvo):
       print(f"{self.nome} está usando {self.habilidade_especial} em {alvo.nome}!")
    pass


class ChefeFinal(InimigoEspecial):

    def __init__(self, nome, vida, ataque, defesa, habilidade_especial):
        super().__init__(nome, vida, ataque, defesa, habilidade_especial)

    def atacar(self, alvo):
        print(f"{self.nome} está atacando {alvo.nome} com um ataque devastador! ")
        alvo.receber_dano(self.ataque * 3)


class CondicaoVitoria:

    def condicao_vitoria(inimigo):
        if inimigo.vida <= 0:
            print("Vitória! O inimigo foi derrotado!")
            return True

        return False
        

