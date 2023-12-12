import requests

from .SteamWebPage import SteamWebPage


class SellListingPage(SteamWebPage, name='sell_listing_page'):

    @staticmethod
    def required_user_data() -> tuple:
        return ()

    @staticmethod
    def required_cookies() -> tuple:
        return 'steamLoginSecure',

    def generate_url(self, **kwargs) -> str:
        return f'{super().BASESTEAMURL}market/mylistings/'

    def interact(self, cookies: dict, **kwargs) -> requests.Response:
        listings_per_page: int = kwargs['listings_per_page'] if 'listings_per_page' in kwargs.keys() else 100
        listings_start_count: int = kwargs['listings_start_count'] if 'listings_start_count' in kwargs.keys() else None

        url = self.generate_url(**kwargs)
        params = {
            'start': listings_start_count,
            'count': listings_per_page
        }

        response = requests.get(url, params=params, cookies=cookies)
        return response
