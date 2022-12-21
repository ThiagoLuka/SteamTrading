from threading import Thread
from queue import Queue, Empty

from user_interfaces.GenericUI import GenericUI
from user_interfaces.SteamTraderUI import SteamTraderUI
from steam_users.SteamUser import SteamUser
from data_models.SteamInventory import SteamInventory


class SteamTraderController:

    def __init__(self, steam_user: SteamUser):
        self.__user = steam_user
        self.__user_id = steam_user.user_id
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
        cards_to_sell = SteamInventory.get_marketable_cards_asset_ids(self.__user_id, game_name)
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
                self.__user.create_sell_listing(asset_id=asset_id, price=price)
                self.__sell_items_queue.task_done()
