from datetime import datetime

import pandas as pd

from data_models import QueryDB


class BuyOrders:

    def __init__(self, user_id: int):
        self._user_id = user_id
        self._df_active = pd.DataFrame()
        self._df_most_recent_inactive = pd.DataFrame()
        self.reload_current()

    @property
    def df(self) -> pd.DataFrame:
        return self._df_active.copy()

    def active_quantity(self, item_id: int) -> int:
        df = self._df_active
        qtd = 0 if item_id not in df['item_id'].values else df.loc[df['item_id'] == item_id, 'qtd_current'].iloc[0]
        return qtd

    def reload_current(self) -> None:
        columns = ['id', 'game_id', 'item_id', 'steam_id', 'price', 'qtd_start', 'qtd_current', 'created_at', 'updated_at', 'removed_at']
        db_data = QueryDB.get_repo('buy_order').get_current_buy_orders(user_id=self._user_id)
        self._df_active = pd.DataFrame(db_data, columns=columns)
        db_data = QueryDB.get_repo('buy_order').get_inactive_with_created_at_rank(user_id=self._user_id)
        df = pd.DataFrame(db_data, columns=columns + ['created_at_rank'])
        df = df[df['created_at_rank'] <= 2]
        self._df_most_recent_inactive = df.drop(columns='created_at_rank')

    def get_game_ids_with_most_outdated_orders(self, quantity: int) -> list[int]:
        df_aux = self.df.sort_values(by='updated_at')
        df_aux.drop_duplicates('game_id', inplace=True)
        return list(df_aux['game_id'].iloc[0:quantity])

    def get_game_and_item_ids_without_active(self, item_quantity: int) -> dict[int, list]:
        """:return {game_id: [item_id_1, item_id_2]}"""
        actives = self.df
        inactives = self._df_most_recent_inactive.copy()
        actives['has_active'] = True
        inactives = pd.merge(inactives, actives[['item_id', 'has_active']], how='left')
        inactives_without_actives = inactives[inactives['has_active'] != True]
        df = inactives_without_actives.drop(columns='has_active').copy()

        df.sort_values(by='removed_at', inplace=True)
        df.drop_duplicates(subset=['game_id', 'item_id'], keep='last', inplace=True)
        df.reset_index(drop=True, inplace=True)
        rows = df.loc[0:item_quantity-1, ['game_id', 'item_id']].to_dict('records')

        result = {}
        for item in rows:
            if item['game_id'] not in result.keys():
                result[item['game_id']] = []
            result[item['game_id']].append(item['item_id'])
        return result

    def get_recent_history(self, game_id: int) -> dict:
        """:return {
            item_id: [{keys: 'id', 'steam_id', 'active', 'price', 'qtd_start', 'qtd_current', 'created_at', 'removed_at', 'days_active'}]
        }"""
        result = {}

        df = self.df
        df = df[df['game_id'] == game_id].copy()
        df['days_active'] = (datetime.today() - df['created_at']).dt.days
        df = df[['item_id', 'steam_id', 'price', 'qtd_start', 'qtd_current', 'created_at', 'removed_at', 'days_active']].copy()
        for item in df.to_dict('records'):
            item_id = item.pop('item_id')
            item['active'] = True
            result[item_id] = [item]

        df = self._df_most_recent_inactive.copy()
        df = df[df['game_id'] == game_id].copy()
        df['days_active'] = (df['removed_at'] - df['created_at']).dt.days
        df = df[['item_id', 'price', 'qtd_start', 'qtd_current', 'created_at', 'removed_at', 'days_active']].copy()
        for item in df.to_dict('records'):
            item_id = item.pop('item_id')
            if item_id not in list(result.keys()):
                result[item_id] = []
            item['active'] = False
            result[item_id].append(item)

        return result
