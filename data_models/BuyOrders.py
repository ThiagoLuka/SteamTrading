from datetime import datetime

from typing import Union

from repositories.BuyOrdersRepository import BuyOrdersRepository
from data_models.PandasDataModel import PandasDataModel
from data_models.PandasUtils import PandasUtils


class BuyOrders(
    PandasDataModel,
    tables={
        'buy_orders'
    },
    columns={
        'default': (
            'buy_order_id', 'steam_buy_order_id', 'user_id', 'item_steam_id', 'active', 'price',
            'qtd_start', 'qtd_estimate', 'qtd_current', 'created_at', 'updated_at', 'removed_at'),
        'buy_orders': (
            'buy_order_id', 'steam_buy_order_id', 'user_id', 'item_steam_id', 'active', 'price',
            'qtd_start', 'qtd_estimate', 'qtd_current', 'created_at', 'updated_at', 'removed_at'),
    },
    repository=BuyOrdersRepository
):

    def __init__(self, table: str = 'default', **data):
        super().__init__(table, **data)

    def save(self) -> None:
        last_buy_order = self.get_last_buy_order(self.df.item_steam_id, self.df.loc[0, 'user_id'])
        if last_buy_order.empty or not last_buy_order.df.loc[0, 'active']:
            to_save = self.df.copy()
            to_save['qtd_start'] = self.df['qtd_current']
            to_save['qtd_estimate'] = self.df['qtd_current']
            create_time = datetime.now()
            to_save['created_at'] = create_time
            to_save['updated_at'] = create_time
            cols_to_insert = self._get_class_columns('buy_orders')
            cols_to_insert.remove('buy_order_id')
            zipped_data = PandasUtils.zip_df_columns(to_save, cols_to_insert)
            BuyOrdersRepository.insert_multiple_buy_orders(zipped_data, cols_to_insert)
            return
        buy_order_id = last_buy_order.df.loc[0, 'buy_order_id']
        steam_buy_order_id = self.df.loc[0, 'steam_buy_order_id']
        qtd = self.df.loc[0, 'qtd_current']
        BuyOrdersRepository.update_buy_order(buy_order_id, steam_buy_order_id, qtd)
        return

    @staticmethod
    def get_last_buy_order(steam_item_ids: Union[list, str], user_id: int) -> 'BuyOrders':
        if type(steam_item_ids) == str:
            steam_item_ids = [steam_item_ids]
        table = 'default'
        columns = BuyOrders._get_class_columns(table)
        data = BuyOrdersRepository.get_last_buy_orders(columns, steam_item_ids, user_id)
        return BuyOrders._from_db(table, data)

    @staticmethod
    def handle_empty_from_market_page(steam_item_id: str, user_id: int) -> None:
        last_buy_order = BuyOrders.get_last_buy_order(steam_item_id, user_id)
        if last_buy_order.empty or not last_buy_order.df.loc[0, 'active']:
            return
        BuyOrdersRepository.set_last_buy_order_to_inactive(steam_item_id, user_id)

    @staticmethod
    def get_game_ids_with_most_outdated_orders(n_of_games: int) -> list:
        game_ids_and_oldest_order_date = BuyOrdersRepository.get_game_ids_with_most_outdated_orders(n_of_games)
        game_ids = [game_id for game_id, oldest_buy_order_timestamp in game_ids_and_oldest_order_date]
        return game_ids
