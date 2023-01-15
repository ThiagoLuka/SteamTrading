import requests

from .SteamWebPage import SteamWebPage


class ProfileBadgesPage(SteamWebPage, name='get_profile_badges'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'steam_id',

    @staticmethod
    def required_cookies() -> tuple:
        return 'timezoneOffset',

    def interact(self, cookies: dict, **kwargs) -> requests.Response:
        steam_id: str = kwargs['steam_id']
        page: int = kwargs['page']

        url = f'{super().BASESTEAMURL}profiles/{steam_id}/badges/'
        params = {
            'sort': 'a',
            'p': page
        }
        response = requests.get(url, params=params, cookies=cookies)
        return response
