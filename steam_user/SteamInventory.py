import pandas as pd

from data_models import QueryDB


class SteamInventory:

    def __init__(self, user_id: int):
        self._user_id = user_id
        self._df = pd.DataFrame()
        self.reload_current()

    @property
    def df(self) -> pd.DataFrame:
        return self._df.copy()

    def reload_current(self) -> None:
        columns = ['id', 'game_id', 'item_steam_id', 'steam_asset_id', 'marketable', 'created_at']
        db_data = QueryDB.get_repo('inventory').get_current_inventory(user_id=self._user_id)
        self._df = pd.DataFrame(db_data, columns=columns)

    def size(self, marketable: bool = False) -> int:
        if marketable:
            return len(self.df[self.df['marketable']])
        return len(self.df)

    def get_all_game_ids(self) -> list[int]:
        return list(self.df['game_id'].drop_duplicates())

    def get_asset_ids(self, item_id: int) -> list:
        df = self.df[self.df['item_steam_id'] == item_id]
        return list(df['steam_asset_id'])

    def get_game_ids_with_marketable_items(self, game_quantity: int, games_allowed: list) -> list[int]:
        df = self.df[self.df['marketable'] == True]
        df.sort_values(by='created_at', inplace=True)
        df.drop_duplicates(subset='game_id', inplace=True)
        df = df[df['game_id'].isin(games_allowed)]
        df.reset_index(drop=True, inplace=True)
        return list(df.loc[0:game_quantity-1, 'game_id'])

    def summary_qtd(self, by: str = 'game', marketable: bool = False) -> dict:
        """:return {by: qtd}"""
        df = self.df
        if marketable:
            df = df[df['marketable']]
        summary_qtd = {
            'game': dict(df.value_counts(subset='game_id')),
            'item': dict(df.value_counts(subset='item_steam_id')),
        }.get(by, {})
        return summary_qtd

    def get_steam_asset_ids_by_item_ids(self, item_ids: list[int]) -> dict[tuple[int, int], list]:
        """:return {(game_id, item_id): [asset_id_0, asset_id_1]}"""
        df_filtered = self.df[self.df['item_steam_id'].isin(item_ids)]
        df_grouped = df_filtered.groupby(
            by=['game_id', 'item_steam_id']
        ).agg({'steam_asset_id': lambda x: x.tolist()})
        return df_grouped.to_dict()['steam_asset_id']
