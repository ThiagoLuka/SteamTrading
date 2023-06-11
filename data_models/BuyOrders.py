from datetime import datetime

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
        last_buy_order = self.get_item_last_buy_orders(self.df.loc[0, 'item_steam_id'], self.df.loc[0, 'user_id'])
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

    def finished(self) -> list[int]:
        finished_df = self.df[self.df['qtd_current'] == 0]
        item_ids = finished_df['item_steam_id'].to_list()
        return item_ids

    @staticmethod
    def get_game_last_buy_orders(game_id: int, user_id: int) -> 'BuyOrders':
        table = 'default'
        columns = BuyOrders._get_class_columns(table)
        data = BuyOrdersRepository.get_game_last_buy_orders(columns, game_id, user_id)
        return BuyOrders._from_db(table, data)

    @staticmethod
    def get_item_last_buy_orders(steam_item_id: int, user_id: int, amount: int = 1) -> 'BuyOrders':
        table = 'default'
        columns = BuyOrders._get_class_columns(table)
        data = BuyOrdersRepository.get_item_last_buy_orders(columns, steam_item_id, user_id, amount)
        return BuyOrders._from_db(table, data)

    @staticmethod
    def handle_empty_from_market_page(steam_item_id: int, user_id: int) -> None:
        last_buy_order = BuyOrders.get_item_last_buy_orders(steam_item_id, user_id)
        if last_buy_order.empty or not last_buy_order.df.loc[0, 'active']:
            return
        BuyOrdersRepository.set_last_buy_order_to_inactive(steam_item_id, user_id)

    @staticmethod
    def get_game_ids_with_most_outdated_orders(n_of_games: int, user_id: int) -> list:
        game_ids_and_date = BuyOrdersRepository.get_game_ids_with_most_outdated_orders(n_of_games, user_id)
        game_ids = [game_id for game_id, timestamp in game_ids_and_date]
        return game_ids

    @staticmethod
    def get_game_ids_to_be_updated(n_of_games: int, user_id: int) -> list:
        game_ids_and_date = BuyOrdersRepository.get_game_ids_to_create_buy_order(n_of_games, user_id)
        game_ids = [game_id for game_id, timestamp in game_ids_and_date]
        return game_ids
