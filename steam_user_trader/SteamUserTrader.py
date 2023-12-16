from scrap_steam_services import ScrapMarketItemPage, ScrapMarketMainPage
from steam_user.SteamUser import SteamUser
from steam_user_trader.BuyOrders import BuyOrders


class SteamUserTrader(SteamUser):

    def __init__(self, user_data: dict):
        super().__init__(user_data=user_data)
        self._buy_orders = BuyOrders(user_id=self.user_id)

    @property
    def buy_orders(self):
        return self._buy_orders

    @classmethod
    def from_steam_user(cls, steam_user: SteamUser):
        # that is awful but it's temporary. Fix it when implementing new user factor
        user_data = steam_user._SteamUser__user_data
        return cls(user_data)

    def update_buy_orders(self, game_ids: list[int]) -> None:
        ScrapMarketItemPage(steam_user=self).update_games_buy_orders(game_ids=game_ids)
        self.buy_orders.reload_current()

    def update_sell_listings(self) -> None:
        ScrapMarketMainPage(steam_user=self).get_sell_listings()
