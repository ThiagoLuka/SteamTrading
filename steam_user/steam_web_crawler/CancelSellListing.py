import requests

from .SteamWebPage import SteamWebPage


class CancelSellListing(SteamWebPage, name='cancel_sell_listing'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'game_market_id', 'item_url_name', 'sell_listing_id',

    @staticmethod
    def required_cookies() -> tuple:
        return 'sessionid', 'steamLoginSecure',

    @staticmethod
    def required_referer() -> str:
        return 'item_market_page'

    def generate_url(self, **kwargs) -> str:
        sell_listing_id = kwargs['sell_listing_id']
        return f'{super().BASESTEAMURL}market/removelisting/{sell_listing_id}'

    def interact(self, cookies: dict, **kwargs) -> requests.Response:
        referer: str = kwargs['referer']

        url = self.generate_url(**kwargs)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': referer,
        }
        payload = {
            'sessionid': cookies['sessionid'],
        }

        response = requests.post(url, data=payload, headers=headers, cookies=cookies)
        return response
