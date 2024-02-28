from user_interfaces.InputValidation import InputValidation


class MainUI:

    @staticmethod
    def run() -> int:
        print(
            '\n-- MAIN MENU --\n'
            '1 - Regular workflow by user\n'
            '2 - Individual functions menu\n'
            '0 - Exit'
        )
        return InputValidation.int_within_range(0, 2)

    @staticmethod
    def user_loaded(user_name: str, steam_level: int):
        steam_level = 'unknown' if steam_level == 0 else steam_level
        print(
            f'\nSteam user loaded!\n'
            f'Welcome {user_name}!\n'
            f'Your current steam level is {steam_level}'
        )

    @staticmethod
    def goodbye() -> None:
        print('\nSee you later!')
