from src.guerreiro import Guerreiro


def test_guerreiro_esta_vivo():

    guerreiro = Guerreiro("Arthur")

    assert guerreiro.esta_vivo() is True


def test_personagem_recebe_dano():
    guerreiro = Guerreiro("Arthur")

    guerreiro.receber_dano(20)

    assert guerreiro.vida == 115


def test_personagem_morre():
    # TODO
    pass


def test_guerreiro_ataca():
    # TODO
    pass
