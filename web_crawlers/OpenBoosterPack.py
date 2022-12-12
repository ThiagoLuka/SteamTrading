import requests

from user_interfaces.GenericUI import GenericUI
from web_crawlers.SteamWebPage import SteamWebPage


class OpenBoosterPack(SteamWebPage, name='open_booster_pack'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'booster_pack_assets_ids', 'steam_alias',

    @staticmethod
    def required_cookies() -> tuple:
        return 'sessionid', 'steamLoginSecure',

    def interact(self, cookies: dict, **kwargs) -> None:
        booster_pack_assets_ids: list = kwargs['booster_pack_assets_ids']
        steam_alias: str = kwargs['steam_alias']

        self.__open_booster_pack(booster_pack_assets_ids, steam_alias, cookies)

    def __open_booster_pack(self, booster_pack_assets_id: list,steam_alias: str, cookies: dict) -> None:
        progress_text = 'Opening booster packs'
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)

        url = f"{super().BASESTEAMURL}id/{steam_alias}/ajaxunpackbooster/"
        for counter, asset_id in enumerate(booster_pack_assets_id):
            payload = {
                'communityitemid': asset_id,
                'sessionid': cookies['sessionid']
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
            requests.post(url, data=payload, headers=headers, cookies=cookies)
            GenericUI.progress_completed(progress=counter + 1, total=len(booster_pack_assets_id), text=progress_text)
