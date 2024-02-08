from urllib.request import Request, urlopen
import json

from .SteamWebPage import SteamWebPage


class ItemPricesHistory(SteamWebPage, name='item_prices_history'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'game_market_id', 'item_url_name',

    @staticmethod
    def required_cookies() -> tuple:
        return 'sessionid', 'steamLoginSecure',

    @staticmethod
    def required_referer() -> str:
        return 'item_market_page'

    def generate_url(self, **kwargs) -> str:
        return f'{super().BASESTEAMURL}market/pricehistory'

    def interact(self, cookies: dict, **kwargs) -> dict:
        game_market_id: str = kwargs['game_market_id']
        item_url_name: str = kwargs['item_url_name']

        url = self.generate_url()
        url += f'?appid=753&market_hash_name={game_market_id}-{item_url_name}'

        cookies_list = []
        for cookie_key, cookie_value in cookies.items():
            cookies_list.append(f'{cookie_key}={cookie_value}')
        urllib_header = {'Cookie': '; '.join(cookies_list)}

        req = Request(url, headers=urllib_header)
        page = urlopen(req).read()
        json_res = json.loads(page)

        return json_res
