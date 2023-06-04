import time
from threading import Thread
from queue import Queue, Empty

from user_interfaces.GenericUI import GenericUI
from user_interfaces.SteamTraderUI import SteamTraderUI
from steam_users.SteamUser import SteamUser
from data_models.SteamGames import SteamGames
from data_models.ItemsSteam import ItemsSteam
from data_models.BuyOrders import BuyOrders
from data_models.SteamInventory import SteamInventory


class SteamTraderController:

    def __init__(self, steam_user: SteamUser):
        self.__user = steam_user
        self.__user_id = steam_user.user_id
        self.__cards_sold_count = 0
        self.__sell_items_queue = Queue()
        sell_items_thread = Thread(
            target=self.__sell_item_task,
            daemon=True,
        )
        sell_items_thread.start()
        self.__create_buy_orders_queue = Queue()
        create_buy_orders_thread = Thread(
            target=self.__create_buy_order_task,
            daemon=True
        )
        create_buy_orders_thread.start()

    def run_ui(self) -> None:
        while True:
            command = SteamTraderUI.run()
            if command == 1:
                self.overview_marketable_cards()
            if command == 2:
                self.update_buy_orders()
            if command == 3:
                game_name = GenericUI.get_game_name()
                self.__user.open_booster_packs(game_name)
                self.__user.update_inventory()
            if command == 4:
                self.sell_multiple_cards()

            if command == 0:
                self.__sell_items_queue.join()
                self.__create_buy_orders_queue.join()
                return None

    def overview_marketable_cards(self) -> None:
        if GenericUI.update_inventory():
            self.__user.update_inventory()
        data_for_overview = SteamInventory.get_overview_marketable_cards(self.__user_id)
        inventory_size = SteamInventory.get_current_inventory_size(self.__user_id)
        SteamTraderUI.overview_marketable_cards(data_for_overview, inventory_size)

    def update_buy_orders(self) -> None:
        create_buy_oders, n_games_to_update = SteamTraderUI.update_buy_orders_prompt_message()

        if not n_games_to_update:
            return

        if create_buy_oders:
            game_ids: list[str] = BuyOrders.get_game_ids_to_be_updated(n_games_to_update, self.__user_id)
        else:
            game_ids: list[str] = BuyOrders.get_game_ids_with_most_outdated_orders(n_games_to_update, self.__user_id)

        games = SteamGames.get_all_by_id(game_ids)

        for idx, game_data in enumerate(games):
            print(f"{idx + 1} - {game_data['name']}")
            game_items = ItemsSteam.get_booster_pack_and_cards_market_url(game_data['id'], booster_pack_last=True)
            if create_buy_oders:
                self.__create_buy_orders(game_items, game_data)
                continue
            for steam_item in game_items:
                self.__update_buy_orders_from_market_page(steam_item, game_data['market_id'])

    def sell_multiple_cards(self) -> None:
        game_name = GenericUI.get_game_name()
        game = SteamGames.get_all_by_name(game_name)
        if game.empty:
            return
        game_items = ItemsSteam.get_booster_pack_and_cards_market_url(game.id)

        items_to_sell = SteamInventory.get_marketable_cards_asset_ids(self.__user_id, game.id)

        buy_orders = BuyOrders.get_last_buy_order(list(game_items.df.id), self.__user_id)
        self.__show_buy_orders(buy_orders, game_items, game.name)

        self.__show_items_to_sell(game_items, items_to_sell)

        for idx, steam_item in enumerate(game_items):
            item_name = steam_item.df.loc[0, 'name']
            if item_name in items_to_sell.keys():
                self.__open_item_market_page_in_browser(steam_item, game.market_id)
                price = SteamTraderUI.set_sell_price_for_item(item_name, idx)
                for asset_id in items_to_sell[item_name]:
                    self.__sell_items_queue.put((asset_id, price))

    def __create_buy_orders(self, game_items: ItemsSteam, game_data: dict) -> None:
        buy_orders = BuyOrders.get_last_buy_order(list(game_items.df.id), self.__user_id)
        self.__show_buy_orders(buy_orders, game_items, game_data['name'])

        SteamTraderUI.set_buy_orders_header()
        item_ids_with_buy_orders_finished = buy_orders.finished()
        for idx, steam_item in enumerate(game_items):
            item_id = steam_item.df.loc[0, 'id']
            item_name = steam_item.df.loc[0, 'name']
            item_url_name = steam_item.df.loc[0, 'market_url_name']
            if item_id in item_ids_with_buy_orders_finished:
                self.__open_item_market_page_in_browser(steam_item, game_data['market_id'])
                price, qtd = SteamTraderUI.set_buy_order_for_item(item_name, idx+1)
                if not price or not qtd:
                    continue
                self.__create_buy_orders_queue.put((item_id, item_url_name, price, qtd, game_data['market_id']))

    @staticmethod
    def __show_buy_orders(buy_orders: BuyOrders, game_items: ItemsSteam, game_name: str) -> None:
        SteamTraderUI.buy_orders_header(game_name)
        for steam_item in game_items:
            buy_order_filter = buy_orders.df['item_steam_id'] == steam_item.df.loc[0, 'id']
            buy_order_qtd = list(buy_orders.df.loc[buy_order_filter, 'qtd_current'].values)[0]
            buy_order_price = list(buy_orders.df.loc[buy_order_filter, 'price'].values)[0]
            item_name = steam_item.df.loc[0, 'name']
            SteamTraderUI.show_buy_order(qtd=buy_order_qtd, price=buy_order_price, item_name=item_name)

    @staticmethod
    def __show_items_to_sell(game_items: ItemsSteam, items_to_sell: dict) -> None:
        items_to_sell_print_formatted = []
        for idx, steam_item in enumerate(game_items):
            item_name = steam_item.df.loc[0, 'name']
            if item_name in items_to_sell.keys():
                to_sell_qtd = len(items_to_sell[item_name])
                items_to_sell_print_formatted.append([item_name, to_sell_qtd, idx])
        SteamTraderUI.view_trading_cards_to_sell(items_to_sell_print_formatted)

    def __update_buy_orders_from_market_page(self, steam_item: ItemsSteam, game_market_id: str) -> None:
        self.__user.update_buy_order(
            game_market_id=game_market_id,
            steam_item=steam_item,
            open_web_browser=False
        )
        time.sleep(15)

    def __open_item_market_page_in_browser(self, steam_item: ItemsSteam, game_market_id: str) -> None:
        self.__user.update_buy_order(
            game_market_id=game_market_id,
            steam_item=steam_item,
            open_web_browser=True
        )
        time.sleep(0.5)

    def __sell_item_task(self) -> None:
        while True:
            try:
                asset_id, price = self.__sell_items_queue.get()
            except Empty:
                continue
            else:
                if self.__cards_sold_count % 100 == 0:
                    time.sleep(10)
                self.__user.create_sell_listing(asset_id=asset_id, price=price)
                self.__cards_sold_count += 1
                self.__sell_items_queue.task_done()

    def __create_buy_order_task(self) -> None:
        while True:
            try:
                item_id, item_url_name, price, qtd, game_market_id = self.__create_buy_orders_queue.get()
            except Empty:
                continue
            else:
                response_content = self.__user.create_buy_order(item_url_name, price, qtd, game_market_id)
                if response_content['success'] == 1:
                    BuyOrders(
                        steam_buy_order_id=response_content['buy_orderid'], user_id=self.__user_id,
                        item_steam_id=item_id, active=True, price=price, qtd_current=qtd
                    ).save()
                else:
                    SteamTraderUI.create_buy_order_failed()
                self.__create_buy_orders_queue.task_done()
