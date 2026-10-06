from guerreiro import Guerreiro
from inimigo import CondicaoVitoria, Inimigo, InimigoEspecial
from batalha import Batalha
from mago import Mago
from arqueiro import Arqueiro
from item import Item, PocaoDeVida



    jogador = Guerreiro("GUTIN O DOMINADOR DE GOBLINS")

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


def testar_magia():
    print("\n===== TESTE 1: MAGIA DO MAGO =====")

    merlin = Mago("Merlin")
    gandalf = Mago("Gandalf")

    # Magia normal: gasta 20 de mana e causa 45 de dano (ataque 30 x 1,5)
    merlin.usar_magia(gandalf)
    assert merlin.mana == 80, "A mana deveria cair de 100 para 80"
    assert gandalf.vida == 35, "A vida do Gandalf deveria cair de 80 para 35"

    # Esgotando a mana (80 de mana = 4 magias)
    dragao = Inimigo("Dragão", vida=500, ataque=40, defesa=20)
    for _ in range(4):
        merlin.usar_magia(dragao)
    assert merlin.mana == 0, "A mana deveria chegar a 0"
    assert dragao.vida == 320, "A magia deveria ignorar a defesa (500 - 4 x 45)"

    # Sem mana: não pode causar dano
    merlin.usar_magia(dragao)
    assert dragao.vida == 320, "Sem mana, a magia não pode causar dano"

    print("[OK] Magia do mago funcionando")


def testar_pocao():
    print("\n===== TESTE 2: POÇÃO DE VIDA =====")

    arthur = Guerreiro("Arthur")
    arthur.vida = 50  # simula um personagem ferido

    pocao = PocaoDeVida()
    assert isinstance(pocao, Item), "PocaoDeVida deve herdar de Item"
    assert pocao.nome == "Poção de Vida"
    assert pocao.valor == 30

    pocao.usar(arthur)
    assert arthur.vida == 80, "A poção deveria curar 30 de vida (50 -> 80)"

    # Poção personalizada
    pocao_grande = PocaoDeVida("Poção Grande", 60)
    pocao_grande.usar(arthur)
    assert arthur.vida == 140, "A poção grande deveria curar 60 de vida (80 -> 140)"

    print("[OK] Poção de Vida funcionando")


def testar_arqueiro():
    print("\n===== TESTE 3: ARQUEIRO =====")

    legolas = Arqueiro("Legolas")
    legolas.mostrar_status()
    assert legolas.esta_vivo() is True
    assert (legolas.vida, legolas.ataque, legolas.defesa) == (90, 25, 8)

    # Dano = ataque (25) - defesa do alvo
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)
    legolas.atacar(goblin)
    assert goblin.vida == 80, "Goblin: 25 - 5 de defesa = 20 de dano"

    arthur = Guerreiro("Arthur")
    legolas.atacar(arthur)
    assert arthur.vida == 110, "Guerreiro: 25 - 15 de defesa = 10 de dano"

    # Defesa maior que o ataque: dano mínimo é 0 (nunca cura o alvo)
    golem = Inimigo("Golem", vida=200, ataque=10, defesa=50)
    legolas.atacar(golem)
    assert golem.vida == 200, "Dano não pode ser negativo"

    # Derrotando o alvo: a vida nunca fica abaixo de 0
    while goblin.esta_vivo():
        legolas.atacar(goblin)
    assert goblin.vida == 0
    assert goblin.esta_vivo() is False

    print("[OK] Arqueiro funcionando")


def main():
    testar_magia()
    testar_pocao()
    testar_arqueiro()
    print("\nTodos os testes passaram!")


if __name__ == "__main__":
    main()
    
from guerreiro import Guerreiro
from inimigo import Inimigo
from batalha import Batalha


def testar_ataque_guerreiro():
    guerreiro = Guerreiro("Arthur")
    inimigo = Inimigo("Goblin", vida=50, ataque=10, defesa=5)

    guerreiro.atacar(inimigo)

    # ataque 20 - defesa 5 = 15 de dano
    assert inimigo.vida == 35
    print("OK - ataque do guerreiro")


def testar_turno_inimigo():
    guerreiro = Guerreiro("Arthur")
    inimigo = Inimigo("Goblin", vida=50, ataque=25, defesa=5)
    batalha = Batalha(guerreiro, inimigo)

    batalha.turno_inimigo()

    # ataque 25 - defesa 15 = 10 de dano
    assert guerreiro.vida == 110
    print("OK - turno do inimigo")


def testar_inimigo_morto_nao_ataca():
    guerreiro = Guerreiro("Arthur")
    inimigo = Inimigo("Goblin", vida=0, ataque=25, defesa=5)
    batalha = Batalha(guerreiro, inimigo)

    batalha.turno_inimigo()

    assert guerreiro.vida == 120
    print("OK - inimigo morto nao ataca")


def testar_dano_nao_fica_negativo():
    guerreiro = Guerreiro("Arthur")
    inimigo = Inimigo("Formiga", vida=10, ataque=1, defesa=0)
    batalha = Batalha(guerreiro, inimigo)

    batalha.turno_inimigo()

    # ataque 1 < defesa 15: não causa dano
    assert guerreiro.vida == 120
    print("OK - dano minimo zero")


def testar_morte_do_inimigo():
    guerreiro = Guerreiro("Arthur")
    inimigo = Inimigo("Goblin", vida=10, ataque=10, defesa=0)

    guerreiro.atacar(inimigo)

    assert inimigo.vida == 0
    assert inimigo.esta_vivo() is False
    print("OK - morte do inimigo")


def testar_jogador_morre():
    guerreiro = Guerreiro("Arthur")
    guerreiro.vida = 5
    inimigo = Inimigo("Dragao", vida=200, ataque=100, defesa=50)
    batalha = Batalha(guerreiro, inimigo)

    batalha.turno_inimigo()

    assert guerreiro.vida == 0
    assert guerreiro.esta_vivo() is False
    print("OK - jogador morre")


if __name__ == "__main__":
    testar_ataque_guerreiro()
    testar_turno_inimigo()
    testar_inimigo_morto_nao_ataca()
    testar_dano_nao_fica_negativo()
    testar_morte_do_inimigo()
    testar_jogador_morre()
    print("\nTodos os testes passaram!")