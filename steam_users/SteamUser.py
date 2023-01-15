from etl_pipelines.ScrapProfileBadgesPage import ScrapProfileBadgesPage
from etl_pipelines.UpdateFullInventory import UpdateFullInventory
from etl_pipelines.GetTradingCardsOfNewGames import GetTradingCardsOfNewGames
from etl_pipelines.OpenGameBoosterPacks import OpenGameBoosterPacks
from web_crawlers import SteamWebCrawler
from data_models.SteamGames import SteamGames
from repositories.SteamUserRepository import SteamUserRepository


class SteamUser:

    def __init__(self, user_data: dict):
        self.__steam_id: str = user_data['steam_id']
        self.__steam_alias: str = user_data['steam_alias']
        self.__user_id = self.__save_user()
        self.__crawler = SteamWebCrawler(self.__steam_id, user_data)

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def steam_id(self) -> str:
        return self.__steam_id

    @property
    def name(self) -> str:
        return (
            self.__steam_alias
            if self.__steam_alias is not None
            else self.__steam_id
        )

    def log_in(self, login_data: dict) -> None:
        pass

    def get_badges(self, logged_in: bool = True) -> None:
        ScrapProfileBadgesPage().run(
            self.__crawler,
            logged_in=logged_in,
            user_id=self.__user_id,
        )
        GetTradingCardsOfNewGames().run(self.__crawler)

    def update_inventory(self) -> None:
        UpdateFullInventory().run(
            self.__crawler,
            user_id=self.__user_id,
        )

    def open_booster_packs(self, game_name: str) -> None:
        OpenGameBoosterPacks().run(
            self.__crawler,
            user_id=self.__user_id,
            steam_alias=self.__steam_alias,
            game_name=game_name
        )

    def create_sell_listing(self, asset_id: str, price: int) -> None:
        status, result = self.__crawler.interact(
            'sell_listing',
            asset_id=asset_id,
            price=price,
            steam_alias=self.__steam_alias,
        )
        if status != 200:
            print(f'\n{status}: {result}\n')
            return

    def __save_user(self) -> int:
        saved = SteamUserRepository.get_by_steam_id(self.__steam_id)
        if not saved:
            SteamUserRepository.save_user(self.__steam_id, self.__steam_alias)
            saved = SteamUserRepository.get_by_steam_id(self.__steam_id)
        user_id = saved[0][0]
        return user_id
