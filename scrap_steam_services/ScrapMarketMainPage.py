from __future__ import annotations
from typing import TYPE_CHECKING
import requests

from user_interfaces.GenericUI import GenericUI
from scrap_steam_services.web_page_cleaning import MarketMainPageCleaner
from data_models import PersistToDB

if TYPE_CHECKING:
    from steam_user.SteamUser import SteamUser


class ScrapMarketMainPage:

    def __init__(self, steam_user: SteamUser):
        self.__steam_user = steam_user
        self.__items_per_page = 100
        self.__extraction_progress_counter = 0

    def get_sell_listings(self):

        listings_cleaner = self.__full_extraction()

        cleaned_data = listings_cleaner.clean()

        PersistToDB.persist(
            'sell_listing',
            cleaned_data,
            user_id=self.__steam_user.user_id,
        )

    def __full_extraction(self) -> MarketMainPageCleaner:
        progress_text = 'Downloading every sell listing'
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)
        listings_cleaner = MarketMainPageCleaner()
        while listings_cleaner.has_more_items_to_download():
            page_response = self.__get_page(offset=listings_cleaner.listings_downloaded)
            listings_raw = page_response.json()
            listings_cleaner += listings_raw
            GenericUI.progress_completed(progress=listings_cleaner.listings_downloaded, total=listings_cleaner.total_count, text=progress_text)
        return listings_cleaner

    def __get_page(self, offset: int = None) -> requests.Response:
        status, response = self.__steam_user.web_crawler.interact(
            'sell_listing_page',
            listings_start_count=offset,
            listings_per_page=self.__items_per_page,
        )
        return response
