import requests

from web_crawlers.SteamWebCrawler import SteamWebCrawler
from web_page_cleaning.MarketItemPageCleaner import MarketItemPageCleaner
from data_models.BuyOrders import BuyOrders


class ScrapMarketItemPage:

    def run(self, web_crawler: SteamWebCrawler, required_data: list[dict]):

        item_descript_ids, quantities, prices = [], [], []

        for item in required_data:
            game_market_id: int = item['game_market_id']
            item_descript_id: int = item['item_descript_id']
            item_url_name: str = item['item_url_name']

            custom_status_code, response = self.__extract(web_crawler, game_market_id, item_url_name)
            if response.status_code != 200:
                continue

            price, quantity = self.__transform(response)
            if quantity == 0:
                continue

            item_descript_ids.append(item_descript_id)
            quantities.append(quantity)
            prices.append(price)

        buy_orders = BuyOrders(
            item_descript_id=item_descript_ids, active=True,
            price=prices, qtd_estimate=quantities, qtd_current=quantities
        )
        self.__load(buy_orders)

    @staticmethod
    def __extract(web_crawler: SteamWebCrawler, game_market_id: int, item_url_name: str) -> requests.Response:
        response = web_crawler.interact(
            'scrap_market_item',
            game_market_id=game_market_id,
            item_url_name=item_url_name,
        )
        return response

    @staticmethod
    def __transform(response: requests.Response) -> tuple[int, int]:
        qtd, price = MarketItemPageCleaner.clean(response)
        return qtd, price

    @staticmethod
    def __load(buy_orders: BuyOrders) -> None:
        buy_orders.save()
