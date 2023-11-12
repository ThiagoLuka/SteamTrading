import requests
import time

from user_interfaces.GenericUI import GenericUI
from web_crawlers.SteamWebCrawler import SteamWebCrawler
from web_page_cleaning.MarketItemPageCleaner import MarketItemPageCleaner
from etl_data_models.BuyOrder import BuyOrder


class ScrapMarketItemPage:

    def __init__(self, web_crawler: SteamWebCrawler, user_id: int, game_info: dict, items: list[dict]):
        self.__crawler = web_crawler
        self.__user_id = user_id
        self.__game_name = game_info['name']
        self.__game_market_id = game_info['market_id']
        self.__items = items
        self.__retries = 4

    def get_game_buy_orders(self):
        progress_text = f"{self.__game_name}"
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)
        for index, item in enumerate(self.__items):
            retries_left = self.__retries
            while True:
                try:
                    market_item_page_cleaner = self.__full_extraction(market_url_name=item['market_url_name'])
                    cleaned_data = market_item_page_cleaner.get_buy_order()
                    empty_buy_order = not any(cleaned_data.values())
                    cleaned_data['item_id'] = item['id']
                    BuyOrder([cleaned_data]).save(user_id=self.__user_id, empty_buy_order=empty_buy_order)
                    GenericUI.progress_completed(progress=index+1,total=len(self.__items), text=progress_text)
                    break
                except Exception as error:
                    retries_left -= 1
                    print(f"\n{error}: {item['name']}")
                    GenericUI.progress_completed(progress=index+1, total=len(self.__items), text=progress_text)
                    time.sleep(5)
                    if not retries_left:
                        raise error

    def __full_extraction(self, market_url_name: str) -> MarketItemPageCleaner:
        page_response = self.__get_page(market_url_name=market_url_name)
        page_cleaner = MarketItemPageCleaner(page_response.content)
        return page_cleaner

    def __get_page(self, market_url_name: str) -> requests.Response:
        response_status, response = self.__crawler.interact(
            'item_market_page',
            open_web_browser=False,
            game_market_id=self.__game_market_id,
            item_url_name=market_url_name,
        )
        return response