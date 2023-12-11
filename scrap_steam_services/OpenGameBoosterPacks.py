import requests
from typing import Union

from user_interfaces.GenericUI import GenericUI
from scrap_steam_services import ScrapInventory
from steam_user.SteamUser import SteamUser
from data_models.SteamInventory import SteamInventory
from data_models.SteamGames import SteamGames


class OpenGameBoosterPacks:

    def __init__(self, steam_user: SteamUser):
        self.__steam_user = steam_user

    def run(self, games_quantity: int) -> None:
        update_inventory_task = ScrapInventory(self.__steam_user)
        update_inventory_task.full_update()

        game_ids = SteamInventory.get_game_ids_with_booster_packs_to_be_opened(
            n_of_games=games_quantity,
            user_id=self.__steam_user.user_id
        )
        games = SteamGames.get_all_by_id(game_ids)

        for index, game in enumerate(games):
            print(f"{index+1} - {game['name']}")
            asset_ids: list = SteamInventory.get_booster_pack_assets_id(
                user_id=self.__steam_user.user_id,
                game_id=game['id']
            )

            progress_text = 'Opening booster packs'
            GenericUI.progress_completed(progress=0, total=len(asset_ids), text=progress_text)
            while asset_ids:
                for index2, asset_id in enumerate(asset_ids):
                    self.__post_request(asset_id)
                    GenericUI.progress_completed(progress=index2+1, total=len(asset_ids), text=progress_text)
                booster_pack_not_opened_asset_ids = update_inventory_task.after_booster_pack_opened(game['market_id'])
                asset_ids = booster_pack_not_opened_asset_ids

    def __post_request(self, asset_id: str) -> (int, Union[requests.Response, str]):
        custom_status_code, response = self.__steam_user.web_crawler.interact(
            'open_booster_pack',
            asset_id=asset_id,
        )
        return custom_status_code, response
