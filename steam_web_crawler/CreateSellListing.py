import requests

from .SteamWebPage import SteamWebPage


class CreateSellListing(SteamWebPage, name='create_sell_listing'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'asset_id', 'price', 'steam_alias',

    @staticmethod
    def required_cookies() -> tuple:
        return 'sessionid', 'steamLoginSecure',

    @staticmethod
    def required_referer() -> str:
        return 'inventory_page'

    def generate_url(self, **kwargs) -> str:
        return f'{super().BASESTEAMURL}market/sellitem/'

    def interact(self, cookies: dict, **kwargs) -> requests.Response:
        referer: str = kwargs['referer']
        asset_id: str = kwargs['asset_id']
        price: int = kwargs['price']

        url = self.generate_url()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': referer
        }
        payload = {
            'sessionid': cookies['sessionid'],
            'appid': 753,
            'contextid': 6,
            'assetid': asset_id,
            'amount': 1,
            'price': price,
        }

        response = requests.post(url, data=payload, headers=headers, cookies=cookies)
        return response
