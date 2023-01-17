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
    def user_loaded(user_name: str, steam_level: int):
        steam_level = 'unknown' if steam_level == 0 else steam_level
        print(
            f'\nSteam user loaded!\n'
            f'Welcome {user_name}!\n'
            f'Your current steam level is {steam_level}'
        )

    @staticmethod
    def no_user():
        print('\nNo steam user available.')

    @staticmethod
    def user_setup_instructions():
        print(
            'You need to set up a steam user in order to use this piece of software.\n'
            'To do that, create a txt file called "standard_user.txt" in the folder of this project\n'
            'and add to it the following variables:\n'
            'steam_id=\n'
            'steam_alias=\n'
            'timezoneOffset=\n'
            'sessionid=\n'
            'steamMachineAuth=\n'
            'steamLoginSecure=\n'
            'The first two variables are identifiers of your steam profile and will be saved in the db\n'
            'The others may only be found as cookies while visiting a steam webpage logged in a browser as that user\n'
            'Whitout those variables the software may not work properly.\n'
            'After that, you may start the software again and enjoy leveling up on steam! :)'
        )

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
