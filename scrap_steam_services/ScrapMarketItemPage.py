import requests
import time

from user_interfaces.GenericUI import GenericUI
from steam_user.SteamUser import SteamUser
from web_page_cleaning.MarketItemPageCleaner import MarketItemPageCleaner
from data_models import PersistToDB


class ScrapMarketItemPage:

    def __init__(self, steam_user: SteamUser, game_name: str, game_market_id: str, items: list[dict]):
        self.__steam_user = steam_user
        self.__game_name = game_name
        self.__game_market_id = game_market_id
        self.__items = items
        self.__retries = 4

    def get_game_buy_orders(self):
        progress_text = f"{self.__game_name}"
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)
        for index, item in enumerate(self.__items):
            retries_left = self.__retries
            while True:
                time.sleep(5)  # avoiding too many requests
                try:
                    market_item_page_cleaner = self.__full_extraction(market_url_name=item['market_url_name'])
                    cleaned_data = market_item_page_cleaner.get_buy_order()
                    empty_buy_order = not any(cleaned_data.values())
                    cleaned_data['item_id'] = item['id']
                    PersistToDB.persist(
                        'buy_order',
                        [cleaned_data],
                        user_id=self.__steam_user.user_id,
                        empty_buy_order=empty_buy_order
                    )
                    GenericUI.progress_completed(progress=index+1,total=len(self.__items), text=progress_text)
                    break
                except Exception as error:
                    if retries_left == self.__retries:
                        print('')
                    retries_left -= 1
                    print(f"{error}: {item['name']}")
                    if not retries_left:
                        raise error

    def __full_extraction(self, market_url_name: str) -> MarketItemPageCleaner:
        page_response = self.__get_page(market_url_name=market_url_name)
        page_cleaner = MarketItemPageCleaner(page_response.content)
        return page_cleaner

    def __get_page(self, market_url_name: str) -> requests.Response:
        response_status, response = self.__steam_user.web_crawler.interact(
            'item_market_page',
            open_web_browser=False,
            game_market_id=self.__game_market_id,
            item_url_name=market_url_name,
        )
        return response