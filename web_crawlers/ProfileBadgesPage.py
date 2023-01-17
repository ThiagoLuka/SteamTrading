import requests

from .SteamWebPage import SteamWebPage


class ProfileBadgesPage(SteamWebPage, name='profile_badges'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'steam_id',

    @staticmethod
    def required_cookies() -> tuple:
        return 'timezoneOffset',

    def generate_url(self, **kwargs) -> str:
        steam_id: str = kwargs['steam_id']
        return f'{super().BASESTEAMURL}profiles/{steam_id}/badges/'

    def interact(self, cookies: dict, **kwargs) -> requests.Response:
        page: int = kwargs['page']

        url = self.generate_url(**kwargs)
        params = {
            'sort': 'a',
            'p': page
        }

        response = requests.get(url, params=params, cookies=cookies)
        return response
