from __future__ import annotations
from typing import TYPE_CHECKING
import time

from user_interfaces.SteamTraderUI import SteamTraderUI
from steam_games import SteamGames

if TYPE_CHECKING:
    from steam_user_trader.SteamUserTrader import SteamUserTrader


class CreateSellListings:

    def __init__(self, steam_trader: SteamUserTrader):
        self._steam_trader = steam_trader

    def create_sell_listings(self) -> None:
        game_quantity = SteamTraderUI.sell_cards_prompt_message()
        games_allowed = self._steam_trader.get_games_allowed()
        game_ids = self._steam_trader.inventory.get_game_ids_with_marketable_items(
            game_quantity=game_quantity,
            games_allowed=games_allowed,
        )
        games = SteamGames(game_ids=game_ids, with_items=True)
        inventory_summary = self._steam_trader.inventory.summary_qtd(by='item', marketable=True)

        for idx, game_id in enumerate(game_ids):
            game_name = games.name(game_id=game_id)
            game_market_id = games.market_id(game_id=game_id)

            items = games.get_trading_cards_and_booster_pack(game_id=game_id, foil=False)
            buy_orders_history = self._steam_trader.buy_orders.get_recent_history(game_id=game_id)
            SteamTraderUI.buy_orders_header(game_name=game_name, index=idx)
            SteamTraderUI.show_game_recent_buy_orders(
                items=items,
                buy_orders_history=buy_orders_history
            )

            items = games.get_trading_cards_and_booster_pack(game_id=game_id)
            game_summary = {item['item_id']: inventory_summary[item['item_id']] for item in items if item['item_id'] in inventory_summary.keys()}
            SteamTraderUI.show_marketable_items_to_sell_summary(items=items, summary=game_summary)

            for idx2, item in enumerate(items):
                item_id = item['item_id']
                item_market_url_name = item['item_market_url_name']
                if item_id in inventory_summary.keys():
                    self._steam_trader.open_market_item_page_in_browser(
                        game_market_id=game_market_id,
                        item_market_url_name=item_market_url_name
                    )
                    SteamTraderUI.show_item_name(item_name=item['item_name'], set_number=item['set_number'])
                    if item_id in list(buy_orders_history.keys()):
                        SteamTraderUI.show_item_all_buy_orders(
                            item=item,
                            buy_orders=buy_orders_history[item_id],
                            reverse=True,
                        )
                    price = SteamTraderUI.set_sell_price_for_item()
                    asset_ids = self._steam_trader.inventory.get_asset_ids(item_id=item_id, marketable=True)
                    self._steam_trader.market_actions_queue.put((
                        'create_sell_listing', {
                            'asset_ids': asset_ids,
                            'price': price,
                        }))

    @staticmethod
    def queue_task(steam_trader: SteamUserTrader, **kwargs) -> None:
        asset_ids = kwargs['asset_ids']
        price = kwargs['price']
        for asset_id in asset_ids:
            if steam_trader.cards_sold_count % 100 == 0:
                time.sleep(10)
            status, result = steam_trader.web_crawler.interact(
                'create_sell_listing',
                asset_id=asset_id,
                price=price,
            )
            if status != 200:
                print(f'\n{status}: {result}\n')
                return
            steam_trader.cards_sold_count += 1