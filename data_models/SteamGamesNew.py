import pandas as pd

from data_models.query.SteamGamesRepository import SteamGamesRepository


class SteamGamesNew:

    def __init__(self, game_ids: list = None, with_items: bool = False):
        self._df = pd.DataFrame()
        self._df_items = pd.DataFrame()
        self._with_items: bool = with_items
        self._load_data(game_ids=game_ids, with_items=with_items)

    @property
    def df(self) -> pd.DataFrame:
        return self._df.copy()

    def name(self, game_id: int) -> str:
        return self.df.loc[self.df['id'] == game_id, 'name'].iloc[0]

    def market_id(self, game_id: int) -> str:
        return self.df.loc[self.df['id'] == game_id, 'market_id'].iloc[0]

    def id_name_dict(self) -> dict:
        df = self.df[['id', 'name']].drop_duplicates()
        df.set_index(keys='id', inplace=True)
        return df.to_dict()['name']

    def get_booster_pack_item_ids(self) -> list[int]:
        if not self._with_items:
            self._load_data(game_ids=list(self.df['id']), with_items=True)
        df_filtered = self._df_items[self._df_items['steam_item_type'] == 'Booster Pack']
        item_ids = list(df_filtered['item_id'].drop_duplicates())
        return item_ids

    def _load_data(self, game_ids: list, with_items: bool) -> None:
        self._with_items = with_items
        columns = ['id', 'name', 'market_id', 'has_trading_cards']
        item_cols = ['item_id', 'item_name', 'steam_item_type', 'item_market_url_name', 'set_number']
        db_data = SteamGamesRepository().get_all_by_ids_new(ids=game_ids, with_items=with_items)
        if with_items:
            self._df_items = pd.DataFrame(db_data, columns=columns + item_cols)
            self._df = self._df_items[columns].drop_duplicates().copy()
            return
        self._df_items = pd.DataFrame()
        self._df = pd.DataFrame(db_data, columns=columns)
