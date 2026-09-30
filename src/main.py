from guerreiro import Guerreiro
from inimigo import Inimigo
from batalha import Batalha
from mago import Mago

def main():

    jogador = Guerreiro("GUTIN O DOMINADOR DE GOBLINS")

    inimigo = Inimigo(
        nome="Goblin",
        vida=100,
        ataque=15,
        defesa=5
    )

    batalha = Batalha(jogador, inimigo)

    batalha.iniciar()


if __name__ == "__main__":
    main()


m1=Mago("Merlin")
m2=Mago("Gandalf")
Mago.usar_magia(m1, m2)
m1.mostrar_status()
