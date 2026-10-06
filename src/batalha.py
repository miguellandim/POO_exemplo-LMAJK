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
                if not self.jogador.inventario:
                    print("Você não tem itens.")
                    continue

                print("\n--- ITENS ---")
                for i, item in enumerate(self.jogador.inventario, start=1):
                    print(f"{i} - {item.nome}")

                escolha = input("Escolha um item: ")

                if not escolha.isdigit() or not self.jogador.usar_item(int(escolha) - 1):
                    print("Item inválido.")
                    continue

            elif opcao == "3":
                print("Você fugiu da batalha!")
                return

            else:
                print("Opção inválida.")
                continue

            # TODO: inimigo deve atacar depois do jogador

        # TODO: verificar quem venceu
