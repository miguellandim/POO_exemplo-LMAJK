from src.guerreiro import Guerreiro
from src.inimigo import Inimigo
import pytest

def test_personagem_recebe_dano():
    guerreiro = Guerreiro("Arthur")  # vida 120, defesa 15
    guerreiro.receber_dano(35)
    assert guerreiro.vida == 100


def test_dano_considera_defesa_de_outros_personagens():
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)
    goblin.receber_dano(20)
    assert goblin.vida == 85


def test_dano_minimo_e_1():
    guerreiro = Guerreiro("Arthur")
    guerreiro.receber_dano(10)
    assert guerreiro.vida == 119


def test_personagem_morre():
    guerreiro = Guerreiro("Arthur")
    guerreiro.receber_dano(1000)
    assert guerreiro.vida == 0
    assert guerreiro.esta_vivo() is False


def test_dano_negativo_levanta_erro():
    guerreiro = Guerreiro("Arthur")
    with pytest.raises(ValueError):
        guerreiro.receber_dano(-5)


def test_guerreiro_ataca():
    # TODO
    pass
