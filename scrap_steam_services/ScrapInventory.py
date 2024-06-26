from __future__ import annotations
from typing import Union, TYPE_CHECKING
import requests

from user_interfaces.GenericUI import GenericUI
from scrap_steam_services.web_page_cleaning import InventoryCleaner
from data_models import PersistToDB

if TYPE_CHECKING:
    from steam_user.SteamUser import SteamUser


class ScrapInventory:

    def __init__(self, steam_user: SteamUser):
        self.__steam_user = steam_user
        self.__items_per_page = 2000
        self.__extraction_progress_counter = 0

    def full_update(self) -> None:
        inventory_cleaner: InventoryCleaner = self._full_extraction()
        if inventory_cleaner.empty:
            return
        self._save_to_db(inventory_cleaner)

    def after_booster_pack_opened(self, game_market_id: str) -> list[str]:
        inventory_cleaner: InventoryCleaner = self._full_extraction()
        if inventory_cleaner.empty:
            raise Exception('Inventory did not download correctly.')
        self._save_to_db(inventory_cleaner)

        # this part should be somewhere else and this whole function should be the same as above
        # but I won't fix it right now, I'm commenting this just to remember to do it later
        bps_in_inventory: list[str] = inventory_cleaner.get_game_booster_pack_asset_ids(game_market_id=game_market_id)
        return bps_in_inventory

    def _save_to_db(self, inventory_cleaner: InventoryCleaner) -> None:
        games_found_in_inventory = inventory_cleaner.get_game_info()
        PersistToDB.persist('game', source='inventory',
            data=games_found_in_inventory,
            update_game_name=True,
        )

        steam_items_found_in_inventory = inventory_cleaner.get_steam_item_info()
        PersistToDB.persist('steam_item', source='inventory',
            data=steam_items_found_in_inventory,
        )

        assets_found_in_inventory = inventory_cleaner.get_asset_info()
        PersistToDB.persist('steam_asset', source='inventory',
            data=assets_found_in_inventory,
            user_id=self.__steam_user.user_id,
        )

    def _full_extraction(self) -> InventoryCleaner:
        inventory_cleaner = InventoryCleaner()

        progress_text = 'Downloading full inventory'
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)

        custom_status_code, page_response = self._get_page()
        if custom_status_code != 200:
            print(f'\n{custom_status_code}: {page_response}\n')
            return inventory_cleaner

        inventory_raw = page_response.json()
        inventory_cleaner += inventory_raw

        inventory_size = inventory_cleaner.full_size
        GenericUI.progress_completed(progress=self._add_extraction_page_progress(), total=inventory_size, text=progress_text)

        while inventory_cleaner.more_items:
            custom_status_code, page_response = self._get_page(start_assetid=inventory_cleaner.last_assetid)
            # used to fix instability on steam servers, but it's a bad way to do it
            # while custom_status_code == 502:
            #     custom_status_code, page_response = self.__get_page(start_assetid=inventory_cleaner.last_assetid)
            inventory_raw = page_response.json()
            inventory_cleaner += inventory_raw
            GenericUI.progress_completed(progress=self._add_extraction_page_progress(), total=inventory_size, text=progress_text)
        self.__extraction_progress_counter = 0
        GenericUI.progress_completed(progress=1, total=1, text=progress_text)

        return inventory_cleaner

    def _get_page(self, start_assetid: str = None) -> (int, Union[requests.Response, str]):
        custom_status_code, response = self.__steam_user.web_crawler.interact(
            'inventory_page',
            logged_in=True,
            items_per_page=self.__items_per_page,
            start_assetid=start_assetid,
        )
        return custom_status_code, response

    def _add_extraction_page_progress(self) -> int:
        self.__extraction_progress_counter += 1
        progress = self.__extraction_progress_counter * self.__items_per_page
        return progress
