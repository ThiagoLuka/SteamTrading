import random

from user_interfaces.GenericUI import GenericUI
from user_interfaces.SteamTraderUI import SteamTraderUI
from steam_user_trader.SteamUserTrader import SteamUserTrader
from steam_games import SteamGames


class SteamTraderController:

    def __init__(self, steam_user_trader: SteamUserTrader):
        self._steam_trader = steam_user_trader
        self._steam_trader.start_market_actions_queue()

    def run_ui(self) -> None:
        while True:
            command = SteamTraderUI.run()
            if command == 1:
                self.overview_marketable_cards()
            if command == 2:
                self.update_user_badge()
            if command == 3:
                self.update_buy_orders()
            if command == 4:
                self.create_buy_orders()
            if command == 5:
                self.open_booster_packs()
            if command == 6:
                self.remove_old_sell_listings()
            if command == 7:
                self.update_sell_listings()
            if command == 8:
                self.create_sell_listings()

            if command == 0:
                self._steam_trader.end_market_actions_queue()
                return

    def overview_marketable_cards(self) -> None:
        if GenericUI.update_inventory():
            self._steam_trader.update_inventory()
        summary_qtd_by_game = self._steam_trader.inventory.summary_qtd(by='game', marketable=True)
        game_id_and_name = SteamGames(game_ids=list(summary_qtd_by_game.keys())).id_name_dict()
        summary_qtd_by_game = {game_id_and_name[game_id]: qtd for game_id, qtd in summary_qtd_by_game.items()}
        inventory_size = self._steam_trader.inventory.size()
        SteamTraderUI.overview_marketable_cards(summary=summary_qtd_by_game, inv_total_size=inventory_size)

    def update_user_badge(self) -> None:
        self._steam_trader.update_badges()

    def update_buy_orders(self) -> None:
        n_games_outdate = SteamTraderUI.update_buy_orders_prompt_message(option='outdated')
        n_games_undefined = SteamTraderUI.update_buy_orders_prompt_message(option='undefined')
        game_ids_0 = self._steam_trader.buy_orders.get_game_ids_with_most_outdated_orders(quantity=n_games_outdate)
        game_ids_1 = self._steam_trader.inventory.get_game_ids_with_most_undefined(quantity=n_games_undefined)
        game_ids = list(set(game_ids_0 + game_ids_1))
        random.shuffle(game_ids)
        self._steam_trader.update_buy_orders(game_ids=game_ids)

    def update_sell_listings(self) -> None:
        self._steam_trader.update_sell_listings()

    def create_buy_orders(self) -> None:
        self._steam_trader.create_game_buy_orders()

    def open_booster_packs(self) -> None:
        games_quantity = SteamTraderUI.open_booster_packs()
        self._steam_trader.open_booster_packs(games_quantity=games_quantity)

    def remove_old_sell_listings(self) -> None:
        self._steam_trader.remove_sell_listings()

    def create_sell_listings(self) -> None:
        manual = SteamTraderUI.set_manual_option_prompt_message()
        game_quantity = SteamTraderUI.sell_cards_prompt_message()
        self._steam_trader.create_sell_listings(manual=manual, game_quantity=game_quantity)
