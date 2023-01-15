import requests
from typing import Union

from user_interfaces.GenericUI import GenericUI
from web_crawlers import SteamWebCrawler
from web_page_cleaning.InventoryPageCleaner import InventoryPageCleaner
from data_models.SteamInventory import SteamInventory
from data_models.SteamTradingCards import SteamTradingCards


class UpdateFullInventory:

    def __init__(self):
        self.__items_per_page = 2000
        self.__progress_counter = 0

    def run(self, web_crawler: SteamWebCrawler, **required_data) -> None:
        user_id: int = required_data['user_id']

        inventory_cleaner = self.__extraction(web_crawler)
        if inventory_cleaner is None:
            return

        progress_text = 'Cleaning and saving data'
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)

        inventory_cleaner.save_new_games()

        descripts: SteamInventory = inventory_cleaner.to_descriptions()
        assets: SteamInventory = inventory_cleaner.to_assets(user_id)

        descripts.save('descriptions')
        SteamTradingCards.set_relationship_with_item_descripts(SteamInventory.get_all('descriptions').df)
        assets.save('assets', user_id)

        GenericUI.progress_completed(progress=1, total=1, text=progress_text)

    def __extraction(self, web_crawler: SteamWebCrawler) -> Union[InventoryPageCleaner, None]:
        progress_text = 'Downloading full inventory'
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)

        custom_status_code, page_response = self.__get_page(web_crawler)
        if custom_status_code != 200:
            print(f'\n{custom_status_code}: {page_response}\n')
            return

        inventory_raw = page_response.json()
        inventory_cleaner = InventoryPageCleaner(inventory_raw)

        inventory_size = len(inventory_cleaner)
        GenericUI.progress_completed(progress=self.__add_page_progress(), total=inventory_size, text=progress_text)

        while inventory_cleaner.more_items:
            csc, page_response = self.__get_page(
                web_crawler,
                start_assetid=inventory_cleaner.last_assetid
            )
            inventory_raw = page_response.json()
            inventory_cleaner += inventory_raw
            GenericUI.progress_completed(progress=self.__add_page_progress(), total=inventory_size, text=progress_text)
        GenericUI.progress_completed(progress=1, total=1, text=progress_text)

        return inventory_cleaner

    def __get_page(
            self, web_crawler: SteamWebCrawler, start_assetid: str = None
    ) -> (int, Union[requests.Response, str]):
        custom_status_code, response = web_crawler.interact(
            'get_inventory_page',
            logged_in=True,
            items_per_page=self.__items_per_page,
            start_assetid=start_assetid,
        )
        return custom_status_code, response

    def __add_page_progress(self):
        self.__progress_counter += 1
        progress = self.__progress_counter * self.__items_per_page
        return progress
