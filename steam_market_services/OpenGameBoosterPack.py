from __future__ import annotations
from typing import Union, TYPE_CHECKING
import requests

from user_interfaces.GenericUI import GenericUI
from user_interfaces.SteamTraderUI import SteamTraderUI
from steam_games import SteamGames
from steam_user_trader.ItemPriceTable import ItemPriceTable
from data_models import PersistToDB

if TYPE_CHECKING:
    from steam_user_trader.SteamUserTrader import SteamUserTrader


class OpenGameBoosterPack:

    def __init__(self, steam_user: SteamUserTrader):
        self._steam_trader = steam_user
        self._price_rate_to_open_bp = 1.1

    def run(self, games_quantity: int = 0, allowed_game_ids: list = None) -> None:
        self._steam_trader.update_inventory()

        if not allowed_game_ids:
            allowed_game_ids: list[int] = self._steam_trader.inventory.get_all_game_ids()
        else:
            games_quantity = len(allowed_game_ids)
        games = SteamGames(allowed_game_ids, with_items=True)
        bp_item_ids: list[int] = games.get_booster_pack_item_ids()
        game_ids = self._steam_trader.inventory.get_game_ids(item_ids=bp_item_ids, qtd=games_quantity, sort='created_at')

        for index, game_id in enumerate(game_ids):
            game_market_id = games.market_id(game_id=game_id)
            SteamTraderUI.game_header_with_counter(games.name(game_id=game_id), index=index)

            item_keys = ['item_id', 'item_market_url_name', 'steam_item_name_id', 'steam_item_type']
            items = games.get_trading_cards_and_booster_pack(game_id=game_id, item_keys=item_keys, foil=False)
            tcgs = [item_dict for item_dict in items if item_dict['steam_item_type'] == 'Trading Card']
            bp = [item_dict for item_dict in items if item_dict['steam_item_type'] == 'Booster Pack'][0]
            bp_assets = self._steam_trader.inventory.get_asset_ids(item_id=bp['item_id'], origin_undefined=False)
            if not bp_assets:
                continue

            SteamTraderUI.comparing_bp_and_cards_prices()
            bp_seller_price = self._item_seller_price(item=bp, game_market_id=game_market_id)
            tcgs_mean_seller_price = self._tcgs_mean_seller_price(tcgs=tcgs, game_market_id=game_market_id)
            SteamTraderUI.bp_and_card_price_comparison(bp_price=bp_seller_price, card_price=tcgs_mean_seller_price)
            better_to_sell_bp = ( self._price_rate_to_open_bp < ( bp_seller_price / (3 * tcgs_mean_seller_price) ) )
            if better_to_sell_bp:
                continue

            qtd_booster_packs = len(bp_assets)
            progress_text = f"{index + 1:02d} - Opening booster packs"
            GenericUI.progress_completed(progress=0, total=len(bp_assets), text=progress_text)
            while bp_assets:
                for index2, asset_id in enumerate(bp_assets):
                    self._post_request(asset_id)
                    GenericUI.progress_completed(progress=index2+1, total=len(bp_assets), text=progress_text)
                self._steam_trader.update_inventory()
                bp_assets = self._steam_trader.inventory.get_asset_ids(item_id=bp['item_id'], origin_undefined=False)

            PersistToDB.persist('steam_asset_origin', source='open_booster_pack',
                user_id=self._steam_trader.user_id,
                game_id=game_id,
                booster_packs_opened=qtd_booster_packs,
            )

    def _tcgs_mean_seller_price(self, tcgs: list[dict], game_market_id: str) -> float:
        tcgs_total_seller_price = 0
        for tcg in tcgs:
            tcgs_total_seller_price += self._item_seller_price(item=tcg, game_market_id=game_market_id)
        return tcgs_total_seller_price / len(tcgs)


    def _item_seller_price(self, item: dict, game_market_id: str) -> int:
        return ItemPriceTable(
                steam_trader=self._steam_trader,
                game_market_id=game_market_id,
                item=item,
            ).recommended_seller_price()

    def _post_request(self, asset_id: str) -> (int, Union[requests.Response, str]):
        custom_status_code, response = self._steam_trader.web_crawler.interact(
            'open_booster_pack',
            asset_id=asset_id,
        )
        return custom_status_code, response
