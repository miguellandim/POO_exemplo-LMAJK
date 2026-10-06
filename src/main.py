from guerreiro import Guerreiro
from inimigo import CondicaoVitoria, Inimigo, InimigoEspecial
from batalha import Batalha


def main():

    jogador = Guerreiro("Arthur")

    inimigo = Inimigo(
        nome="Goblin",
        vida=100,
        ataque=15,
        defesa=5
    )

    batalha = Batalha(jogador, inimigo)

    batalha.iniciar()

    CondicaoVitoria.condicao_vitoria(inimigo)
    
    x1 = Inimigo("Goblin", 50, 10, 5)
    x2 = InimigoEspecial("Orc", 100, 20, 10, "Fúria")
    x1.atacar(jogador)
    x2.usar_habilidade_especial(x1) 


if __name__ == "__main__":
    main()
