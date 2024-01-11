import requests

from .SteamWebPage import SteamWebPage


class CancelBuyOrder(SteamWebPage, name='cancel_buy_order'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'steam_buy_order_id', 'game_market_id', 'item_url_name',

    @staticmethod
    def required_cookies() -> tuple:
        return 'sessionid', 'steamLoginSecure',

    @staticmethod
    def required_referer() -> str:
        return 'item_market_page'

    def generate_url(self, **kwargs) -> str:
        return f'{super().BASESTEAMURL}market/cancelbuyorder/'

    def interact(self, cookies: dict, **kwargs) -> requests.Response:
        referer: str = kwargs['referer']
        steam_buy_order_id: str = kwargs['steam_buy_order_id']

        url = self.generate_url()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': referer,
        }
        payload = {
            'sessionid': cookies['sessionid'],
            'buy_orderid': steam_buy_order_id,
        }

        response = requests.post(url, data=payload, headers=headers, cookies=cookies)
        return response
