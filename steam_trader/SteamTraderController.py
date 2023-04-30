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

    def run_ui(self) -> None:
        while True:
            command = SteamTraderUI.run()
            if command == 1:
                self.overview_marketable_cards()
            if command == 2:
                game_name = GenericUI.get_game_name()
                self.__user.open_booster_packs(game_name)
                self.__user.update_inventory()
            if command == 3:
                self.sell_multiple_cards()

            if command == 0:
                self.__sell_items_queue.join()
                return None

    def overview_marketable_cards(self):
        if GenericUI.update_inventory():
            self.__user.update_inventory()
        data_for_overview = SteamInventory.get_overview_marketable_cards(self.__user_id)
        inventory_size = SteamInventory.get_current_inventory_size(self.__user_id)
        SteamTraderUI.overview_marketable_cards(data_for_overview, inventory_size)

    def sell_multiple_cards(self):
        game_name = GenericUI.get_game_name()
        game = SteamGames.get_all_by_name(game_name)
        if game.empty:
            return
        game_items = ItemsSteam.get_booster_pack_and_cards_market_url(game.id)

        cards_to_sell_names, cards_to_sell = SteamInventory.get_marketable_cards_asset_ids(self.__user_id, game.name)

        for steam_item_data in game_items:
            steam_item = ItemsSteam('items_steam', **steam_item_data)
            open_web_browser = False
            if steam_item.df.loc[0, 'name'] in cards_to_sell_names:
                open_web_browser = True
            self.__user.update_buy_order(
                game_market_id=game.market_id,
                steam_item=steam_item,
                open_web_browser=open_web_browser
            )

        buy_orders = BuyOrders.get_last_buy_order(list(game_items.df.id), self.__user_id)
        SteamTraderUI.buy_orders_header(game.name)
        for steam_item_data in game_items:
            buy_order_filter = buy_orders.df['item_steam_id'] == steam_item_data['id']
            buy_order_qtd = list(buy_orders.df.loc[buy_order_filter, 'qtd_current'].values)[0]
            buy_order_price = list(buy_orders.df.loc[buy_order_filter, 'price'].values)[0]
            item_name = steam_item_data['name']
            SteamTraderUI.show_buy_order(qtd=buy_order_qtd, price=buy_order_price, item_name=item_name)

        asset_ids_with_prices = SteamTraderUI.set_prices_for_cards(cards_to_sell)
        for index, (asset_id, price) in enumerate(asset_ids_with_prices.items()):
            self.__sell_items_queue.put((asset_id, price))

    def __sell_item_task(self):
        while True:
            try:
                asset_id, price = self.__sell_items_queue.get()
            except Empty:
                continue
            else:
                if self.__cards_sold_count % 100 == 0:
                    time.sleep(25)
                self.__user.create_sell_listing(asset_id=asset_id, price=price)
                self.__sell_items_queue.task_done()
                self.__cards_sold_count += 1
