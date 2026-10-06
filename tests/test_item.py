from src.guerreiro import Guerreiro
from src.item import Item


class ItemDeCura(Item):
    """Item falso só para testar o mecanismo de uso de itens."""

    def usar(self, personagem):
        personagem.vida += self.valor


def test_usar_item_aplica_efeito_e_consome_o_item():
    guerreiro = Guerreiro("Arthur")
    guerreiro.vida = 50
    guerreiro.adicionar_item(ItemDeCura("Cura de teste", 30))

    usou = guerreiro.usar_item(0)

    assert usou is True
    assert guerreiro.vida == 80
    assert guerreiro.inventario == []


def test_usar_item_com_indice_invalido():
    guerreiro = Guerreiro("Arthur")

    assert guerreiro.usar_item(0) is False
    assert guerreiro.usar_item(-1) is False