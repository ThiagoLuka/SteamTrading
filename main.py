import time

from utils.Singleton import Singleton
from user_interfaces.MainUI import MainUI
from user_interfaces.SteamTraderUI import SteamTraderUI
from steam_user.SteamUserManager import SteamUserManager
from steam_user.SteamTraderController import SteamTraderController
from steam_user_trader.SteamUserTrader import SteamUserTrader
from steam_games.SteamGamesDiscovery import SteamGamesDiscovery


class MainController(metaclass=Singleton):

    def __init__(self):
        SteamUserManager()

    def run_ui(self) -> None:
        steam_user: SteamUserTrader = SteamUserManager().get_user(default_user=True)

        while True:
            command = MainUI.run(steam_user.name)

            if command == 1:
                steam_user = SteamUserManager().get_user()
            if command == 2:
                n_games_outdate = SteamTraderUI.update_buy_orders_prompt_message(option='outdated')
                self.update_workflow(steam_user=steam_user, n_games_to_update=n_games_outdate)
            if command == 3:
                self.sell_cards_workflow(
                    steam_user=steam_user,
                    sell_manual=SteamTraderUI.set_manual_option_prompt_message(),
                    sell_game_quantity=SteamTraderUI.sell_cards_prompt_message(),
                )
                self.update_workflow(steam_user=steam_user, n_games_to_update=0)
            if command == 4:
                self.create_buy_order_workflow(steam_user=steam_user)
            if command == 5:
                SteamTraderController(steam_user_trader=steam_user).run_ui()
            if command == 6:
                SteamGamesDiscovery().discover_new_apps(qtd=5000)

            if command == 0:
                MainUI.goodbye()
                break

    @staticmethod
    def update_workflow(
        steam_user: SteamUserTrader,
        n_games_to_update: int = 0
    ) -> None:
        game_ids = steam_user.buy_orders.get_game_ids_with_most_outdated_orders(quantity=n_games_to_update)

        # steam_user.update_badges()  # it's broken but it should be here

        steam_user.update_inventory()
        SteamTraderController(
            steam_user_trader=steam_user
        ).overview_marketable_cards(get_user_inputs=False)

        steam_user.update_sell_listings()

        steam_user.remove_sell_listings()

        steam_user.update_buy_orders(game_ids=game_ids)


    @staticmethod
    def sell_cards_workflow(
        steam_user: SteamUserTrader,
        sell_manual: bool,
        sell_game_quantity: int,
    ) -> None:
        steam_user.start_market_actions_queue()
        steam_user.create_sell_listings(manual=sell_manual, game_quantity=sell_game_quantity)
        steam_user.end_market_actions_queue()
        time.sleep(60)  # waiting phone app confirmations

    @staticmethod
    def create_buy_order_workflow(steam_user: SteamUserTrader) -> None:
        steam_user.start_market_actions_queue()
        steam_user.create_game_buy_orders()
        steam_user.end_market_actions_queue()


if __name__ == "__main__":
    MainController().run_ui()
