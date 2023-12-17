from __future__ import annotations
from typing import Union, TYPE_CHECKING
import requests

from user_interfaces.GenericUI import GenericUI
from steam_games import SteamGames

if TYPE_CHECKING:
    from steam_user.SteamUser import SteamUser


class OpenGameBoosterPacks:

    def __init__(self, steam_user: SteamUser):
        self.__steam_user = steam_user

    def run(self, games_quantity: int) -> None:
        self.__steam_user.update_inventory()

        inv_game_ids: list[int] = self.__steam_user.inventory.get_all_game_ids()
        games = SteamGames(inv_game_ids, with_items=True)
        bp_item_ids: list[int] = games.get_booster_pack_item_ids()
        steam_asset_ids: dict[tuple[int, int], list] = self.__steam_user.inventory.get_steam_asset_ids_by_item_ids(item_ids=bp_item_ids)

        for index, assets_info in enumerate(steam_asset_ids.items()):
            game_id, item_id = assets_info[0]
            bp_assets = assets_info[1]
            if index >= games_quantity:
                break
            progress_text = f"{index+1:02d} - Opening booster packs: {games.name(game_id=game_id)}"
            GenericUI.progress_completed(progress=0, total=len(bp_assets), text=progress_text)
            while bp_assets:
                for index2, asset_id in enumerate(bp_assets):
                    self.__post_request(asset_id)
                    GenericUI.progress_completed(progress=index2+1, total=len(bp_assets), text=progress_text)
                bps_not_opened = self.__steam_user.update_inventory_after_booster_pack(game_market_id=games.market_id(game_id=game_id))
                bp_assets = bps_not_opened

    def __post_request(self, asset_id: str) -> (int, Union[requests.Response, str]):
        custom_status_code, response = self.__steam_user.web_crawler.interact(
            'open_booster_pack',
            asset_id=asset_id,
        )
        return custom_status_code, response
