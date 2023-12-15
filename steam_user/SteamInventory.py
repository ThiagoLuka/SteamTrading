import pandas as pd

from data_models.query.SteamInventoryRepository import SteamInventoryRepository


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
        db_data = SteamInventoryRepository.get_current_inventory(user_id=self._user_id)
        self._df = pd.DataFrame(db_data, columns=columns)

    def size(self, marketable: bool = False) -> int:
        if marketable:
            return len(self.df[self.df['marketable']])
        return len(self.df)

    def get_all_game_ids(self) -> list[int]:
        return list(self.df['game_id'].drop_duplicates())

    def summary_qtd(self, by: str = 'game', marketable: bool = False) -> dict:
        """:return {by: qtd}"""
        df = self.df
        if marketable:
            df = df[df['marketable']]
        summary_qtd = {
            'game': dict(df.value_counts(subset='game_id'))
        }.get(by, {})
        return summary_qtd

    def get_steam_asset_ids_by_item_ids(self, item_ids: list[int]) -> dict[tuple[int, int], list]:
        """:return {(game_id, item_id): [asset_id_0, asset_id_1]}"""
        df_filtered = self.df[self.df['item_steam_id'].isin(item_ids)]
        df_grouped = df_filtered.groupby(
            by=['game_id', 'item_steam_id']
        ).agg({'steam_asset_id': lambda x: x.tolist()})
        return df_grouped.to_dict()['steam_asset_id']
