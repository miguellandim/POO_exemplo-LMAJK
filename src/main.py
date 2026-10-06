from guerreiro import Guerreiro
from inimigo import Inimigo, InimigoEspecial
from batalha import Batalha
from mago import Mago



    jogador = Guerreiro("GUTIN O DOMINADOR DE GOBLINS")

    inimigo = Inimigo(
        nome="Goblin",
        vida=100,
        ataque=15,
        defesa=5
    )

    batalha = Batalha(jogador, inimigo)

    batalha.iniciar()
    
    x1 = Inimigo("Goblin", 50, 10, 5)
    x2 = InimigoEspecial("Orc", 100, 20, 10, "Fúria")
    x1.atacar(jogador)
    x2.usar_habilidade_especial(x1) 

if __name__ == "__main__":
    main()


m1=Mago("Merlin")
m2=Mago("Gandalf")
Mago.usar_magia(m1, m2)
m1.mostrar_status()
