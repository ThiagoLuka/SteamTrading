import requests
from typing import Union

from user_interfaces.GenericUI import GenericUI
from web_crawlers import SteamWebCrawler
from web_page_cleaning.InventoryPageCleaner import InventoryPageCleaner
from data_models.SteamInventory import SteamInventory
from data_models.SteamGames import SteamGames
from data_models.ItemsSteam import ItemsSteam
from data_models.TradingCards import TradingCards


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
        self.__save_to_db(inventory_cleaner)

    def after_booster_pack_opened(self, game: dict, booster_pack_asset_ids: list[str]) -> list[str]:

        inventory_cleaner: InventoryPageCleaner = self.__full_extraction()
        if inventory_cleaner.empty:
            raise Exception('Inventory did not download correctly.')

        bps_in_inventory: list[str] = inventory_cleaner.get_booster_packs_asset_ids(game_market_id=game['market_id'])
        booster_packs_not_opened = [bp for bp in booster_pack_asset_ids if bp in bps_in_inventory]
        qtd_bps_opened = len(booster_pack_asset_ids) - len(booster_packs_not_opened)

        cards_in_new_inventory: dict = inventory_cleaner.get_cards_asset_ids_and_foil(game_market_id=game['market_id'])
        saved_inventory = SteamInventory.get_current_inventory_from_db(self.__user_id)

        new_game_cards = 0
        foil_quantity = 0
        for card_asset_id, foil in cards_in_new_inventory.items():
            if card_asset_id not in saved_inventory.df['asset_id'].values:
                new_game_cards += 1
                if foil:
                    foil_quantity += 1

        TradingCards.update_booster_packs_opened(
            game_id=game['id'],
            times_opened=qtd_bps_opened,
            foil_quantity=foil_quantity,
        )

        self.__save_to_db(inventory_cleaner)
        return booster_packs_not_opened

    def __save_to_db(self, inventory_cleaner: InventoryPageCleaner) -> None:
        progress_text = 'Cleaning and saving data'
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)

        # there's still a mixed level of abstraction here. This part shouldn't be that aware of details of the data
        # that flows from the cleaner to the data_models

        inventory_games_raw = inventory_cleaner.get_games_with_market_id()
        inventory_games = SteamGames()
        saved_game_market_ids = SteamGames().get_market_ids()
        for game_name, game_market_id in inventory_games_raw:
            if str(game_market_id) not in saved_game_market_ids:
                inventory_games += SteamGames(name=game_name, market_id=game_market_id)
        inventory_games.save()

        type_id_and_names = inventory_cleaner.get_item_types_with_item_names()
        type_ids, type_names = zip(*set(type_id_and_names))
        ItemsSteam(
            'item_steam_types', id=type_ids, name=type_names
        ).save()

        game_market_ids = inventory_cleaner.get_game_market_ids_for_descripts()
        game_ids = SteamGames.get_ids_list_by_market_ids_list(game_market_ids)
        type_ids, type_names = zip(*type_id_and_names)
        names = inventory_cleaner.get_descript_names()
        url_names = inventory_cleaner.get_item_url_names()
        ItemsSteam(
            'items_steam', game_id=game_ids, item_steam_type_id=type_ids, name=names, market_url_name=url_names
        ).save()

        items_steam_ids = ItemsSteam.get_ids_by_game_id_and_market_url_name(game_ids, url_names)
        class_ids = inventory_cleaner.get_class_ids('descriptions')
        ItemsSteam(
            'item_steam_descriptions', item_steam_id=items_steam_ids, class_id=class_ids
        ).save()

        class_ids = inventory_cleaner.get_class_ids('assets')
        asset_ids = inventory_cleaner.get_asset_ids()
        marketables = inventory_cleaner.get_asset_marketable_info()
        SteamInventory(
            'cleaning', class_id=class_ids, asset_id=asset_ids, marketable=marketables,
        ).save(self.__user_id)

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
            # used to fix instability on steam servers, but it's a bad way to do it
            # while custom_status_code == 502:
            #     custom_status_code, page_response = self.__get_page(start_assetid=inventory_cleaner.last_assetid)
            inventory_raw = page_response.json()
            inventory_cleaner += inventory_raw
            GenericUI.progress_completed(progress=self.__add_extraction_page_progress(), total=inventory_size, text=progress_text)
        self.__extraction_progress_counter = 0
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
