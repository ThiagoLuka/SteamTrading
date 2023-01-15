import requests
from typing import Union

from user_interfaces.GenericUI import GenericUI
from web_crawlers import SteamWebCrawler
from data_models.SteamInventory import SteamInventory


class OpenGameBoosterPacks:

    def run(self, web_crawler: SteamWebCrawler, **required_data) -> None:
        user_id: int = required_data['user_id']
        steam_alias: str = required_data['steam_alias']
        game_name: str = required_data['game_name']

        asset_ids: list = SteamInventory.get_booster_pack_assets_id(
            user_id=user_id,
            game_name=game_name
        )

        progress_text = 'Opening booster packs'
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)

        for counter, asset_id in enumerate(asset_ids):
            self.__post_request(web_crawler, steam_alias, asset_id)
            GenericUI.progress_completed(progress=counter + 1, total=len(asset_ids), text=progress_text)

    @staticmethod
    def __post_request(
            web_crawler: SteamWebCrawler, steam_alias: str, asset_id: str
    ) -> (int, Union[requests.Response, str]):
        custom_status_code, response = web_crawler.interact(
            'open_booster_pack',
            asset_id=asset_id,
            steam_alias=steam_alias,
        )
        return custom_status_code, response
