from __future__ import annotations
from typing import TYPE_CHECKING

from user_interfaces.SteamTraderUI import SteamTraderUI
from steam_games import SteamGames
from data_models import PersistToDB

if TYPE_CHECKING:
    from steam_user_trader.SteamUserTrader import SteamUserTrader


class RemoveSellListings:

    def __init__(self, steam_trader: SteamUserTrader):
        self._steam_trader = steam_trader

    def older_than(self, days_old: int = 140) -> None:
        SteamTraderUI.remove_old_sell_listing()
        sell_listings = self._steam_trader.sell_listings
        item_with_sl_to_cancel = sell_listings.get_items_older_than(days=days_old)
        game_ids = list(set(item['game_id'] for item in item_with_sl_to_cancel))
        games = SteamGames(game_ids=game_ids, with_items=True)

        for item_info in item_with_sl_to_cancel:
            item_id = item_info['item_id']
            game_id = item_info['game_id']
            created_at = item_info['steam_created_at']
            price_to_receive = item_info['price_to_receive']

            game_market_id = games.market_id(game_id=game_id)
            item_market_url_name = games.get_item_market_url_name(item_id=item_id)
            item_name = games.get_item_name(item_id=item_id)
            game_name = games.id_name_dict()[game_id]
            steam_sell_listing_ids = sell_listings.get_steam_ids(
                item_id=item_id,
                steam_created_at=created_at,
                price_to_receive=price_to_receive
            )
            SteamTraderUI.show_item_info_remove_sell_listing(
                item_name=item_name,
                game_name=game_name,
                created_at=created_at,
                price_to_receive=price_to_receive,
            )
            for steam_sell_listing_id in steam_sell_listing_ids:
                self._cancel_sell_listing(
                    game_market_id=game_market_id,
                    item_url_name=item_market_url_name,
                    sell_listing_id=steam_sell_listing_id,
                )
        self._steam_trader.update_inventory()
        PersistToDB.persist('steam_asset_origin', source='remove_sell_listing')

    def _cancel_sell_listing(self, game_market_id: str, item_url_name: str, sell_listing_id: str) -> None:
        status, result = self._steam_trader.web_crawler.interact(
            'cancel_sell_listing',
            game_market_id=game_market_id,
            item_url_name=item_url_name,
            sell_listing_id=sell_listing_id,
        )
        PersistToDB.persist('sell_listing', source='remove_sell_listing',
            steam_sell_listing_id=sell_listing_id
        )