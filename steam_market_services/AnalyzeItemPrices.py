from __future__ import annotations
from typing import TYPE_CHECKING

from user_interfaces.SteamTraderUI import SteamTraderUI
from steam_games import SteamGames
from steam_user_trader.ItemPriceTable import ItemPriceTable
from steam_user_trader.ItemPriceHistory import ItemPriceHistory

if TYPE_CHECKING:
    from steam_user_trader.SteamUserTrader import SteamUserTrader


class AnalyzeItemPrices:

    def __init__(self, steam_trader: SteamUserTrader):
        self._steam_trader = steam_trader
        self._filename = 'reports/price_analysis.txt'
        with open(self._filename, 'w') as file:
            SteamTraderUI.starting_price_analysis(show_date=True, file=file)
            SteamTraderUI.starting_price_analysis()

    def run(self, game_ids: list[int], days_to_analyze_history: int = 60) -> None:
        games = SteamGames(game_ids=game_ids, with_items=True)

        buyer_to_seller_price = self._steam_trader.sell_listings.buyer_to_seller_price_dict()

        for idx, game_id in enumerate(game_ids):
            game_name = games.name(game_id=game_id)
            game_market_id = games.market_id(game_id=game_id)
            items = games.get_trading_cards_and_booster_pack(game_id=game_id, foil=False)
            buy_orders_history = self._steam_trader.buy_orders.get_recent_history(game_id=game_id)

            with open(self._filename, 'a') as file:
                SteamTraderUI.game_header_with_counter(game_name=game_name, index=idx)
                SteamTraderUI.game_header_with_counter(game_name=game_name, index=idx, file=file)
                print(f'game_id  : {game_id}', file=file)
                SteamTraderUI.show_game_recent_buy_orders(
                    items=items,
                    buy_orders_history=buy_orders_history,
                    file=file
                )
                print('', file=file)

            for idx2, item in enumerate(items):
                item_id = item['item_id']
                market_prices = ItemPriceTable(
                    steam_trader=self._steam_trader,
                    game_market_id=game_market_id,
                    item=item
                )
                prices_history = ItemPriceHistory(
                    steam_trader=self._steam_trader,
                    game_market_id=game_market_id,
                    item=item,
                    days_to_analyze=days_to_analyze_history
                )
                current_range_l = market_prices.highest_buy_order_seller_price()
                current_range_h = market_prices.lowest_sell_order_seller_price()
                hist_range_l, hist_range_h = prices_history.buyer_price_rounded_empirical_rule_95_range()
                hist_range_h = self._get_nearest_seller_price(price=hist_range_h, buyer_to_seller_price=buyer_to_seller_price)

                recent_qtd_sold = prices_history.recent_sum()

                last_buy_order_price = buy_orders_history[item_id][0]['price']

                with open(self._filename, 'a') as file:
                    SteamTraderUI.show_item_name(item_name=item['item_name'], set_number=item['set_number'], file=file)
                    print(f'last_buy_order_price   : {last_buy_order_price}\n'
                          f'current_profit_range   : {current_range_h} - {current_range_l}\n'
                          f'history_profit_range   : {hist_range_h} - {hist_range_l}\n'
                          f'dayly sold last {days_to_analyze_history} days: {recent_qtd_sold / days_to_analyze_history:.3f}\n',
                          file=file
                          )

    @staticmethod
    def _get_nearest_seller_price(price: int, buyer_to_seller_price: dict) -> int:
        last_price = 3
        for buyer_price, seller_price in buyer_to_seller_price.items():
            if price < buyer_price:
                return last_price
            last_price = seller_price


