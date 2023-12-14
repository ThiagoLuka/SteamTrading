import requests

from .SteamWebPage import SteamWebPage


class CraftBadge(SteamWebPage, name='craft_badge'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'game_market_id',

    @staticmethod
    def required_cookies() -> tuple:
        return 'sessionid', 'steamLoginSecure',

    @staticmethod
    def required_referer() -> str:
        return 'game_cards_page'

    def generate_url(self, **kwargs) -> str:
        steam_alias = kwargs['steam_alias']
        return f'{super().BASESTEAMURL}id/{steam_alias}/ajaxcraftbadge/'

    def interact(self, cookies: dict, **kwargs) -> requests.Response:
        referer: str = kwargs['referer']
        game_market_id: str = kwargs['game_market_id']
        foil: bool = kwargs['foil'] if 'foil' in kwargs.keys() else False

        url = self.generate_url(**kwargs)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': referer
        }
        payload = {
            'appid': game_market_id,
            'series': 1,
            'border_color': int(foil),
            'levels': 1,
            'sessionid': cookies['sessionid']
        }

        response = requests.post(url, data=payload, headers=headers, cookies=cookies)
        return response