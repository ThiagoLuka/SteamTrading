import pandas as pd
from datetime import datetime

from data_models import QueryDB


class SellListings:

    def __init__(self, user_id: int):
        self._user_id = user_id
        self._df = pd.DataFrame()
        self.reload_current()

    @property
    def df(self) -> pd.DataFrame:
        return self._df.copy()

    def reload_current(self) -> None:
        columns = [
            'id',
            'game_id',
            'item_id',
            'asset_id',
            'steam_sell_listing_id',
            'price_buyer',
            'price_to_receive',
            'steam_created_at',
            'created_at',
            'removed_at',
        ]
        db_data = QueryDB.get_repo('sell_listing').get_current_sell_listings(user_id=self._user_id)
        self._df = pd.DataFrame(db_data, columns=columns)

    def get_items_older_than(self, days: int) -> list[dict]:
        """:return [{item_id, game_id, steam_created_at, price_to_receive}]"""
        df = self.df
        df['today'] = datetime.today()
        df = df[(df['today'].dt.date - df['steam_created_at']).dt.days > days].copy()
        df.sort_values('steam_created_at', inplace=True)
        item_info = ['item_id', 'game_id', 'steam_created_at', 'price_to_receive']
        df = df[item_info].copy()
        result = df.drop_duplicates().to_dict('records')
        return result

    def get_steam_ids(self, item_id: int, steam_created_at: datetime.date, price_to_receive: int) -> list[str]:
        df = self._df
        steam_sell_listing_ids = list(df.loc[
            (df['item_id'] == item_id)
            & (df['steam_created_at'] == steam_created_at)
            & (df['price_to_receive'] == price_to_receive)
        , 'steam_sell_listing_id'])
        return steam_sell_listing_ids

    def item_price_seller_summary(self, item_id: int) -> dict:
        """:return {price: qtd}"""
        df = self.df
        df = df[df['item_id'] == item_id]
        return dict(df.value_counts(subset='price_to_receive'))

    @staticmethod
    def buyer_to_seller_price_dict() -> dict:
        """:return {price_buyer: price_seller}"""
        db_data = QueryDB.get_repo('sell_listing').get_buyer_to_seller_price_dict()
        return dict(db_data)
