"""Regras da interface gráfica, sem nenhuma dependência do pygame.

Este módulo faz a ponte entre a interface e as classes do jogo (pasta
``src``). Toda a mecânica de combate continua sendo das classes originais
(``Guerreiro.atacar``, ``Mago.usar_magia``, ``Batalha.turno_inimigo``...);
aqui apenas organizamos os turnos e transformamos os ``print`` das classes
em mensagens que a interface consegue mostrar na tela.
"""

import io
from contextlib import redirect_stdout
from dataclasses import dataclass, field

from src.arqueiro import Arqueiro
from src.batalha import Batalha
from src.guerreiro import Guerreiro
from src.inimigo import ChefeFinal, Inimigo, InimigoEspecial
from src.mago import Mago
from src.pocaodevida import PocaoDeVida


@dataclass
class ResultadoAcao:
    """Descreve o que aconteceu em uma ação, para a interface animar."""

    tipo: str  # "ataque", "magia", "item", "habilidade", "fuga"
    ator: str
    alvo: str = ""
    dano: int = 0
    cura: int = 0
    sucesso: bool = True
    mensagens: list = field(default_factory=list)


def capturar_mensagens(acao):
    """Executa ``acao`` e devolve as linhas que ela imprimiu com ``print``."""
    saida = io.StringIO()
    with redirect_stdout(saida):
        acao()

    linhas = []
    for linha in saida.getvalue().splitlines():
        linha = linha.strip()
        # Ignora separadores de console, como "--- TURNO DO INIMIGO ---"
        if linha and not linha.startswith("---") and not linha.startswith("==="):
            linhas.append(linha)
    return linhas


class ControladorBatalha:
    """Controla uma batalha turno a turno usando a classe ``Batalha``."""

    CUSTO_MAGIA = 20
    MANA_MAXIMA = 100
    # A cada quantos turnos um inimigo especial usa a habilidade especial
    INTERVALO_HABILIDADE = 3

    def __init__(self, jogador, inimigo, vida_maxima_jogador=None):
        self.batalha = Batalha(jogador, inimigo)
        self.vida_maxima_jogador = vida_maxima_jogador or jogador.vida
        self.vida_maxima_inimigo = inimigo.vida
        self.turno = 1
        self.fugiu = False
        self.historico = []
        self.dano_causado = 0
        self.dano_recebido = 0
        self.itens_usados = 0

    @property
    def jogador(self):
        return self.batalha.jogador

    @property
    def inimigo(self):
        return self.batalha.inimigo

    # ------------------------------------------------------------------
    # Estado da batalha
    # ------------------------------------------------------------------
    @property
    def terminou(self):
        return (
            self.fugiu
            or not self.jogador.esta_vivo()
            or not self.inimigo.esta_vivo()
        )

    @property
    def vencedor(self):
        """``"jogador"``, ``"inimigo"`` ou ``None`` (batalha em andamento/fuga)."""
        if not self.inimigo.esta_vivo():
            return "jogador"
        if not self.jogador.esta_vivo():
            return "inimigo"
        return None

    @property
    def jogador_e_mago(self):
        return isinstance(self.jogador, Mago)

    @property
    def pode_usar_magia(self):
        return self.jogador_e_mago and self.jogador.mana >= self.CUSTO_MAGIA

    @property
    def tem_itens(self):
        return bool(self.jogador.inventario)

    @property
    def proxima_e_habilidade(self):
        """Indica se o próximo ataque do inimigo será a habilidade especial."""
        return (
            isinstance(self.inimigo, InimigoEspecial)
            and self.turno % self.INTERVALO_HABILIDADE == 0
        )

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------
    def _executar(self, tipo, ator, alvo, acao):
        vida_alvo_antes = alvo.vida if alvo else 0
        vida_ator_antes = ator.vida

        mensagens = capturar_mensagens(acao)

        resultado = ResultadoAcao(
            tipo=tipo,
            ator=ator.nome,
            alvo=alvo.nome if alvo else "",
            dano=max(0, vida_alvo_antes - alvo.vida) if alvo else 0,
            cura=max(0, ator.vida - vida_ator_antes),
            mensagens=mensagens,
        )
        self.historico.extend(mensagens)

        if ator is self.jogador:
            self.dano_causado += resultado.dano
            if tipo == "item":
                self.itens_usados += 1
        else:
            self.dano_recebido += resultado.dano
        return resultado

    def jogador_atacar(self):
        return self._executar(
            "ataque", self.jogador, self.inimigo,
            lambda: self.jogador.atacar(self.inimigo),
        )

    def jogador_usar_magia(self):
        if not self.pode_usar_magia:
            return ResultadoAcao(
                "magia", self.jogador.nome, sucesso=False,
                mensagens=["Mana insuficiente para lançar a magia."],
            )
        return self._executar(
            "magia", self.jogador, self.inimigo,
            lambda: self.jogador.usar_magia(self.inimigo),
        )

    def jogador_usar_item(self, indice):
        if not 0 <= indice < len(self.jogador.inventario):
            return ResultadoAcao(
                "item", self.jogador.nome, sucesso=False,
                mensagens=["Item inválido."],
            )
        return self._executar(
            "item", self.jogador, None,
            lambda: self.jogador.usar_item(indice),
        )

    def turno_inimigo(self):
        """Executa o turno do inimigo e avança o contador de turnos."""
        usar_habilidade = self.proxima_e_habilidade

        def acao():
            if usar_habilidade:
                self.inimigo.usar_habilidade_especial(self.jogador)
            self.batalha.turno_inimigo()

        tipo = "habilidade" if usar_habilidade else "ataque"
        resultado = self._executar(tipo, self.inimigo, self.jogador, acao)
        self.turno += 1
        return resultado

    def fugir(self):
        self.fugiu = True
        mensagem = f"{self.jogador.nome} fugiu da batalha!"
        self.historico.append(mensagem)
        return ResultadoAcao("fuga", self.jogador.nome, mensagens=[mensagem])


# ----------------------------------------------------------------------
# Campanha: heróis disponíveis e sequência de fases
# ----------------------------------------------------------------------
@dataclass
class ClasseHeroi:
    chave: str
    classe: type
    titulo: str
    descricao: str
    especial: str


CLASSES_HEROI = [
    ClasseHeroi(
        "guerreiro", Guerreiro, "Guerreiro",
        "Muita vida e defesa. Aguenta qualquer pancada.",
        "Golpe de espada",
    ),
    ClasseHeroi(
        "mago", Mago, "Mago",
        "Frágil, mas sua magia ignora a defesa do alvo.",
        "Bola de fogo (20 de mana)",
    ),
    ClasseHeroi(
        "arqueiro", Arqueiro, "Arqueiro",
        "Equilibrado e preciso. Flechas certeiras.",
        "Flecha certeira",
    ),
]


@dataclass
class Fase:
    chave: str  # também define o desenho do inimigo
    titulo: str
    descricao: str
    criar_inimigo: object  # função sem argumentos que devolve um Inimigo


FASES = [
    Fase(
        "goblin", "Floresta Sombria",
        "Um goblin saqueador bloqueia a trilha.",
        lambda: Inimigo("Goblin Saqueador", vida=60, ataque=18, defesa=3),
    ),
    Fase(
        "orc", "Fortaleza Orc",
        "O berserker da fortaleza entra em fúria a cada 3 turnos.",
        lambda: InimigoEspecial(
            "Orc Berserker", vida=110, ataque=24, defesa=8,
            habilidade_especial="Fúria Sangrenta",
        ),
    ),
    Fase(
        "dragao", "Covil do Dragão",
        "O Chefe Final. Seus ataques causam o triplo de dano!",
        lambda: ChefeFinal(
            "Dragão Ancestral", vida=200, ataque=7, defesa=5,
            habilidade_especial="Sopro de Fogo",
        ),
    ),
]


class Campanha:
    """Guarda o herói escolhido e o progresso nas fases."""

    POCOES_INICIAIS = 2

    def __init__(self, classe_heroi, nome_heroi, fases=None):
        self.heroi = classe_heroi(nome_heroi)
        self.vida_maxima = self.heroi.vida
        self.fases = fases or FASES
        self.indice_fase = 0
        self.vitorias = 0
        self.total_turnos = 0
        self.total_dano_causado = 0
        self.total_dano_recebido = 0
        self.total_itens_usados = 0
        self._inventario_inicio = []

        for _ in range(self.POCOES_INICIAIS):
            self.heroi.adicionar_item(PocaoDeVida())

    @property
    def fase(self):
        return self.fases[self.indice_fase]

    @property
    def concluida(self):
        return self.indice_fase >= len(self.fases)

    def nova_batalha(self):
        """Recupera o herói (descanso na fogueira) e cria o inimigo da fase."""
        self.heroi.vida = self.vida_maxima
        if isinstance(self.heroi, Mago):
            self.heroi.mana = ControladorBatalha.MANA_MAXIMA
        self._inventario_inicio = list(self.heroi.inventario)
        return ControladorBatalha(self.heroi, self.fase.criar_inimigo(), self.vida_maxima)

    def tentar_novamente(self):
        """Recomeça a fase atual devolvendo os itens gastos na tentativa."""
        self.heroi.inventario = list(self._inventario_inicio)
        return self.nova_batalha()

    def registrar_vitoria(self, batalha=None):
        """Avança de fase e devolve o item recebido como recompensa."""
        if batalha is not None:
            self.total_turnos += batalha.turno
            self.total_dano_causado += batalha.dano_causado
            self.total_dano_recebido += batalha.dano_recebido
            self.total_itens_usados += batalha.itens_usados
        self.vitorias += 1
        self.indice_fase += 1

        if self.indice_fase == len(self.fases) - 1:
            recompensa = PocaoDeVida("Poção Grande", 60)
        else:
            recompensa = PocaoDeVida()
        self.heroi.adicionar_item(recompensa)
        return recompensa
