from utils.Singleton import Singleton
from user_interfaces.MainUI import MainUI
from user_interfaces.GenericUI import GenericUI
from steam_user.SteamUserManager import SteamUserManager
from steam_user.SteamTraderController import SteamTraderController
from steam_user_trader.SteamUserTrader import SteamUserTrader


class MainController(metaclass=Singleton):

    def __init__(self):
        SteamUserManager()
        self._steam_user_trader: SteamUserTrader = SteamUserManager().get_user(steam_alias='thiagomg')
        MainUI.user_loaded(self._steam_user_trader.name, self._steam_user_trader.steam_level)

    def run_ui(self) -> None:
        while True:
            command = MainUI.run()

            if command == 1:
                GenericUI.not_implemented()
            if command == 2:
                SteamTraderController(steam_user_trader=self._steam_user_trader).run_ui()

            if command == 0:
                MainUI.goodbye()
                break


if __name__ == "__main__":
    MainController().run_ui()