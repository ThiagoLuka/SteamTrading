import requests

from .SteamWebPage import SteamWebPage


class InventoryPage(SteamWebPage, name='inventory_page'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'steam_id',

    @staticmethod
    def required_cookies() -> tuple:
        return 'steamMachineAuth', 'steamLoginSecure',

    def generate_url(self, **kwargs) -> str:
        if 'get_json' in kwargs.keys():
            steam_id: str = kwargs['steam_id']
            app_id = self.__get_inventory_appid(kwargs['get_json'])
            return f'{super().BASESTEAMURL}inventory/{steam_id}/{app_id}/6/'
        steam_alias: str = kwargs['steam_alias']
        return f'{super().BASESTEAMURL}id/{steam_alias}/inventory/'

    def interact(self, cookies: dict, **kwargs) -> requests.Response:
        items_per_page: int = kwargs['items_per_page'] if 'items_per_page' in kwargs.keys() else 2000
        start_assetid: str = kwargs['start_assetid'] if 'start_assetid' in kwargs.keys() else None

        kwargs['get_json'] = 'steam'
        url = self.generate_url(**kwargs)
        params = {
            'count': items_per_page,
            'start_assetid': start_assetid,
        }

        response = requests.get(url, params=params, cookies=cookies)
        return response

    @staticmethod
    def __get_inventory_appid(type_key: str) -> str:
        # this function should be moved elsewhere when the software starts dealing with inventories of different games
        return {
                'steam': '753',  # it's their game_market_id!
                'tf2': '440',
                'portal': '620',
            }.get(type_key)
