import pandas as pd

from data_models.query.BuyOrdersRepository import BuyOrdersRepository


class BuyOrders:

    def __init__(self, user_id: int):
        self._user_id = user_id
        self._df_active = pd.DataFrame()
        self._df_most_recent_inactive = pd.DataFrame()
        self.reload_current()

    @property
    def df(self) -> pd.DataFrame:
        return self._df_active.copy()

    def reload_current(self) -> None:
        columns = ['id', 'game_id', 'item_id', 'steam_id', 'price', 'qtd_start', 'qtd_current', 'created_at', 'updated_at', 'removed_at']
        db_data = BuyOrdersRepository.get_current_buy_orders(user_id=self._user_id)
        self._df_active = pd.DataFrame(db_data, columns=columns)
        db_data = BuyOrdersRepository.get_inactive_with_created_at_rank(user_id=self._user_id)
        df = pd.DataFrame(db_data, columns=columns + ['created_at_rank'])
        df = df[df['created_at_rank'] <= 2]
        self._df_most_recent_inactive = df.drop(columns='created_at_rank')

    def get_game_ids_with_most_outdated_orders(self, quantity: int) -> list[int]:
        df_aux = self.df.sort_values(by='updated_at')
        df_aux.drop_duplicates('game_id', inplace=True)
        return list(df_aux['game_id'].iloc[0:quantity])
