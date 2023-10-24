import requests

from user_interfaces.GenericUI import GenericUI
from web_crawlers.SteamWebCrawler import SteamWebCrawler
from web_page_cleaning.SellListingPageCleaner import SellListingPageCleaner
from etl_data_models.SellListing import SellListing


class ScrapMarketMainPage:

    def __init__(self, web_crawler: SteamWebCrawler, user_id: int):
        self.__crawler = web_crawler
        self.__user_id = user_id
        self.__items_per_page = 100
        self.__extraction_progress_counter = 0

    def get_sell_listings(self):

        listings_cleaner = self.__full_extraction()

        cleaned_data = listings_cleaner.clean()

        sell_listings = SellListing(cleaned_data)

        sell_listings.save(self.__user_id)

    def __full_extraction(self) -> SellListingPageCleaner:
        progress_text = 'Downloading every sell listing'
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)
        listings_cleaner = SellListingPageCleaner()
        while listings_cleaner.has_more_items_to_download():
            page_response = self.__get_page(offset=listings_cleaner.listings_downloaded)
            listings_raw = page_response.json()
            listings_cleaner += listings_raw
            GenericUI.progress_completed(progress=listings_cleaner.listings_downloaded, total=listings_cleaner.total_count, text=progress_text)
        return listings_cleaner

    def __get_page(self, offset: int = None) -> requests.Response:
        status, response = self.__crawler.interact(
            'sell_listing_page',
            listings_start_count=offset,
            listings_per_page=self.__items_per_page,
        )
        return response
