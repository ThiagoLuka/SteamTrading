import requests

from .SteamWebPage import SteamWebPage


class CreateSellListing(SteamWebPage, name='sell_listing'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'asset_id', 'price', 'steam_alias',

    @staticmethod
    def required_cookies() -> tuple:
        return 'sessionid', 'steamLoginSecure',

    def interact(self, cookies: dict, **kwargs) -> requests.Response:
        asset_id: str = kwargs['asset_id']
        price: int = kwargs['price']
        steam_alias: str = kwargs['steam_alias']

        url = f"{super().BASESTEAMURL}market/sellitem/"

        payload = {
            'sessionid': cookies['sessionid'],
            'appid': 753,
            'contextid': 6,
            'assetid': asset_id,
            'amount': 1,
            'price': price,
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': f'{super().BASESTEAMURL}id/{steam_alias}/inventory?modal=1&market=1'
        }
        response = requests.post(url, data=payload, headers=headers, cookies=cookies)
        return response
