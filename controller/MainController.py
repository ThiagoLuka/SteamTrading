import sys

from utils.Singleton import Singleton
from user_interfaces.MainUI import MainUI
from controller.SteamUserController import SteamUserController
from controller.SteamTraderController import SteamTraderController
from steam_user.SteamUser import SteamUser
from steam_user_trader.SteamUserTrader import SteamUserTrader
from scrap_steam_services import ScrapProfileBadgesPage, ScrapProfileGameCardsPage


class MainController(metaclass=Singleton):

    def __init__(self):
        # I have to fix this user controller for more users later, it's a mess right now
        self._steam_user = SteamUserController().get_active_user()
        SteamUserController()
        if not SteamUserController().has_user:
            sys.exit(0)

    def run_ui(self) -> None:
        while True:
            command = MainUI.run()

            if command == 1:
                SteamUserController().run_ui()
            if command == 2:
                self.get_user_badge(steam_user=self._steam_user)
            if command == 3:
                self.update_user_inventory(steam_user=self._steam_user)
            if command == 4:
                steam_user_trader = SteamUserTrader.from_steam_user(steam_user=self._steam_user)
                SteamTraderController(steam_user_trader=steam_user_trader).run_ui()

            if command == 0:
                MainUI.goodbye()
                break

    @staticmethod
    def get_user_badge(steam_user: SteamUser) -> None:
        ScrapProfileBadgesPage(
            steam_user=steam_user,
        ).get_profile_badges()
        ScrapProfileGameCardsPage(
            steam_user=steam_user,
        ).get_new_trading_cards()

    @staticmethod
    def update_user_inventory(steam_user: SteamUser) -> None:
        steam_user.update_inventory()
