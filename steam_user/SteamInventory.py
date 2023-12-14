import pandas as pd

from data_models.query.SteamInventoryRepository import SteamInventoryRepository


class SteamInventory:

    def __init__(self, user_id: int):
        self._user_id = user_id
        self._df = pd.DataFrame()
        self.reload_current()

    def reload_current(self) -> None:
        columns = ['id', 'game_id', 'item_steam_id', 'steam_asset_id', 'marketable', 'created_at']
        db_data = SteamInventoryRepository.get_current_inventory(user_id=self._user_id)
        self._df = pd.DataFrame(db_data, columns=columns)

    def size(self, marketable: bool = False) -> int:
        df = self._df
        if marketable:
            return len(df[df['marketable']])
        return len(df)


    def summary_qtd(self, by: str = 'game', marketable: bool = False) -> dict:
        """return {by: qtd}"""
        df = self._df
        if marketable:
            df = df[df['marketable']]
        summary_qtd = {
            'game': dict(df.value_counts(subset='game_id'))
        }.get(by, {})
        return summary_qtd
