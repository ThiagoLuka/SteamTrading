from user_interfaces.InputValidation import InputValidation


class MainUI:

    @staticmethod
    def run() -> int:
        print(
            '\n-- MAIN MENU --\n'
            '1 - Manage steam users\n'
            '2 - Scrap for user badges\n'
            '3 - Update inventory\n'
            '4 - Open booster packs\n'
            '0 - Exit'
        )
        return InputValidation.int_within_range(0, 4)

    @staticmethod
    def goodbye() -> None:
        print('\nSee you later!')
