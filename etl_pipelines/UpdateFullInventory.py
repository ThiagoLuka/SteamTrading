import requests
from typing import Union

from user_interfaces.GenericUI import GenericUI
from web_crawlers import SteamWebCrawler
from web_page_cleaning.InventoryPageCleaner import InventoryPageCleaner
from data_models.SteamInventory import SteamInventory
from data_models.SteamTradingCards import SteamTradingCards
from data_models.SteamGames import SteamGames


class UpdateInventory:

    def __init__(self, web_crawler: SteamWebCrawler, user_id: int):
        self.__crawler = web_crawler
        self.__user_id = user_id
        self.__items_per_page = 2000
        self.__extraction_progress_counter = 0

    def full_update(self) -> None:

        inventory_cleaner: InventoryPageCleaner = self.__full_extraction()
        if inventory_cleaner.empty:
            return

        progress_text = 'Cleaning and saving data'
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)

        self.__save_new_games(inventory_cleaner)

        descripts: SteamInventory = self.__to_descriptions(inventory_cleaner)
        assets: SteamInventory = self.__to_assets(inventory_cleaner, self.__user_id)

        descripts.save('descriptions')
        SteamTradingCards.set_relationship_with_item_descripts(SteamInventory.get_all('descriptions').df)
        assets.save('assets', self.__user_id)

        GenericUI.progress_completed(progress=1, total=1, text=progress_text)

    def __full_extraction(self) -> InventoryPageCleaner:
        inventory_cleaner = InventoryPageCleaner()

        progress_text = 'Downloading full inventory'
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)

        custom_status_code, page_response = self.__get_page()
        if custom_status_code != 200:
            print(f'\n{custom_status_code}: {page_response}\n')
            return inventory_cleaner

        inventory_raw = page_response.json()
        inventory_cleaner += inventory_raw

        inventory_size = inventory_cleaner.full_size
        GenericUI.progress_completed(progress=self.__add_extraction_page_progress(), total=inventory_size, text=progress_text)

        while inventory_cleaner.more_items:
            custom_status_code, page_response = self.__get_page(start_assetid=inventory_cleaner.last_assetid)
            inventory_raw = page_response.json()
            inventory_cleaner += inventory_raw
            GenericUI.progress_completed(progress=self.__add_extraction_page_progress(), total=inventory_size, text=progress_text)
        GenericUI.progress_completed(progress=1, total=1, text=progress_text)

        return inventory_cleaner

    def __get_page(self, start_assetid: str = None) -> (int, Union[requests.Response, str]):
        custom_status_code, response = self.__crawler.interact(
            'inventory_page',
            logged_in=True,
            items_per_page=self.__items_per_page,
            start_assetid=start_assetid,
        )
        return custom_status_code, response

    def __add_extraction_page_progress(self) -> int:
        self.__extraction_progress_counter += 1
        progress = self.__extraction_progress_counter * self.__items_per_page
        return progress

    def __to_descriptions(self, inventory_cleaner: InventoryPageCleaner) -> SteamInventory:
        game_market_ids = inventory_cleaner.get_game_market_ids_for_descripts()
        game_ids = SteamGames.get_ids_list_by_market_ids_list(game_market_ids)
        class_ids = inventory_cleaner.get_class_ids('descriptions')
        type_id_and_names = inventory_cleaner.get_item_types_with_item_names()
        self.__save_new_item_types(type_id_and_names)
        type_ids = [type_id[0] for type_id in type_id_and_names]
        names = inventory_cleaner.get_descript_names()
        url_names = inventory_cleaner.get_item_url_names()
        descripts = SteamInventory(game_id=game_ids, name=names, type_id=type_ids, class_id=class_ids, url_name=url_names)
        return descripts

    @staticmethod
    def __to_assets(inventory_cleaner: InventoryPageCleaner, user_id: int) -> SteamInventory:
        user_ids = [user_id] * len(inventory_cleaner)
        class_ids = inventory_cleaner.get_class_ids('assets')
        asset_ids = inventory_cleaner.get_asset_ids()
        marketables = inventory_cleaner.get_asset_marketable_info()
        assets = SteamInventory(user_id=user_ids, class_id=class_ids, asset_id=asset_ids, marketable=marketables)
        return assets

    @staticmethod
    def __save_new_games(inventory_cleaner: InventoryPageCleaner) -> None:
        inventory_games_raw = inventory_cleaner.get_games_with_market_id()
        inventory_games = SteamGames()
        saved_game_market_ids = SteamGames().get_market_ids()
        for game_name, game_market_id in inventory_games_raw:
            if str(game_market_id) not in saved_game_market_ids:
                inventory_games += SteamGames(name=game_name, market_id=game_market_id)
        inventory_games.save()

    @staticmethod
    def __save_new_item_types(type_id_and_names: list) -> None:
        new_id_and_name = {elem[0]: elem[1] for elem in type_id_and_names}
        saved_type_ids = SteamInventory.get_item_types()
        to_save = SteamInventory()
        for type_id, type_name in new_id_and_name.items():
            if int(type_id) not in saved_type_ids.keys():
                to_save += SteamInventory(id=type_id, name=type_name)
        if not to_save.empty:
            to_save.save('types')
