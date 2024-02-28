import json

from utils.Singleton import Singleton
from steam_user.SteamUser import SteamUser
from steam_user_trader.SteamUserTrader import SteamUserTrader


class SteamUserManager(metaclass=Singleton):

    def __init__(self):
        self.__users: dict = {}
        self._load_all_users()

    def get_user(self, steam_alias: str) -> SteamUserTrader:
        steam_user = self.__users[steam_alias]
        return steam_user

    def _load_all_users(self) -> None:
        with open('user_steam.json') as file:
            users = json.load(file)
        for user_data in users:
            steam_user = SteamUser(user_data)
            steam_user_trader = SteamUserTrader.from_steam_user(steam_user=steam_user)
            self.__users[steam_user.name] = steam_user_trader
