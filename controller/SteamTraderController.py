import time
from threading import Thread
from queue import Queue, Empty

from user_interfaces.GenericUI import GenericUI
from user_interfaces.SteamTraderUI import SteamTraderUI
from data_models import PersistToDB
from steam_user_trader.SteamUserTrader import SteamUserTrader
from data_models.SteamGames import SteamGames
from data_models.SteamGamesNew import SteamGamesNew
from data_models.ItemsSteam import ItemsSteam
from data_models.BuyOrders import BuyOrders
from data_models.SteamInventory import SteamInventory


class SteamTraderController:

    def __init__(self, steam_user_trader: SteamUserTrader):
        self._steam_trader = steam_user_trader
        self._cards_sold_count = 0
        self._market_actions_queue = Queue()
        market_actions_thread = Thread(
            target=self.__market_actions_queue_controller,
            daemon=True,
        )
        market_actions_thread.start()

    def run_ui(self) -> None:
        while True:
            command = SteamTraderUI.run()
            if command == 1:
                self.overview_marketable_cards()
            if command == 2:
                self.update_buy_orders()
            if command == 3:
                self.create_buy_orders()
            if command == 4:
                self.open_booster_packs()
            if command == 5:
                self.update_sell_listings()
            if command == 6:
                self.create_sell_listings()

            if command == 0:
                self._market_actions_queue.join()
                return None

    def overview_marketable_cards(self) -> None:
        if GenericUI.update_inventory():
            self._steam_trader.update_inventory()
        summary_qtd_by_game = self._steam_trader.inventory.summary_qtd(by='game', marketable=True)
        game_id_and_name = SteamGamesNew(game_ids=list(summary_qtd_by_game.keys())).id_name_dict()
        summary_qtd_by_game = {game_id_and_name[game_id]: qtd for game_id, qtd in summary_qtd_by_game.items()}
        inventory_size = self._steam_trader.inventory.size()
        SteamTraderUI.overview_marketable_cards(summary=summary_qtd_by_game, inv_total_size=inventory_size)

    def update_buy_orders(self) -> None:
        n_games_to_update = SteamTraderUI.update_buy_orders_prompt_message()
        game_ids = self._steam_trader.buy_orders.get_game_ids_with_most_outdated_orders(quantity=n_games_to_update)
        self._steam_trader.update_buy_orders(game_ids=game_ids)

    def update_sell_listings(self) -> None:
        self._steam_trader.update_sell_listings()

    def create_buy_orders(self) -> None:
        if SteamTraderUI.create_first_buy_order_of_game():
            self.__create_first_buy_orders(GenericUI.get_game_id())
            return
        n_games_to_update = SteamTraderUI.how_many_games_buy_orders()
        game_ids: list[str] = BuyOrders.get_game_ids_to_be_updated(n_games_to_update, self._steam_trader.user_id)
        games = SteamGames.get_all_by_id(game_ids)

        for idx, game_data in enumerate(games):
            print(f"{idx + 1} - {game_data['name']}")
            game_items = ItemsSteam.get_booster_pack_and_cards_market_url(game_data['id'], booster_pack_last=True)
            buy_orders = BuyOrders.get_game_last_buy_orders(game_data['id'], self._steam_trader.user_id)
            self.__show_game_buy_orders(buy_orders, game_items, game_data['name'])

            SteamTraderUI.set_buy_orders_header()
            item_ids_with_buy_orders_finished = buy_orders.finished()
            for idx2, steam_item in enumerate(game_items):
                item_id = steam_item.df.loc[0, 'id']
                item_name = steam_item.df.loc[0, 'name']
                item_url_name = steam_item.df.loc[0, 'market_url_name']
                if item_id in item_ids_with_buy_orders_finished:
                    self.__open_item_market_page_in_browser(steam_item, game_data['market_id'])
                    price, qtd = SteamTraderUI.set_buy_order_for_item(item_name, idx2 + 1)
                    if not price or not qtd:
                        continue
                    self._market_actions_queue.put((
                        'create_buy_order', {
                            'item_id': item_id,
                            'item_url_name': item_url_name,
                            'price': price,
                            'qtd': qtd,
                            'game_market_id': game_data['market_id']
                        }))

    def __create_first_buy_orders(self, game_id: str):
        game = SteamGames.get_all_by_id([game_id])
        for game_data in game:
            game_items = ItemsSteam.get_booster_pack_and_cards_market_url(game_data['id'], booster_pack_last=True)
            for idx2, steam_item in enumerate(game_items):
                item_id = steam_item.df.loc[0, 'id']
                item_name = steam_item.df.loc[0, 'name']
                item_url_name = steam_item.df.loc[0, 'market_url_name']
                self.__open_item_market_page_in_browser(steam_item, game_data['market_id'])
                price, qtd = SteamTraderUI.set_buy_order_for_item(item_name, idx2 + 1)
                if not price or not qtd:
                    continue
                self._market_actions_queue.put((
                    'create_buy_order', {
                        'item_id': item_id,
                        'item_url_name': item_url_name,
                        'price': price,
                        'qtd': qtd,
                        'game_market_id': game_data['market_id']
                    }))

    def open_booster_packs(self) -> None:
        games_quantity = SteamTraderUI.open_booster_packs()
        self._steam_trader.open_booster_packs(games_quantity=games_quantity)

    def create_sell_listings(self) -> None:
        n_games_to_update = SteamTraderUI.sell_cards_prompt_message()
        game_ids = SteamInventory.get_game_ids_with_cards_to_be_sold(n_games_to_update, self._steam_trader.user_id)
        games = SteamGames.get_all_by_id(game_ids)

        for idx, game_data in enumerate(games):
            game_items = ItemsSteam.get_booster_pack_and_cards_market_url(game_data['id'], include_foil=True)

            item_name_with_asset_ids = SteamInventory.get_marketable_cards_asset_ids(self._steam_trader.user_id, game_data['id'])

            buy_orders = BuyOrders.get_game_last_buy_orders(game_data['id'], self._steam_trader.user_id)
            self.__show_game_buy_orders(buy_orders, game_items, game_data['name'])

            self.__show_items_to_sell(game_items, item_name_with_asset_ids)

            for idx2, steam_item in enumerate(game_items):
                item_id = steam_item.df.loc[0, 'id']
                item_name = steam_item.df.loc[0, 'name']
                if item_name in item_name_with_asset_ids.keys():
                    self.__open_item_market_page_in_browser(steam_item, game_data['market_id'])
                    last_buy_orders = BuyOrders.get_item_last_buy_orders(item_id, self._steam_trader.user_id, amount=2)
                    self.__show_item_buy_orders(last_buy_orders, item_name)
                    price = SteamTraderUI.set_sell_price_for_item(item_name, idx2)
                    self._market_actions_queue.put((
                        'create_sell_listing', {
                            'asset_ids': item_name_with_asset_ids[item_name],
                            'price': price,
                        }))

    def __open_item_market_page_in_browser(self, steam_item: ItemsSteam, game_market_id: str) -> None:
        self._steam_trader.open_market_item_page_in_browser(
            game_market_id=game_market_id,
            item_market_url_name=steam_item.df.loc[0, 'market_url_name'],
        )
        time.sleep(0.5)

    @staticmethod
    def __show_game_buy_orders(buy_orders: BuyOrders, game_items: ItemsSteam, game_name: str) -> None:
        SteamTraderUI.buy_orders_header(game_name)
        for steam_item in game_items:
            buy_order_filter = buy_orders.df['item_steam_id'] == steam_item.df.loc[0, 'id']
            if True not in buy_order_filter.values:
                continue
            buy_order_qtd = list(buy_orders.df.loc[buy_order_filter, 'qtd_current'].values)[0]
            buy_order_price = list(buy_orders.df.loc[buy_order_filter, 'price'].values)[0]
            item_name = steam_item.df.loc[0, 'name']
            SteamTraderUI.show_buy_order(qtd=buy_order_qtd, price=buy_order_price, item_name=item_name)

    @staticmethod
    def __show_item_buy_orders(buy_orders: BuyOrders, item_name: str) -> None:
        SteamTraderUI.buy_orders_header(item_name)
        for bo in buy_orders:
            SteamTraderUI.show_buy_order(qtd=bo['qtd_current'], price=bo['price'], item_name=item_name)

    @staticmethod
    def __show_items_to_sell(game_items: ItemsSteam, items_to_sell: dict) -> None:
        items_to_sell_print_formatted = []
        for idx, steam_item in enumerate(game_items):
            item_name = steam_item.df.loc[0, 'name']
            if item_name in items_to_sell.keys():
                to_sell_qtd = len(items_to_sell[item_name])
                items_to_sell_print_formatted.append([item_name, to_sell_qtd, idx])
        SteamTraderUI.view_trading_cards_to_sell(items_to_sell_print_formatted)

    def __market_actions_queue_controller(self) -> None:
        while True:
            try:
                cmd, kwargs = self._market_actions_queue.get()
            except Empty:
                continue
            else:
                if cmd == 'create_sell_listing':
                    self.__create_sell_listing_task(**kwargs)
                elif cmd == 'create_buy_order':
                    self.__create_buy_order_task(**kwargs)
                self._market_actions_queue.task_done()


    def __create_sell_listing_task(self, **kwargs) -> None:
        asset_ids = kwargs['asset_ids']
        price = kwargs['price']
        for asset_id in asset_ids:
            if self._cards_sold_count % 100 == 0:
                time.sleep(10)
            self._steam_trader.create_sell_listing(asset_id=asset_id, price=price)
            self._cards_sold_count += 1

    def __create_buy_order_task(self, **kwargs) -> None:
        item_id = kwargs['item_id']
        item_url_name = kwargs['item_url_name']
        price = kwargs['price']
        qtd = kwargs['qtd']
        game_market_id = kwargs['game_market_id']
        response_content = self._steam_trader.create_buy_order(
            item_url_name=item_url_name,
            price=price,
            qtd=qtd,
            game_market_id=game_market_id,
        )
        if response_content['success'] == 1:
            PersistToDB.persist(
                'buy_order',
                [{
                    'item_id': item_id,
                    'steam_buy_order_id': response_content['buy_orderid'],
                    'quantity': qtd,
                    'price': price,
                }],
                user_id=self._steam_trader.user_id
            )
        else:
            SteamTraderUI.create_buy_order_failed()
