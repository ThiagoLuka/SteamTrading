import pandas as pd

from repositories.SteamGamesRepository import SteamGamesRepository
from data_models.PandasDataModel import PandasDataModel
from data_models.PandasUtils import PandasUtils


class SteamGames(PandasDataModel):

    __columns = ['id', 'name', 'market_id']

    def __init__(self, **data):
        cols = self.__get_columns()
        class_name = self.__class__.__name__
        super().__init__(class_name, cols, **data)

    @classmethod
    def __get_columns(cls) -> list:
        return cls.__columns.copy()

    @classmethod
    def __from_db(cls, db_data: list[tuple]):
        zipped_data = zip(*db_data)
        dict_data = dict(zip(cls.__get_columns(), zipped_data))
        return cls(**dict_data)

    def save(self) -> None:
        saved = SteamGames.get_all()
        new_and_update = PandasUtils.df_set_difference(self.df, saved.df, 'name')
        if not new_and_update.empty:
            cols_to_insert = self.__get_columns()
            cols_to_insert.remove('id')
            zipped_data = PandasUtils.zip_df_columns(new_and_update, cols_to_insert)
            SteamGamesRepository.upsert_multiple_games(zipped_data, cols_to_insert)

    @staticmethod
    def get_all() -> 'SteamGames':
        cols = SteamGames.__get_columns()
        data = SteamGamesRepository.get_all(cols)
        return SteamGames.__from_db(data)

    @staticmethod
    def get_all_without_trading_cards() -> 'SteamGames':
        data = SteamGamesRepository.get_all_without_trading_cards()
        return SteamGames.__from_db(data)

    @staticmethod
    def get_id_by_market_id(market_id: str) -> str:
        cols = SteamGames.__get_columns()
        result = SteamGamesRepository.get_by_market_id(market_id, cols)
        return result[0][0]

    @staticmethod
    def get_ids_list_by_market_ids_list(market_ids: list) -> list:
        market_ids_series = SteamGames(market_id=market_ids).df.drop(columns=['id', 'name'])
        all_games_df = SteamGames.get_all().df.copy()
        all_games_df['market_id'] = all_games_df['market_id'].astype(int)
        new_complete_df = pd.merge(market_ids_series, all_games_df, how='left')
        return list(new_complete_df['id'])

    def get_market_ids(self) -> list:
        if self.empty:
            all_games = SteamGames.get_all()
            return list(all_games.df['market_id'])
        return list(self.df['market_id'])
