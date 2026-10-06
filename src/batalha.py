class Batalha:

    def __init__(self, jogador, inimigo):
        self.jogador = jogador
        self.inimigo = inimigo

    def iniciar(self):

        print("=" * 40)
        print("        INÍCIO DA BATALHA")
        print("=" * 40)

        while self.jogador.esta_vivo() and self.inimigo.esta_vivo():

            print("\n--- STATUS ---")
            self.jogador.mostrar_status()
            self.inimigo.mostrar_status()

            print("\n--- AÇÕES ---")
            print("1 - Atacar")
            print("2 - Usar item")
            print("3 - Fugir")

            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                # TODO: jogador ataca inimigo
                pass

            elif opcao == "2":
                # TODO: implementar item
                pass

            elif opcao == "3":
                print("Você fugiu da batalha!")
                return

            else:
                print("Opção inválida.")
                continue

            # TODO: inimigo deve atacar depois do jogador

        # TODO: verificar quem venceu
        def turno_inimigo(self):
        if not self.inimigo.esta_vivo():
            return

        print("\n--- TURNO DO INIMIGO ---")
        self.inimigo.atacar(self.jogador)
        