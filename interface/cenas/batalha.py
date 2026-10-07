import math
import random

import pygame

from src.inimigo import ChefeFinal, InimigoEspecial

from .. import config as c
from ..cenario import Cenario
from ..componentes import (Botao, BarraStatus, PainelLog, desenhar_painel, desenhar_texto, icone)
from ..efeitos import (Anel, Corte, Particula, Projetil, SistemaParticulas, TextoFlutuante, Tremor,
                       desenhar_brilho)
from ..recursos import Fontes
from ..sprites import SpritePersonagem
from .base import Cena
from .mapa import chave_do_heroi


class Agenda:
    """Executa funções depois de um tempo (encadeia as animações do turno)."""

    def __init__(self):
        self.tarefas = []

    def agendar(self, atraso, funcao):
        self.tarefas.append([atraso, funcao])

    def atualizar(self, dt):
        prontas = []
        for tarefa in self.tarefas:
            tarefa[0] -= dt
            if tarefa[0] <= 0:
                prontas.append(tarefa)
        for tarefa in prontas:
            self.tarefas.remove(tarefa)
            tarefa[1]()


class Faixa:
    """Texto grande que atravessa a tela ("SEU TURNO", nome da habilidade...)."""

    def __init__(self, texto, cor, duracao=1.1, subtitulo=""):
        self.texto = texto
        self.cor = cor
        self.subtitulo = subtitulo
        self.duracao = duracao
        self.tempo = 0.0

    @property
    def viva(self):
        return self.tempo < self.duracao

    def atualizar(self, dt):
        self.tempo += dt

    def desenhar(self, tela):
        t = self.tempo / self.duracao
        if t < 0.2:
            entrada = 1 - (1 - t / 0.2) ** 3
            alfa = entrada
            x = c.LARGURA / 2 - (1 - entrada) * 300
        elif t > 0.75:
            saida = (t - 0.75) / 0.25
            alfa = 1 - saida
            x = c.LARGURA / 2 + saida ** 2 * 300
        else:
            alfa, x = 1.0, c.LARGURA / 2
        y = 300
        faixa = pygame.Surface((c.LARGURA, 110), pygame.SRCALPHA)
        for i in range(110):
            intensidade = 1 - abs(i - 55) / 55
            faixa.fill((0, 0, 0, int(170 * intensidade * alfa)), (0, i, c.LARGURA, 1))
        tela.blit(faixa, (0, y - 55))
        desenhar_texto(tela, self.texto, Fontes.titulo(58), self.cor, (x, y - (8 if self.subtitulo else 0)),
                       alfa=int(255 * alfa))
        if self.subtitulo:
            desenhar_texto(tela, self.subtitulo, Fontes.texto(18, negrito=True), c.TEXTO, (x, y + 34),
                           alfa=int(255 * alfa))


TIPO_INIMIGO = {
    "ChefeFinal": ("CHEFE FINAL  •  DANO x3", (255, 120, 60)),
    "InimigoEspecial": ("INIMIGO ESPECIAL", c.ROXO),
    "Inimigo": ("INIMIGO", c.TEXTO_SUAVE),
}


class CenaBatalha(Cena):
    """A batalha por turnos. Toda a regra vem de ``ControladorBatalha``."""

    def __init__(self, jogo, controlador):
        super().__init__(jogo)
        self.campanha = jogo.campanha
        self.ctrl = controlador
        self.fase = self.campanha.fase
        self.cenario = Cenario(self.fase.chave)
        self.info_heroi = chave_do_heroi(self.ctrl.jogador)
        self.cor_heroi = c.CORES_CLASSE[self.info_heroi.chave]

        self.sprite_heroi = SpritePersonagem(self.info_heroi.chave, c.HEROI_X, c.CHAO_Y, True, self.cor_heroi)
        self.sprite_inimigo = SpritePersonagem(self.fase.chave, c.INIMIGO_X, c.CHAO_Y, False)

        self.particulas = SistemaParticulas()
        self.efeitos = []  # textos flutuantes, cortes e anéis
        self.projeteis = []
        self.faixas = []
        self.tremor = Tremor()
        self.agenda = Agenda()
        self.sopro = 0.0
        self.furia = 0.0

        self.estado = "jogador"  # "jogador", "animando", "fim"
        self.menu_itens = False
        self.botoes_itens = []
        self.resultado_final = None
        self.botoes_fim = []
        self.recompensa = None

        self._criar_hud()
        self._criar_botoes()

        self.log.adicionar(f"{self.ctrl.inimigo.nome} apareceu! {self.fase.descricao}", c.OURO)
        self.faixas.append(Faixa(self.fase.titulo.upper(), c.OURO, 1.6,
                                 f"Fase {self.campanha.indice_fase + 1} de {len(self.campanha.fases)}"))
        if isinstance(self.ctrl.inimigo, ChefeFinal):
            self.sons.tocar("rugido")

    # ------------------------------------------------------------------
    # Montagem da interface
    # ------------------------------------------------------------------
    def _criar_hud(self):
        jogador, inimigo = self.ctrl.jogador, self.ctrl.inimigo
        self.painel_heroi = pygame.Rect(24, 18, 410, 150 if self.ctrl.jogador_e_mago else 122)
        self.painel_inimigo = pygame.Rect(c.LARGURA - 434, 18, 410, 122)
        self.barra_vida_heroi = BarraStatus((self.painel_heroi.x + 46, self.painel_heroi.y + 58, 340, 22),
                                            c.VIDA, c.VIDA_ESCURA, self.ctrl.vida_maxima_jogador, jogador.vida)
        self.barra_mana = None
        if self.ctrl.jogador_e_mago:
            self.barra_mana = BarraStatus((self.painel_heroi.x + 46, self.painel_heroi.y + 88, 340, 18),
                                          c.MANA, c.MANA_ESCURA, self.ctrl.MANA_MAXIMA, jogador.mana, "gota")
        self.barra_vida_inimigo = BarraStatus((self.painel_inimigo.x + 46, self.painel_inimigo.y + 58, 340, 22),
                                              c.VIDA, c.VIDA_ESCURA, self.ctrl.vida_maxima_inimigo, inimigo.vida)
        self.barras = [b for b in (self.barra_vida_heroi, self.barra_mana, self.barra_vida_inimigo) if b]
        self.log = PainelLog((c.LARGURA - 560, c.ALTURA - 150, 536, 132), max_linhas=4)

    def _criar_botoes(self):
        jogador = self.ctrl.jogador
        self.botao_atacar = Botao((0, 0, 150, 58), "Atacar", self.acao_atacar, pygame.K_1, "espada",
                                  cor=(236, 104, 84), tamanho_fonte=21, sons=self.sons,
                                  dica=f"Ataque básico: {jogador.ataque} de ATQ contra "
                                       f"{self.ctrl.inimigo.defesa} de DEF do inimigo.")
        self.botao_magia = Botao((0, 0, 150, 58), "Magia", self.acao_magia, pygame.K_2, "magia",
                                 cor=c.ROXO, tamanho_fonte=21, sons=self.sons,
                                 dica=f"Bola de fogo: {int(jogador.ataque * 1.5)} de dano, ignora a defesa. "
                                      f"Custa {self.ctrl.CUSTO_MAGIA} de mana.")
        self.botao_itens = Botao((0, 0, 150, 58), "Itens", self.abrir_itens, pygame.K_3, "pocao",
                                 cor=c.CURA, tamanho_fonte=21, sons=self.sons,
                                 dica="Use uma poção para recuperar vida (gasta o turno).")
        self.botao_fugir = Botao((0, 0, 150, 58), "Fugir", self.acao_fugir, pygame.K_4, "fuga",
                                 cor=(150, 150, 176), tamanho_fonte=21, sons=self.sons,
                                 dica="Abandona a batalha e volta para o mapa.")
        self.botao_magia.visivel = self.ctrl.jogador_e_mago

        visiveis = [b for b in (self.botao_atacar, self.botao_magia, self.botao_itens, self.botao_fugir)
                    if b.visivel]
        self.painel_acoes = pygame.Rect(24, c.ALTURA - 150, 680, 132)
        largura = (self.painel_acoes.width - 40 - 12 * (len(visiveis) - 1)) // len(visiveis)
        for i, botao in enumerate(visiveis):
            botao.ret = pygame.Rect(self.painel_acoes.x + 20 + i * (largura + 12), self.painel_acoes.y + 18,
                                    largura, 58)
        self.botoes = [self.botao_atacar, self.botao_magia, self.botao_itens, self.botao_fugir]
        self._atualizar_botoes()

    def _atualizar_botoes(self):
        livre = self.estado == "jogador" and not self.menu_itens
        self.botao_atacar.habilitado = livre
        self.botao_magia.habilitado = livre and self.ctrl.pode_usar_magia
        self.botao_itens.habilitado = livre and self.ctrl.tem_itens
        self.botao_fugir.habilitado = livre
        self.botao_itens.texto = f"Itens ({len(self.ctrl.jogador.inventario)})"

    # ------------------------------------------------------------------
    # Ações do jogador
    # ------------------------------------------------------------------
    def _iniciar_acao(self):
        """Bloqueia novas ações até o turno terminar. Retorna False se já estava ocupado."""
        if self.estado != "jogador":
            return False
        self.estado = "animando"
        self._atualizar_botoes()
        return True

    def acao_atacar(self):
        if not self._iniciar_acao():
            return
        tipo = self.info_heroi.chave
        if tipo == "guerreiro":
            self.sprite_heroi.investir(c.INIMIGO_X - c.HEROI_X - 230, 0.55)
            self.agenda.agendar(0.22, lambda: self._impacto_jogador("corte"))
        else:
            self.sprite_heroi.conjurar(0.4)
            tipo_projetil = "flecha" if tipo == "arqueiro" else "arcano"
            self.sons.tocar("flecha" if tipo == "arqueiro" else "magia", 0.6)
            self.agenda.agendar(0.15, lambda: self._lancar(tipo_projetil, 0.42,
                                                           lambda: self._impacto_jogador(tipo_projetil)))

    def acao_magia(self):
        if not self.ctrl.pode_usar_magia or not self._iniciar_acao():
            return
        self.sprite_heroi.conjurar(0.7)
        self.sons.tocar("magia")
        arma = self.sprite_heroi.ponto("arma")
        self.particulas.subir(arma.x, arma.y + 30, (255, 150, 60), 26, 30, 0.6, 6)
        self.efeitos.append(Anel(arma.x, arma.y, (255, 150, 60), 70, 0.5))
        self.agenda.agendar(0.35, lambda: self._lancar("fogo", 0.6, lambda: self._impacto_jogador("fogo")))

    def abrir_itens(self):
        self.menu_itens = True
        self._atualizar_botoes()
        largura = 440
        self.botoes_itens = []
        for i, item in enumerate(self.ctrl.jogador.inventario[:6]):
            ret = (c.LARGURA // 2 - largura // 2 + 24, 236 + i * 66, largura - 48, 56)
            self.botoes_itens.append(Botao(ret, f"{item.nome}  (+{item.valor})", lambda i=i: self.acao_item(i),
                                           pygame.K_1 + i, "pocao", cor=c.CURA, tamanho_fonte=20,
                                           sons=self.sons))
        self.botoes_itens.append(Botao((c.LARGURA // 2 - 90, 236 + len(self.botoes_itens) * 66 + 6, 180, 48),
                                       "Voltar", self.fechar_itens, pygame.K_ESCAPE, "fuga",
                                       cor=(200, 90, 100), tamanho_fonte=18, sons=self.sons))

    def fechar_itens(self):
        self.menu_itens = False
        self._atualizar_botoes()

    def acao_item(self, indice):
        self.menu_itens = False
        if not self._iniciar_acao():
            return
        resultado = self.ctrl.jogador_usar_item(indice)
        self._registrar(resultado, c.CURA)
        if resultado.sucesso:
            self.sons.tocar("cura")
            self.sprite_heroi.curar()
            centro = self.sprite_heroi.ponto("centro")
            self.particulas.subir(centro.x, centro.y + 40, c.CURA, 34, 70)
            self.efeitos.append(Anel(centro.x, c.CHAO_Y - 10, c.CURA, 140, 0.7))
            topo = self.sprite_heroi.ponto("topo")
            self.efeitos.append(TextoFlutuante(f"+{resultado.cura}", topo.x, topo.y, c.CURA))
            self.barra_vida_heroi.definir(self.ctrl.jogador.vida)
        self.agenda.agendar(1.0, self._fim_turno_jogador)

    def acao_fugir(self):
        if not self._iniciar_acao():
            return
        resultado = self.ctrl.fugir()
        self._registrar(resultado, c.TEXTO_SUAVE)
        self.sons.tocar("fuga")
        self.sprite_heroi.fugir()
        self.agenda.agendar(1.0, lambda: self._mostrar_fim("fuga"))

    def _lancar(self, tipo, duracao, ao_chegar):
        origem = self.sprite_heroi.ponto("arma")
        destino = self.sprite_inimigo.ponto("centro")
        self.projeteis.append(Projetil(tipo, origem, destino, duracao, ao_chegar, self.particulas))

    def _impacto_jogador(self, tipo):
        if tipo == "fogo":
            resultado = self.ctrl.jogador_usar_magia()
            if self.barra_mana:
                self.barra_mana.definir(self.ctrl.jogador.mana)
        else:
            resultado = self.ctrl.jogador_atacar()
        self._registrar(resultado, c.OURO)

        alvo = self.sprite_inimigo
        centro = alvo.ponto("centro")
        if tipo == "corte":
            self.efeitos.append(Corte(centro.x - 20, centro.y - 10, (255, 240, 200), 100))
            self.sons.tocar("golpe")
        elif tipo == "fogo":
            self.particulas.explosao(centro.x, centro.y, (255, 140, 40), 60, 420, 0.9, 12, 120)
            self.particulas.explosao(centro.x, centro.y, (255, 230, 140), 20, 220, 0.6, 8, 0)
            self.efeitos.append(Anel(centro.x, centro.y, (255, 160, 60), 180, 0.6, 10))
            self.tremor.adicionar(12)
            self.sons.tocar("explosao")
        elif tipo == "flecha":
            self.sons.tocar("golpe", 0.6)
        else:
            self.efeitos.append(Anel(centro.x, centro.y, c.ROXO, 90, 0.4))
            self.sons.tocar("golpe", 0.6)

        self._aplicar_dano(alvo, self.barra_vida_inimigo, self.ctrl.inimigo, resultado.dano, forca=1.2)
        self.agenda.agendar(0.9, self._fim_turno_jogador)

    def _fim_turno_jogador(self):
        if self.ctrl.terminou:
            self._finalizar()
            return
        habilidade = self.ctrl.proxima_e_habilidade
        if habilidade:
            nome = self.ctrl.inimigo.habilidade_especial
            self.faixas.append(Faixa(f"{nome.upper()}!", (255, 90, 70), 1.2,
                                     f"{self.ctrl.inimigo.nome} usa a habilidade especial"))
            self.sons.tocar("rugido")
            self.furia = 1.0
            self.tremor.adicionar(6)
            self.agenda.agendar(1.15, lambda: self._ataque_inimigo(True))
        else:
            self.faixas.append(Faixa("TURNO DO INIMIGO", (255, 120, 110), 0.8))
            self.agenda.agendar(0.75, lambda: self._ataque_inimigo(False))

    # ------------------------------------------------------------------
    # Turno do inimigo
    # ------------------------------------------------------------------
    def _ataque_inimigo(self, habilidade):
        if self.fase.chave == "dragao" and habilidade:
            self.sprite_inimigo.conjurar(0.9)
            self.sopro = 0.8
            self.sons.tocar("explosao", 0.6)
            self.agenda.agendar(0.6, self._impacto_inimigo)
        elif self.fase.chave == "dragao":
            self.sprite_inimigo.investir(200, 0.6)
            self.agenda.agendar(0.24, self._impacto_inimigo)
        else:
            self.sprite_inimigo.investir(c.INIMIGO_X - c.HEROI_X - 240, 0.55)
            self.agenda.agendar(0.22, self._impacto_inimigo)

    def _impacto_inimigo(self):
        resultado = self.ctrl.turno_inimigo()
        self._registrar(resultado, (255, 140, 130))
        self.furia = 0.0
        alvo = self.sprite_heroi
        centro = alvo.ponto("centro")
        chefe = isinstance(self.ctrl.inimigo, ChefeFinal)
        if self.fase.chave == "dragao":
            if resultado.tipo == "habilidade":
                self.particulas.explosao(centro.x, centro.y, (255, 120, 30), 50, 300, 0.8, 10, 100)
            else:
                self.efeitos.append(Corte(centro.x + 10, centro.y - 10, (255, 120, 90), 110,
                                          0.32, espelhado=True, garras=3))
        else:
            self.efeitos.append(Corte(centro.x + 20, centro.y - 10, (255, 170, 150), 90, espelhado=True))
        self.tremor.adicionar(16 if chefe else (10 if resultado.tipo == "habilidade" else 6))
        self.sons.tocar("golpe")
        self.sons.tocar("dano", 0.7)
        self._aplicar_dano(alvo, self.barra_vida_heroi, self.ctrl.jogador, resultado.dano, forca=1.5 if chefe else 1)
        self.agenda.agendar(1.0, self._fim_turno_inimigo)

    def _fim_turno_inimigo(self):
        if self.ctrl.terminou:
            self._finalizar()
            return
        self.estado = "jogador"
        self._atualizar_botoes()
        self.faixas.append(Faixa("SEU TURNO", c.OURO, 0.8))

    # ------------------------------------------------------------------
    # Efeitos compartilhados
    # ------------------------------------------------------------------
    def _registrar(self, resultado, cor):
        for mensagem in resultado.mensagens:
            self.log.adicionar(mensagem, cor)

    def _aplicar_dano(self, sprite, barra, personagem, dano, forca=1.0):
        topo = sprite.ponto("topo")
        if dano > 0:
            sprite.sofrer_dano(forca)
            self.efeitos.append(TextoFlutuante(f"-{dano}", topo.x, topo.y, c.DANO, 52 if dano >= 30 else 44))
            centro = sprite.ponto("centro")
            self.particulas.explosao(centro.x, centro.y, (255, 220, 160), 18, 300, 0.5, 6, 500)
        else:
            self.efeitos.append(TextoFlutuante("DEFENDEU!", topo.x, topo.y, c.TEXTO_SUAVE, 34))
        barra.definir(personagem.vida)

    # ------------------------------------------------------------------
    # Fim da batalha
    # ------------------------------------------------------------------
    def _finalizar(self):
        if self.estado == "fim":
            return
        self.estado = "fim"
        self._atualizar_botoes()
        if self.ctrl.vencedor == "jogador":
            self.sprite_inimigo.morrer()
            self.sons.tocar("vitoria")
            self.recompensa = self.campanha.registrar_vitoria(self.ctrl)
            self.log.adicionar(f"{self.ctrl.inimigo.nome} foi derrotado!", c.CURA)
            self.agenda.agendar(0.6, self.sprite_heroi.comemorar)
            self.agenda.agendar(0.9, lambda: self.particulas.confetes(c.LARGURA))
            self.agenda.agendar(1.3, lambda: self._mostrar_fim("vitoria"))
        else:
            self.sprite_heroi.morrer()
            self.sons.tocar("derrota")
            self.log.adicionar(f"{self.ctrl.jogador.nome} caiu em batalha...", c.DANO)
            self.agenda.agendar(1.5, lambda: self._mostrar_fim("derrota"))

    def _mostrar_fim(self, resultado):
        self.estado = "fim"
        self.resultado_final = resultado
        self._atualizar_botoes()
        centro_x = c.LARGURA // 2
        if resultado == "vitoria":
            texto = "Ver o final" if self.campanha.concluida else "Continuar"
            self.botoes_fim = [Botao((centro_x - 150, 452, 300, 60), texto, self._continuar, pygame.K_RETURN,
                                     "espada", sons=self.sons)]
        elif resultado == "derrota":
            self.botoes_fim = [
                Botao((centro_x - 310, 452, 300, 60), "Tentar de novo", self._tentar_novamente,
                      pygame.K_RETURN, "espada", sons=self.sons),
                Botao((centro_x + 10, 452, 300, 60), "Menu principal", self._ir_menu, pygame.K_ESCAPE,
                      "fuga", cor=(200, 90, 100), sons=self.sons),
            ]
        else:
            self.botoes_fim = [Botao((centro_x - 150, 452, 300, 60), "Voltar ao mapa", self._voltar_mapa,
                                     pygame.K_RETURN, "fuga", sons=self.sons)]

    def _continuar(self):
        if self.campanha.concluida:
            from .final import CenaFinal
            self.jogo.trocar_cena(CenaFinal)
        else:
            from .mapa import CenaMapa
            self.jogo.trocar_cena(CenaMapa, f"Recompensa: você ganhou {self.recompensa.nome} "
                                            f"(+{self.recompensa.valor} de vida)!")

    def _tentar_novamente(self):
        self.jogo.trocar_cena(CenaBatalha, self.campanha.tentar_novamente())

    def _voltar_mapa(self):
        from .mapa import CenaMapa
        self.jogo.trocar_cena(CenaMapa)

    def _ir_menu(self):
        from .menu import CenaMenu
        self.jogo.trocar_cena(CenaMenu)

    # ------------------------------------------------------------------
    # Loop
    # ------------------------------------------------------------------
    def tratar_evento(self, evento):
        if self.resultado_final:
            for botao in self.botoes_fim:
                if botao.tratar_evento(evento):
                    return True
            return False
        if self.menu_itens:
            for botao in self.botoes_itens:
                if botao.tratar_evento(evento):
                    return True
            return False
        return super().tratar_evento(evento)

    def atualizar(self, dt):
        super().atualizar(dt)
        self.cenario.atualizar(dt)
        self.agenda.atualizar(dt)
        self.sprite_heroi.atualizar(dt)
        self.sprite_inimigo.atualizar(dt)
        self.particulas.atualizar(dt)
        self.tremor.atualizar(dt)
        self.log.atualizar(dt)
        for barra in self.barras:
            barra.atualizar(dt)
        for lista in (self.efeitos, self.faixas):
            for efeito in lista:
                efeito.atualizar(dt)
        self.efeitos = [e for e in self.efeitos if e.vivo]
        self.faixas = [f for f in self.faixas if f.viva]
        for projetil in self.projeteis:
            projetil.atualizar(dt)
        self.projeteis = [p for p in self.projeteis if p.ativo]
        for botao in self.botoes_itens if self.menu_itens else []:
            botao.atualizar(dt)
        for botao in self.botoes_fim:
            botao.atualizar(dt)

        if self.sopro > 0:
            self.sopro -= dt
            boca = self.sprite_inimigo.ponto("arma")
            alvo = self.sprite_heroi.ponto("centro")
            direcao = (alvo - boca).normalize()
            for _ in range(7):
                velocidade = direcao.rotate(random.uniform(-9, 9)) * random.uniform(700, 900)
                cor = random.choice([(255, 150, 40), (255, 90, 30), (255, 220, 120)])
                self.particulas.adicionar(Particula(boca.x, boca.y, velocidade.x, velocidade.y,
                                                    random.uniform(0.5, 0.8), cor, random.uniform(8, 16)))

    def desenhar(self, tela):
        deslocamento = self.tremor.deslocamento
        self.cenario.desenhar(tela, deslocamento)

        if self.furia > 0:
            self.sprite_inimigo.desenhar_furia(tela, 0.6 + 0.4 * math.sin(self.tempo * 18), deslocamento)
        self.sprite_inimigo.desenhar(tela, deslocamento)
        self.sprite_heroi.desenhar(tela, deslocamento)
        if self.estado == "jogador" and not self.resultado_final:
            self._seta_turno(tela, self.sprite_heroi)

        for projetil in self.projeteis:
            projetil.desenhar(tela)
        self.particulas.desenhar(tela)
        for efeito in self.efeitos:
            efeito.desenhar(tela)

        self._desenhar_hud(tela)
        for faixa in self.faixas:
            faixa.desenhar(tela)
        if self.menu_itens:
            self._desenhar_menu_itens(tela)
        if self.resultado_final:
            self._desenhar_fim(tela)

    # ------------------------------------------------------------------
    # Desenho da interface
    # ------------------------------------------------------------------
    def _seta_turno(self, tela, sprite):
        topo = sprite.retangulo.top - 18 + math.sin(self.tempo * 5) * 6
        x = sprite.x
        desenhar_brilho(tela, (x, topo), 26, c.OURO, 0.6)
        pygame.draw.polygon(tela, c.OURO, [(x - 12, topo - 10), (x + 12, topo - 10), (x, topo + 6)])

    def _desenhar_painel_personagem(self, tela, ret, personagem, rotulo, cor_rotulo, barras):
        desenhar_painel(tela, ret, alfa=215)
        fonte_nome = Fontes.texto(22, negrito=True)
        nome_ret = desenhar_texto(tela, personagem.nome, fonte_nome, c.TEXTO, (ret.x + 20, ret.y + 28),
                                  ancora="midleft")
        fonte_rotulo = Fontes.texto(12, negrito=True)
        largura = fonte_rotulo.size(rotulo)[0] + 18
        chip = pygame.Rect(nome_ret.right + 12, ret.y + 18, largura, 22)
        if chip.right > ret.right - 12:
            chip.right = ret.right - 12
        pygame.draw.rect(tela, tuple(int(v * 0.35) for v in cor_rotulo), chip, border_radius=11)
        pygame.draw.rect(tela, cor_rotulo, chip, 1, border_radius=11)
        desenhar_texto(tela, rotulo, fonte_rotulo, cor_rotulo, chip.center, sombra=False)
        for barra in barras:
            barra.desenhar(tela)

        y = ret.bottom - 24
        fonte = Fontes.texto(15, negrito=True)
        icone(tela, "espada", (ret.x + 28, y), 16, c.FOGO)
        desenhar_texto(tela, f"ATQ {personagem.ataque}", fonte, c.TEXTO, (ret.x + 42, y), ancora="midleft",
                       sombra=False)
        icone(tela, "escudo", (ret.x + 124, y), 16, c.MANA)
        desenhar_texto(tela, f"DEF {personagem.defesa}", fonte, c.TEXTO, (ret.x + 138, y), ancora="midleft",
                       sombra=False)
        return y

    def _desenhar_hud(self, tela):
        jogador, inimigo = self.ctrl.jogador, self.ctrl.inimigo
        barras = [self.barra_vida_heroi] + ([self.barra_mana] if self.barra_mana else [])
        self._desenhar_painel_personagem(tela, self.painel_heroi, jogador, self.info_heroi.titulo.upper(),
                                         self.cor_heroi, barras)

        rotulo, cor = TIPO_INIMIGO.get(type(inimigo).__name__, ("INIMIGO", c.TEXTO_SUAVE))
        y = self._desenhar_painel_personagem(tela, self.painel_inimigo, inimigo, rotulo, cor,
                                             [self.barra_vida_inimigo])
        fonte = Fontes.texto(14, negrito=True)
        if isinstance(inimigo, InimigoEspecial):
            if self.ctrl.proxima_e_habilidade and self.estado != "fim":
                pulso = 0.5 + 0.5 * math.sin(self.tempo * 8)
                cor_hab = tuple(int(a + (b - a) * pulso) for a, b in zip((255, 220, 120), (255, 80, 60)))
                texto = f"Prepara: {inimigo.habilidade_especial}!"
            else:
                cor_hab = c.TEXTO_SUAVE
                faltam = self.ctrl.INTERVALO_HABILIDADE - self.ctrl.turno % self.ctrl.INTERVALO_HABILIDADE
                texto = f"{inimigo.habilidade_especial} em {faltam} turno{'s' if faltam > 1 else ''}"
            desenhar_texto(tela, texto, fonte, cor_hab, (self.painel_inimigo.right - 18, y), ancora="midright",
                           sombra=False)

        # Faixa central com o turno
        caixa = pygame.Rect(0, 0, 220, 64)
        caixa.midtop = (c.LARGURA // 2, 18)
        desenhar_painel(tela, caixa, alfa=200, raio=14)
        desenhar_texto(tela, f"TURNO {self.ctrl.turno}", Fontes.titulo(26), c.OURO, (caixa.centerx, caixa.y + 24))
        desenhar_texto(tela, self.fase.titulo, Fontes.texto(13), c.TEXTO_SUAVE, (caixa.centerx, caixa.y + 49),
                       sombra=False)

        # Painel de ações
        desenhar_painel(tela, self.painel_acoes, alfa=210)
        self.desenhar_botoes(tela)
        dica = next((b.dica for b in self.botoes if b.visivel and b.mouse_em_cima), None)
        if dica is None:
            if self.estado == "jogador":
                dica = "Sua vez! Escolha uma ação (teclas 1 a 4)."
            elif self.estado == "animando":
                dica = "Aguarde..."
            else:
                dica = ""
        desenhar_texto(tela, dica, Fontes.texto(16), c.TEXTO_SUAVE,
                       (self.painel_acoes.centerx, self.painel_acoes.bottom - 28), sombra=False)
        self.log.desenhar(tela)

    def _desenhar_menu_itens(self, tela):
        veu = pygame.Surface((c.LARGURA, c.ALTURA), pygame.SRCALPHA)
        veu.fill((0, 0, 0, 140))
        tela.blit(veu, (0, 0))
        ultimo = self.botoes_itens[-1].ret
        caixa = pygame.Rect(c.LARGURA // 2 - 220, 160, 440, ultimo.bottom - 160 + 24)
        desenhar_painel(tela, caixa, alfa=240, brilho_borda=0.4)
        desenhar_texto(tela, "MOCHILA", Fontes.titulo(28), c.OURO, (caixa.centerx, caixa.y + 40))
        for botao in self.botoes_itens:
            botao.desenhar(tela)

    def _desenhar_fim(self, tela):
        veu = pygame.Surface((c.LARGURA, c.ALTURA), pygame.SRCALPHA)
        veu.fill((0, 0, 0, 150))
        tela.blit(veu, (0, 0))
        caixa = pygame.Rect(0, 0, 680, 330)
        caixa.center = (c.LARGURA // 2, 380)
        if self.resultado_final == "vitoria":
            titulo, cor = "VITÓRIA!", c.OURO
            linhas = [f"{self.ctrl.inimigo.nome} foi derrotado em {self.ctrl.turno} turnos.",
                      f"Dano causado: {self.ctrl.dano_causado}   •   Dano recebido: {self.ctrl.dano_recebido}"]
            if self.recompensa and not self.campanha.concluida:
                linhas.append(f"Recompensa: {self.recompensa.nome} (+{self.recompensa.valor} de vida)")
        elif self.resultado_final == "derrota":
            titulo, cor = "DERROTA", c.DANO
            linhas = [f"{self.ctrl.jogador.nome} foi derrotado por {self.ctrl.inimigo.nome}.",
                      "Seus itens serão devolvidos se tentar de novo."]
        else:
            titulo, cor = "VOCÊ FUGIU", c.TEXTO_SUAVE
            linhas = ["Às vezes recuar também é estratégia...", "O inimigo continua esperando no mapa."]
        desenhar_brilho(tela, caixa.center, 340, cor, 0.35)
        desenhar_painel(tela, caixa, alfa=235, borda=cor)
        desenhar_texto(tela, titulo, Fontes.titulo(64), cor, (caixa.centerx, caixa.y + 66))
        for i, linha in enumerate(linhas):
            desenhar_texto(tela, linha, Fontes.texto(19), c.TEXTO, (caixa.centerx, caixa.y + 132 + i * 30),
                           sombra=False)
        for botao in self.botoes_fim:
            botao.desenhar(tela)
        # O confete fica por cima do painel
        if self.resultado_final == "vitoria":
            self.particulas.desenhar(tela)
