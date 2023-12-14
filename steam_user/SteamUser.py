from scrap_steam_services.ScrapInventory import ScrapInventory
from steam_user.steam_web_crawler import SteamWebCrawler
from steam_user.SteamInventory import SteamInventory
from steam_user.SteamBadges import SteamBadges
from data_models.query.SteamUserRepository import SteamUserRepository


class SteamUser:

    def __init__(self, user_data: dict):
        self.__steam_id: str = user_data['steam_id']
        self.__steam_alias: str = user_data['steam_alias']
        self.__user_id: int = self.__save_user()
        self.__crawler = SteamWebCrawler(
            self.__steam_id,
            self.__steam_alias,
            user_data,  # user_data should hold user cookies and send them to crawler, at least for now
        )
        self.__inventory = SteamInventory(user_id=self.user_id)
        self.__steam_level: int = SteamBadges.get_user_level(self.__user_id)

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def steam_id(self) -> str:
        return self.__steam_id

    @property
    def name(self) -> str:
        return self.__steam_alias

    @property
    def web_crawler(self) -> SteamWebCrawler:
        return self.__crawler

    @property
    def inventory(self) -> SteamInventory:
        return self.__inventory

    @property
    def steam_level(self) -> int:
        return self.__steam_level

    def log_in(self, login_data: dict) -> None:
        pass

    def update_inventory(self) -> None:
        ScrapInventory(steam_user=self).full_update()
        self.__inventory.reload_current()

    def update_inventory_after_booster_pack(self, game_market_id: str) -> list:
        bps_left = ScrapInventory(steam_user=self).after_booster_pack_opened(game_market_id=game_market_id)
        self.__inventory.reload_current()
        return bps_left

    def create_sell_listing(self, asset_id: str, price: int) -> None:
        status, result = self.__crawler.interact(
            'create_sell_listing',
            asset_id=asset_id,
            price=price,
        )
        if status != 200:
            print(f'\n{status}: {result}\n')
            return

    def create_buy_order(self, item_url_name: str, price: int, qtd: int, game_market_id: int) -> dict:
        status, result = self.__crawler.interact(
            'create_buy_order',
            game_market_id=game_market_id,
            item_url_name=item_url_name,
            price=price,
            quantity=qtd
        )
        return result.json()

    def open_market_item_page_in_browser(self, game_market_id: str, item_market_url_name: str):
        self.__crawler.interact(
            'item_market_page',
            open_web_browser=True,
            game_market_id=game_market_id,
            item_url_name=item_market_url_name,
        )

    def __save_user(self) -> int:
        saved = SteamUserRepository.get_by_steam_id(self.__steam_id)
        if not saved:
            SteamUserRepository.save_user(self.__steam_id, self.__steam_alias)
            saved = SteamUserRepository.get_by_steam_id(self.__steam_id)
        user_id = saved[0][0]
        return user_id
