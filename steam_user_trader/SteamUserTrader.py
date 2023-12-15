from scrap_steam_services import ScrapMarketMainPage
from steam_user.SteamUser import SteamUser


class SteamUserTrader(SteamUser):

    def __init__(self, user_data: dict):
        super().__init__(user_data=user_data)

    @classmethod
    def from_steam_user(cls, steam_user: SteamUser):
        # that is awful but it's temporary. Fix it when implementing new user factor
        user_data = steam_user._SteamUser__user_data
        return cls(user_data)

    def update_buy_orders(self, games_quantity: int) -> None:
        pass

    def update_sell_listings(self) -> None:
        ScrapMarketMainPage(steam_user=self).get_sell_listings()
