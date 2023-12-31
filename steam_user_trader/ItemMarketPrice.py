from __future__ import annotations
from typing import TYPE_CHECKING
import time


if TYPE_CHECKING:
    from steam_user_trader.SteamUserTrader import SteamUserTrader


class ItemMarketPrice:

    def __init__(self, steam_trader: SteamUserTrader, game_market_id: str, item: dict):
        status, response = steam_trader.web_crawler.interact(
            'item_prices_table',
            item_name_id=item['steam_item_name_id'],
            game_market_id=game_market_id,
            item_url_name=item['item_market_url_name'],
        )
        time.sleep(5)
        data = response.json()

        self._total_for_sale = int(data['sell_order_summary'].split('>')[1].split('<')[0])
        self._total_buy_orders = int(data['buy_order_summary'].split('>')[1].split('<')[0])

        # {price: qtd_at_that_price}
        buyer_to_seller_price = steam_trader.sell_listings.buyer_to_seller_price_dict()
        self._sell_orders = {buyer_to_seller_price[round(line[0]*100)]: line[1] for line in data['sell_order_graph']}
        self._buy_orders = {round(line[0]*100): line[1] for line in data['buy_order_graph']}

        sell_listings_summary = steam_trader.sell_listings.item_price_seller_summary(item_id=item['item_id'])
        self._sell_orders_discounted = self._sell_orders.copy()
        for sl_price, sl_qtd in sell_listings_summary.items():
            for market_price in self._sell_orders_discounted.keys():
                if sl_price <= market_price:
                    self._sell_orders_discounted[market_price] -= sl_qtd


    def highest_buy_order_price(self) -> int:
        return max(self._buy_orders.keys())

    def lowest_sell_order_price(self) -> int:
        return min(self._sell_orders.keys())

    def recommended_seller_price(self) -> int:
        if self._total_for_sale <= 150:
            return self.low_total_for_sale_strategy()
        return self.regular_total_for_sale_strategy()

    def low_total_for_sale_strategy(self) -> int:
        return self.lowest_sell_order_price()

    def regular_total_for_sale_strategy(self) -> int:
        for price, qtd in self._sell_orders_discounted.items():
            if qtd >= 20:
                return price-1
