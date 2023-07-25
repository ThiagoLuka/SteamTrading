import requests
import time

from web_crawlers.SteamWebCrawler import SteamWebCrawler
from web_page_cleaning.ItemMarketPageCleaner import ItemMarketPageCleaner
from data_models.BuyOrders import BuyOrders
from data_models.ItemsSteam import ItemsSteam


class ScrapItemMarketPage:

    def run(self, web_crawler: SteamWebCrawler, **required_data):
        user_id: int = required_data['user_id']
        game_market_id: str = required_data['game_market_id']
        steam_item: 'ItemsSteam' = required_data['steam_item']
        open_web_browser: bool = required_data['open_web_browser']

        retries = 4
        for i in range(retries+1):
            custom_status_code, response = self.__extract(
                web_crawler,
                open_web_browser,
                game_market_id,
                steam_item.df.loc[0, 'market_url_name'],  # this should change later to hide the df
            )
            if response.status_code != 200:
                return
            page_cleaner = ItemMarketPageCleaner(response.content)
            try:
                steam_buy_order_id, quantity, price = page_cleaner.get_buy_order_info()
                if not steam_buy_order_id:
                    BuyOrders.handle_empty_from_market_page(steam_item.df.loc[0, 'id'], user_id)
                    return

                BuyOrders(
                    steam_buy_order_id=steam_buy_order_id, user_id=user_id, item_steam_id=steam_item.df.loc[0, 'id'],
                    active=True, price=price, qtd_current=quantity
                ).save()
                break
            except Exception as error:
                time.sleep(10)
                if i == retries:
                    raise error
                print(steam_item.df.loc[0, 'name'], error)
                continue

    @staticmethod
    def __extract(
            web_crawler: SteamWebCrawler, open_web_browser: bool, game_market_id: str, item_url_name: str
    ) -> requests.Response:
        response = web_crawler.interact(
            'item_market_page',
            open_web_browser=open_web_browser,
            game_market_id=game_market_id,
            item_url_name=item_url_name,
        )
        return response
