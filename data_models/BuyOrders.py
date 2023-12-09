from repositories.BuyOrdersRepository import BuyOrdersRepository
from data_models.PandasDataModel import PandasDataModel


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
    def get_game_ids_with_most_outdated_orders(n_of_games: int, user_id: int) -> list:
        game_ids_and_date = BuyOrdersRepository.get_game_ids_with_most_outdated_orders(n_of_games, user_id)
        game_ids = [game_id for game_id, timestamp in game_ids_and_date]
        return game_ids

    @staticmethod
    def get_game_ids_to_be_updated(n_of_games: int, user_id: int) -> list:
        game_ids_and_date = BuyOrdersRepository.get_game_ids_to_create_buy_order(n_of_games, user_id)
        game_ids = [game_id for game_id, timestamp in game_ids_and_date]
        return game_ids
