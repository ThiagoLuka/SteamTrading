from user_interfaces.InputValidation import InputValidation


class MainUI:

    @staticmethod
    def run(steam_user: str) -> int:
        print(
            '\n-- MAIN MENU --\n'
            f'Current user: {steam_user}\n'
            '1 - Change user\n'
            '2 - Update workflow\n'
            '3 - Sell cards workflow\n'
            '4 - Create buy orders workflow\n'
            '5 - Individual functions menu\n'
            '6 - Discover new steam apps\n'
            '0 - Exit'
        )
        return InputValidation.int_within_range(0, 6)

    @staticmethod
    def choose_user(all_users: list) -> str:
        print('\nChoose a user:')
        for index, user in enumerate(all_users):
            print(f'{index+1} - {user}')
        print(f'0 - Default user')
        user_index_plus_one = InputValidation.int_within_range(0, len(all_users))
        if user_index_plus_one == 0:
            return ''
        return all_users[user_index_plus_one-1]

    @staticmethod
    def user_loaded(user_name: str, steam_level: int):
        steam_level = 'unknown' if steam_level == 0 else steam_level
        print(f'\n\nWelcome {user_name}!'
              f'\nCurrent steam level: {steam_level}\n')

    @staticmethod
    def goodbye() -> None:
        print('\nSee you later!')
