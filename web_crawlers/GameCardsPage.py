import requests

from .SteamWebPage import SteamWebPage


class GameCardsPage(SteamWebPage, name='get_trading_cards'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'steam_id', 'game_market_id',

    @staticmethod
    def required_cookies() -> tuple:
        return ()

    def interact(self, cookies: dict, **kwargs) -> requests.Response:
        steam_id: str = kwargs['steam_id']
        game_market_id: str = kwargs['game_market_id']

        url = f"{super().BASESTEAMURL}profiles/{steam_id}/gamecards/{game_market_id}"
        response = requests.get(url, cookies=cookies)
        return response
