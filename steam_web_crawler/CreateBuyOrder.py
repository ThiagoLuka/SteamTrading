import requests

from .SteamWebPage import SteamWebPage


class CreateBuyOrder(SteamWebPage, name='create_buy_order'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'game_market_id', 'item_url_name', 'price', 'quantity',

    @staticmethod
    def required_cookies() -> tuple:
        return 'sessionid', 'steamLoginSecure',

    @staticmethod
    def required_referer() -> str:
        return 'item_market_page'

    def generate_url(self, **kwargs) -> str:
        return f'{super().BASESTEAMURL}market/createbuyorder/'

    def interact(self, cookies: dict, **kwargs) -> requests.Response:
        referer: str = kwargs['referer']
        game_market_id: str = kwargs['game_market_id']
        item_url_name: str = kwargs['item_url_name']
        price: int = kwargs['price']
        quantity: int = kwargs['quantity']

        url = self.generate_url()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': referer,
        }
        payload = {
            'sessionid': cookies['sessionid'],
            'currency': 7,
            'appid': 753,
            'market_hash_name': f'{game_market_id}-{requests.utils.unquote(item_url_name)}',
            'price_total': price * quantity,
            'quantity': quantity,
        }

        response = requests.post(url, data=payload, headers=headers, cookies=cookies)
        return response
