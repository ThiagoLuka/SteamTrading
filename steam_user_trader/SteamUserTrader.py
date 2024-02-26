from threading import Thread
from queue import Queue, Empty

from scrap_steam_services import (
    ScrapMarketItemPage,
    ScrapMarketMainPage,
)
from steam_market_services import (
    AnalyzeItemPrices,
    CreateBuyOrders,
    CreateSellListings,
    RemoveSellListings,
    OpenGameBoosterPack,
)
from steam_user.SteamUser import SteamUser
from steam_user_trader.BuyOrders import BuyOrders
from steam_user_trader.SellListings import SellListings


class SteamUserTrader(SteamUser):

    def __init__(self, user_data: dict):
        super().__init__(user_data=user_data)
        self._buy_orders = BuyOrders(user_id=self.user_id)
        self._sell_listings = SellListings(user_id=self.user_id)
        self.cards_sold_count = 0
        self._market_actions_queue = Queue()
        market_actions_thread = Thread(
            target=self._market_actions_queue_task_handler,
            daemon=True,
        )
        market_actions_thread.start()

    @property
    def buy_orders(self):
        return self._buy_orders

    @property
    def sell_listings(self):
        return self._sell_listings

    @property
    def market_actions_queue(self):
        return self._market_actions_queue

    def end_queue(self) -> None:
        self._market_actions_queue.join()

    @classmethod
    def from_steam_user(cls, steam_user: SteamUser):
        # that is awful but it's temporary. Fix it when implementing new user factor
        user_data = steam_user._SteamUser__user_data
        return cls(user_data)

    def analyze_game_items_prices(self, game_ids: list[int]) -> None:
        AnalyzeItemPrices(steam_trader=self).run(game_ids=game_ids)

    def update_buy_orders(self, game_ids: list[int]) -> None:
        ScrapMarketItemPage(steam_user=self).update_games_buy_orders(game_ids=game_ids)
        self.buy_orders.reload_current()

    def update_sell_listings(self) -> None:
        ScrapMarketMainPage(steam_user=self).get_sell_listings()
        self.sell_listings.reload_current()

    def create_game_buy_orders(self) -> None:
        CreateBuyOrders(steam_trader=self).create_buy_orders()
        self.buy_orders.reload_current()

    def create_sell_listings(self, manual: bool, game_quantity: int) -> None:
        CreateSellListings(steam_trader=self, manual=manual).create_sell_listings(game_quantity=game_quantity)
        self.sell_listings.reload_current()

    def remove_sell_listings(self) -> None:
        RemoveSellListings(steam_trader=self).older_than(days_old=140)

    def open_booster_packs(self, games_quantity: int) -> None:
        OpenGameBoosterPack(steam_user=self).run(games_quantity=games_quantity)
        self.update_inventory()

    def _market_actions_queue_task_handler(self) -> None:
        while True:
            try:
                cmd, kwargs = self.market_actions_queue.get()
            except Empty:
                continue
            else:
                task = {
                    'create_sell_listing': CreateSellListings.queue_task,
                    'create_buy_order': CreateBuyOrders.create_queue_task,
                    'cancel_buy_order': CreateBuyOrders.cancel_queue_task,
                }.get(cmd)
                task(steam_trader=self, **kwargs)
                self.market_actions_queue.task_done()
