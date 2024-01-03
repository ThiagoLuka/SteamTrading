from __future__ import annotations
from typing import TYPE_CHECKING

from user_interfaces.GenericUI import GenericUI
from user_interfaces.SteamTraderUI import SteamTraderUI
from steam_games import SteamGames
from data_models import PersistToDB

if TYPE_CHECKING:
    from steam_user_trader.SteamUserTrader import SteamUserTrader


class CreateBuyOrders:

    def __init__(self, steam_trader: SteamUserTrader):
        self._steam_trader = steam_trader

    def create_buy_orders(self) -> None:
        if SteamTraderUI.create_first_buy_order_of_game():
            game_id = int(GenericUI.get_game_id())
            self._first_buy_orders(game_id=game_id)
            return
        item_quantity = SteamTraderUI.create_buy_orders_prompt_message()
        self._replace_outdated_buy_orders(item_quantity=item_quantity)

    def _replace_outdated_buy_orders(self, item_quantity: int):
        game_and_item_ids: dict = self._steam_trader.buy_orders.get_game_and_item_ids_without_active(item_quantity=item_quantity)
        games = SteamGames(game_ids=list(game_and_item_ids.keys()), with_items=True)

        for idx, game_and_item_ids_tuple in enumerate(game_and_item_ids.items()):
            game_id = game_and_item_ids_tuple[0]
            item_ids = game_and_item_ids_tuple[1]
            game_name = games.name(game_id=game_id)
            game_market_id = games.market_id(game_id=game_id)
            items = games.get_trading_cards_and_booster_pack(game_id=game_id, foil=False)
            buy_orders_history = self._steam_trader.buy_orders.get_recent_history(game_id=game_id)

            SteamTraderUI.game_header_with_counter(game_name=game_name, index=idx)
            SteamTraderUI.show_game_recent_buy_orders(
                items=items,
                buy_orders_history=buy_orders_history
            )
            for idx2, steam_item in enumerate(items):
                item_id = steam_item['item_id']
                if item_id in item_ids:
                    SteamTraderUI.show_item_name(item_name=steam_item['item_name'], set_number=steam_item['set_number'])
                    SteamTraderUI.show_item_all_buy_orders(
                        item=steam_item,
                        buy_orders=buy_orders_history[item_id]
                    )
                    self._create_item_buy_order(
                        steam_item=steam_item,
                        game_market_id=game_market_id,
                    )

    def _first_buy_orders(self, game_id: int):
        game = SteamGames(game_ids=[game_id], with_items=True)
        game_market_id = game.market_id(game_id=game_id)
        items = game.get_trading_cards_and_booster_pack(game_id=game_id, foil=False)
        for index, steam_item in enumerate(items):
            SteamTraderUI.show_item_name(item_name=steam_item['item_name'], set_number=steam_item['set_number'])
            self._create_item_buy_order(
                steam_item=steam_item,
                game_market_id=game_market_id,
            )

    def _create_item_buy_order(self, steam_item: dict, game_market_id: str) -> None:
        item_id = steam_item['item_id']
        item_market_url_name = steam_item['item_market_url_name']
        self._steam_trader.open_market_item_page_in_browser(
            game_market_id=game_market_id,
            item_market_url_name=item_market_url_name
        )
        price, qtd = SteamTraderUI.set_buy_order_for_item()
        if not price or not qtd:
            return
        self._steam_trader.market_actions_queue.put((
            'create_buy_order', {
                'item_id': item_id,
                'item_url_name': item_market_url_name,
                'price': price,
                'qtd': qtd,
                'game_market_id': game_market_id
            }))

    @staticmethod
    def queue_task(steam_trader: SteamUserTrader, **kwargs) -> None:
        item_id = kwargs['item_id']
        item_url_name = kwargs['item_url_name']
        price = kwargs['price']
        qtd = kwargs['qtd']
        game_market_id = kwargs['game_market_id']
        status, result = steam_trader.web_crawler.interact(
            'create_buy_order',
            game_market_id=game_market_id,
            item_url_name=item_url_name,
            price=price,
            quantity=qtd
        )
        response_content = result.json()
        if response_content['success'] == 1:
            PersistToDB.persist('buy_order', source='create_buy_order',
                data=[{
                    'item_id': item_id,
                    'steam_buy_order_id': response_content['buy_orderid'],
                    'quantity': qtd,
                    'price': price,
                }],
                user_id=steam_trader.user_id
            )
            return
        SteamTraderUI.create_buy_order_failed()

