import requests

from .SteamWebPage import SteamWebPage


class OpenBoosterPack(SteamWebPage, name='open_booster_pack'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'steam_alias', 'asset_id',

    @staticmethod
    def required_cookies() -> tuple:
        return 'sessionid', 'steamLoginSecure',

    def interact(self, cookies: dict, **kwargs) -> requests.Response:
        asset_id: list = kwargs['asset_id']
        steam_alias: str = kwargs['steam_alias']

        url = f"{super().BASESTEAMURL}id/{steam_alias}/ajaxunpackbooster/"
        payload = {
            'communityitemid': asset_id,
            'sessionid': cookies['sessionid']
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        response = requests.post(url, data=payload, headers=headers, cookies=cookies)
        # sometimes its response comes 500 even when the booster pack is opened. Go figure
        return response
