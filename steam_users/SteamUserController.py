from utils.Singleton import Singleton
from user_interfaces.SteamUserUI import SteamUserUI
from user_interfaces.GenericUI import GenericUI
from steam_users.SteamUser import SteamUser


class SteamUserController(metaclass=Singleton):

    def __init__(self):
        self.__users: dict = {}
        self.__active_user = str
        self.__has_user: bool = self.__load_standard_user()

    @property
    def has_user(self):
        return self.__has_user

    def run_ui(self) -> None:
        while True:
            command = SteamUserUI.run()
            if command == 1:
                self.view_all_users()
            if command == 2:
                GenericUI.not_implemented()
            if command == 3:
                GenericUI.not_implemented()
            if command == 4:
                self.change_active_user()

            if command == 0:
                return None

    def get_active_user(self) -> SteamUser:
        return self.__users[self.__active_user]

    def get_any_user(self) -> SteamUser:
        return self.__choose_user()

    def change_active_user(self) -> None:
        next_active_user = self.__choose_user()
        self.__active_user = next_active_user.name

    def view_all_users(self) -> list:
        users_names: list = []
        if not self.__users:
            SteamUserUI.no_user()
        else:
            users_names = SteamUserUI.view_users(self.__users)
        return users_names

    def __choose_user(self) -> SteamUser:
        users_names = self.view_all_users()
        user_name_position = SteamUserUI.choose_user(len(users_names))
        user_name = users_names[user_name_position]
        user = self.__users[user_name]
        return user

    def __load_standard_user(self) -> bool:
        user_data: dict = {}
        try:
            with open('standard_user.txt', 'r') as file:
                for line in file.readlines():
                    line_data = line.strip().split('=', 1)
                    user_data[line_data[0]] = line_data[1]
        except FileNotFoundError:
            SteamUserUI.no_user()
            SteamUserUI.user_setup_instructions()
            return False

        standard_user = SteamUser(user_data)

        self.__users[standard_user.name] = standard_user
        self.__active_user = standard_user.name
        SteamUserUI.user_loaded(standard_user.name, standard_user.steam_level)
        return True