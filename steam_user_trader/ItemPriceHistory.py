from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
import time
import math

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from steam_user_trader.SteamUserTrader import SteamUserTrader


class ItemPriceHistory:

    def __init__(self, steam_trader: SteamUserTrader, game_market_id: str, item: dict, days_to_analyze: int):
        self._days_to_analyze = days_to_analyze
        retries = 4
        while retries >= 0:
            status, response = steam_trader.web_crawler.interact(
                'item_prices_history',
                game_market_id=game_market_id,
                item_url_name=item['item_market_url_name'],
            )
            if status == 200:
                break
            time.sleep(30)
            retries -= 1

        data = response
        prices = [
            [datetime.strptime(p[0], '%b %d %Y %H: +0').date(),
             p[1], int(p[2])]
            for p in data['prices']
        ]

        df = pd.DataFrame(prices, columns=['day', 'price', 'qtd'])
        df['day'] = pd.to_datetime(df['day'])
        df.sort_values(by='day', ascending=False, ignore_index=True, inplace=True)
        self._df = df
        self._df_daily = self._to_daily_prices(df=df)

    def buyer_price_rounded_empirical_rule_95_range(self) -> list[int]:
        w_avg = self.recent_daily_weighted_price_avg()
        w_std = self.recent_daily_weighted_price_stddev()
        w_std = w_std if not math.isnan(w_std) else 0
        lower = round(100*(w_avg - 2*w_std))
        higher = round(100*(w_avg + 2*w_std))
        return [lower, higher]

    def recent_sum(self) -> int:
        df = self._df_daily[0:self._days_to_analyze]
        return df['qtd'].sum()

    def recent_daily_weighted_price_avg(self) -> int:
        df = self._df_daily[0:self._days_to_analyze]
        w_avg = np.average(df['price'], weights=df['qtd'])
        return w_avg

    def recent_daily_weighted_price_stddev(self) -> int:
        df = self._df_daily[0:self._days_to_analyze]
        w_cov = np.cov(df['price'], aweights=df['qtd'])
        w_stddev = np.sqrt(w_cov)
        return w_stddev

    @staticmethod
    def _to_daily_prices(df: pd.DataFrame) -> pd.DataFrame:
        qtd_sum = df['qtd'].groupby(df['day']).sum()
        prices_w_avg = (df['price'] * df['qtd']).groupby(df['day']).sum() / qtd_sum
        daily_prices = pd.concat([prices_w_avg, qtd_sum], axis=1).reset_index()
        daily_prices.rename(columns={0: 'price'}, inplace=True)
        daily_prices.sort_values(by='day', ascending=False, ignore_index=True, inplace=True)
        return daily_prices
