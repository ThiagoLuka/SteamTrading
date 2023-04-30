import requests
import webbrowser

from .SteamWebPage import SteamWebPage


class ItemMarketPage(SteamWebPage, name='item_market_page'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'game_market_id', 'item_url_name',

    @staticmethod
    def required_cookies() -> tuple:
        return 'steamLoginSecure',

    def generate_url(self, **kwargs) -> str:
        game_market_id: str = kwargs['game_market_id']
        item_url_name: str = kwargs['item_url_name']
        return f'{super().BASESTEAMURL}market/listings/753/{game_market_id}-{item_url_name}'

    def interact(self, cookies: dict, **kwargs) -> requests.Response:

        url = self.generate_url(**kwargs)

        if 'open_web_browser' in kwargs.keys():
            if kwargs['open_web_browser']:
                webbrowser.open(url, new=2)

        response = requests.get(url, cookies=cookies)
        return response
