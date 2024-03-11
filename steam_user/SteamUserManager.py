import json

from utils.Singleton import Singleton
from user_interfaces.MainUI import MainUI
from steam_user.SteamUser import SteamUser
from steam_user_trader.SteamUserTrader import SteamUserTrader


class SteamUserManager(metaclass=Singleton):

    def __init__(self):
        self._users: dict = {}
        self._default_user = ''
        self._load_all_users()

    def get_user(self, default_user: bool = False) -> SteamUserTrader:
        if default_user:
            return self._users[self._default_user]
        steam_alias = MainUI.choose_user(all_users=list(self._users.keys()))
        if not steam_alias:
            return self._users[self._default_user]
        steam_user = self._users[steam_alias]
        return steam_user

    def _load_all_users(self) -> None:
        with open('user_steam.json') as file:
            users = json.load(file)
        for user_data in users:
            steam_user = SteamUser(user_data)
            steam_user_trader = SteamUserTrader.from_steam_user(steam_user=steam_user)
            self._users[steam_user.name] = steam_user_trader
            if not self._default_user:
                self._default_user = steam_user.name
            MainUI.user_loaded(steam_user.name, steam_user.steam_level)
