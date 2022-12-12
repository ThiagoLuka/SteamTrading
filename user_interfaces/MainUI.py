from user_interfaces.InputValidation import InputValidation


class MainUI:

    @staticmethod
    def run() -> int:
        print(
            '\nMENU PRINCIPAL\n'
            '1 - Gerenciar perfis da steam\n'
            '2 - Scrap profile badges page\n'
            '3 - Update inventory\n'
            '4 - Abrir booster packs\n'
            '0 - Sair'
        )
        return InputValidation.int_within_range(0, 4)

    @staticmethod
    def goodbye() -> None:
        print('\nAté mais!')
