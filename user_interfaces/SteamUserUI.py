from user_interfaces.InputValidation import InputValidation


class SteamUserUI:

    @staticmethod
    def run() -> int:
        print(
            '\nMENU STEAM USERS\n'
            '1 - Ver usuários carregados\n'
            '2 - Adicionar um usuário\n'
            '3 - Adicionar cookies para um usuário\n'
            '4 - Mudar usuário principal\n'
            '0 - Voltar para menu principal'
        )
        return InputValidation.int_within_range(0, 4)

    @staticmethod
    def user_loaded():
        print('Usuário steam carregado!')

    @staticmethod
    def no_user():
        print('Nenhum usuário disponível')

    @staticmethod
    def view_users(users: dict) -> list:
        print('Usuários:')
        users_names: list = []
        for index, user_name in enumerate(users.keys()):
            print(f'{index} - {user_name}')
            users_names.append(user_name)
        return users_names

    @staticmethod
    def choose_user(qtd_of_users: int):
        return InputValidation.int_within_range(
            0, qtd_of_users - 1, 'Escolha o usuário pelo número: '
        )
