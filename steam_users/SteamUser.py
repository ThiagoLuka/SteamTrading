from web_crawlers import SteamWebCrawler
from data_models.SteamInventory import SteamInventory
from data_models.SteamGames import SteamGames
from repositories.SteamUserRepository import SteamUserRepository


class SteamUser:

    def __init__(self, user_data: dict):
        self.__steam_id: str = user_data['steam_id']
        self.__steam_alias: str = user_data['steam_alias']
        self.__user_id = self.__save_user()
        self.__crawler = SteamWebCrawler(self.__steam_id, user_data)

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
        status, result = self.__crawler.interact(
            'get_badges',
            logged_in=logged_in,
            user_id=self.__user_id,
            steam_id=self.steam_id,
        )
        if status != 200:
            print(f'\n{status}: {result}\n')
            return

        self.__get_trading_cards_of_new_games()

    def update_inventory(self) -> None:
        status, result = self.__crawler.interact(
            'get_inventory',
            logged_in=True,
            user_id=self.__user_id,
            steam_id=self.steam_id,
        )
        if status != 200:
            print(f'\n{status}: {result}\n')
            return

    def open_booster_packs(self, game_name: str) -> None:
        bp_assets_id_list = SteamInventory.get_booster_pack_assets_id(
            user_id=self.__user_id, game_name=game_name
        )
        status, result = self.__crawler.interact(
            'open_booster_pack',
            booster_pack_assets_ids=bp_assets_id_list,
            steam_alias=self.__steam_alias,
        )
        if status != 200:
            print(f'\n{status}: {result}\n')
            return

    def __get_trading_cards_of_new_games(self) -> None:
        games_to_get_trading_cards = SteamGames.get_all_without_trading_cards()
        if games_to_get_trading_cards.empty:
            return

        status, result = self.__crawler.interact(
            'get_trading_cards',
            logged_in=True,
            games=games_to_get_trading_cards,
            steam_id=self.steam_id,
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
