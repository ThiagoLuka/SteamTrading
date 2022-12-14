from user_interfaces.InputValidation import InputValidation


class SteamUserUI:

    @staticmethod
    def run() -> int:
        print(
            '\n-- MENU STEAM USERS --\n'
            '1 - View loaded users\n'
            '2 - Add a user\n'
            '3 - Add cookies for a user\n'
            '4 - Change main user\n'
            '0 - Back to main menu'
        )
        return InputValidation.int_within_range(0, 4)

    @staticmethod
    def user_loaded():
        print('Steam user loaded!')

    @staticmethod
    def no_user():
        print('No user available')

    @staticmethod
    def view_users(users: dict) -> list:
        print('Users:')
        users_names: list = []
        for index, user_name in enumerate(users.keys()):
            print(f'{index} - {user_name}')
            users_names.append(user_name)
        return users_names

    @staticmethod
    def choose_user(qtd_of_users: int):
        return InputValidation.int_within_range(
            0, qtd_of_users - 1, 'Choose user: '
        )
