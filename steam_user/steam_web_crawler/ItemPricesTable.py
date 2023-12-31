import requests

from .SteamWebPage import SteamWebPage


class ItemPricesTable(SteamWebPage, name='item_prices_table'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'item_name_id', 'game_market_id', 'item_url_name',

    @staticmethod
    def required_cookies() -> tuple:
        return 'sessionid', 'steamLoginSecure',

    @staticmethod
    def required_referer() -> str:
        return 'item_market_page'

    def generate_url(self, **kwargs) -> str:
        return f'{super().BASESTEAMURL}market/itemordershistogram'

    def interact(self, cookies: dict, **kwargs) -> requests.Response:
        referer: str = kwargs['referer']
        item_name_id: str = kwargs['item_name_id']

        url = self.generate_url()

        headers = {
            'Referer': referer,
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0',
        }
        params = {
            'country': 'BR',
            'language': 'english',
            'currency': 7,
            'item_nameid': item_name_id,
        }

        response = requests.get(url, params=params, headers=headers, cookies=cookies)
        return response
