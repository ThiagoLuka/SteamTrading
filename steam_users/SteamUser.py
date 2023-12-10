from etl_pipelines.ScrapProfileBadgesPage import ScrapProfileBadgesPage
from etl_pipelines.ScrapInventory import ScrapInventory
from etl_pipelines.ScrapProfileGameCardsPage import ScrapProfileGameCardsPage
from etl_pipelines.OpenGameBoosterPacks import OpenGameBoosterPacks
from etl_pipelines.ScrapMarketMainPage import ScrapMarketMainPage
from etl_pipelines.ScrapMarketItemPage import ScrapMarketItemPage
from web_crawlers import SteamWebCrawler
from data_models.SteamBadges import SteamBadges
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
    def steam_level(self) -> int:
        return self.__steam_level

    def log_in(self, login_data: dict) -> None:
        pass

    def get_badges(self, logged_in: bool = True) -> None:
        ScrapProfileBadgesPage(
            self.__crawler,
            self.__user_id,
            logged_in=logged_in,
        ).get_profile_badges()
        ScrapProfileGameCardsPage(
            self.__crawler
        ).get_new_trading_cards()

    def update_inventory(self) -> None:
        ScrapInventory(self.__crawler, self.__user_id).full_update()

    def open_booster_packs(self, n_of_games: int) -> None:
        OpenGameBoosterPacks().run(
            self.__crawler,
            user_id=self.__user_id,
            n_of_games=n_of_games
        )

    def create_sell_listing(self, asset_id: str, price: int) -> None:
        status, result = self.__crawler.interact(
            'create_sell_listing',
            asset_id=asset_id,
            price=price,
        )
        if status != 200:
            print(f'\n{status}: {result}\n')
            return

    def update_sell_listing(self) -> None:
        ScrapMarketMainPage(
            self.__crawler,
            self.__user_id,
        ).get_sell_listings()

    def create_buy_order(self, item_url_name: str, price: int, qtd: int, game_market_id: int) -> dict:
        status, result = self.__crawler.interact(
            'create_buy_order',
            game_market_id=game_market_id,
            item_url_name=item_url_name,
            price=price,
            quantity=qtd
        )
        return result.json()

    def update_game_buy_orders(self, game_name: str, game_market_id: str, items: list[dict]):
        ScrapMarketItemPage(
            self.__crawler,
            self.__user_id,
            game_info={
                'name': game_name,
                'market_id': game_market_id,
            },
            items=items
        ).get_game_buy_orders()

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
