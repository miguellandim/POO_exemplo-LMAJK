"""Testes da camada de lógica da interface (não precisam do pygame)."""

from interface.logica import CLASSES_HEROI, Campanha, ControladorBatalha, capturar_mensagens
from src.arqueiro import Arqueiro
from src.guerreiro import Guerreiro
from src.inimigo import Inimigo, InimigoEspecial
from src.mago import Mago
from src.pocaodevida import PocaoDeVida


def test_capturar_mensagens_ignora_separadores():
    def acao():
        print("--- TURNO DO INIMIGO ---")
        print("Goblin atacou!")

    assert capturar_mensagens(acao) == ["Goblin atacou!"]


def test_ataque_do_jogador_registra_dano_e_mensagens():
    batalha = ControladorBatalha(Guerreiro("Arthur"), Inimigo("Goblin", vida=50, ataque=10, defesa=5))

    resultado = batalha.jogador_atacar()

    assert resultado.dano == 15
    assert batalha.inimigo.vida == 35
    assert batalha.dano_causado == 15
    assert resultado.mensagens


def test_magia_so_funciona_com_mana():
    mago = Mago("Merlin")
    mago.mana = 10
    batalha = ControladorBatalha(mago, Inimigo("Goblin", vida=100, ataque=10, defesa=5))

    assert batalha.pode_usar_magia is False
    resultado = batalha.jogador_usar_magia()

    assert resultado.sucesso is False
    assert batalha.inimigo.vida == 100


def test_usar_item_cura_e_consome():
    heroi = Arqueiro("Legolas")
    heroi.vida = 40
    heroi.adicionar_item(PocaoDeVida())
    batalha = ControladorBatalha(heroi, Inimigo("Goblin", vida=50, ataque=10, defesa=5), vida_maxima_jogador=90)

    resultado = batalha.jogador_usar_item(0)

    assert resultado.cura == 30
    assert heroi.vida == 70
    assert heroi.inventario == []
    assert batalha.jogador_usar_item(0).sucesso is False


def test_inimigo_especial_usa_habilidade_a_cada_tres_turnos():
    batalha = ControladorBatalha(
        Guerreiro("Arthur"), InimigoEspecial("Orc", vida=100, ataque=20, defesa=5, habilidade_especial="Fúria")
    )
    tipos = [batalha.turno_inimigo().tipo for _ in range(6)]

    assert tipos == ["ataque", "ataque", "habilidade", "ataque", "ataque", "habilidade"]


def test_vencedor_e_fuga():
    batalha = ControladorBatalha(Guerreiro("Arthur"), Inimigo("Goblin", vida=10, ataque=10, defesa=0))
    assert batalha.terminou is False

    batalha.jogador_atacar()

    assert batalha.terminou is True
    assert batalha.vencedor == "jogador"

    outra = ControladorBatalha(Guerreiro("Arthur"), Inimigo("Goblin", vida=10, ataque=10, defesa=0))
    outra.fugir()
    assert outra.terminou is True
    assert outra.vencedor is None


def test_campanha_avanca_e_da_recompensas():
    campanha = Campanha(Guerreiro, "Arthur")
    assert len(campanha.heroi.inventario) == Campanha.POCOES_INICIAIS

    batalha = campanha.nova_batalha()
    batalha.inimigo.vida = 0
    recompensa = campanha.registrar_vitoria(batalha)

    assert campanha.indice_fase == 1
    assert isinstance(recompensa, PocaoDeVida)
    assert len(campanha.heroi.inventario) == Campanha.POCOES_INICIAIS + 1


def test_tentar_novamente_devolve_itens_e_vida():
    campanha = Campanha(Mago, "Merlin")
    batalha = campanha.nova_batalha()
    batalha.jogador_usar_magia()
    batalha.jogador_usar_item(0)
    campanha.heroi.vida = 0

    nova = campanha.tentar_novamente()

    assert len(nova.jogador.inventario) == Campanha.POCOES_INICIAIS
    assert nova.jogador.vida == campanha.vida_maxima
    assert nova.jogador.mana == ControladorBatalha.MANA_MAXIMA


def test_toda_classe_de_heroi_consegue_vencer_a_campanha():
    """Estratégia simples: cura com pouca vida, magia quando puder, senão ataca."""
    for info in CLASSES_HEROI:
        campanha = Campanha(info.classe, "Teste")
        while not campanha.concluida:
            batalha = campanha.nova_batalha()
            while not batalha.terminou:
                if batalha.jogador.vida < 40 and batalha.tem_itens:
                    batalha.jogador_usar_item(len(batalha.jogador.inventario) - 1)
                elif batalha.pode_usar_magia:
                    batalha.jogador_usar_magia()
                else:
                    batalha.jogador_atacar()
                if not batalha.terminou:
                    batalha.turno_inimigo()
            assert batalha.vencedor == "jogador", f"{info.titulo} perdeu em {campanha.fase.titulo}"
            campanha.registrar_vitoria(batalha)
