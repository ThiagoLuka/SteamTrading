import pandas as pd

from data_models.PandasDataModel import PandasDataModel
from repositories.SteamGamesRepository import SteamGamesRepository


class SteamGames(
    PandasDataModel,
    tables={
        'games',
    },
    columns={
        'default': ('id', 'name', 'market_id', 'has_trading_cards'),
        'games': ('id', 'name', 'market_id', 'has_trading_cards'),
    },
    repository=SteamGamesRepository
):

    def __init__(self, table: str = 'default', **data):
        super().__init__(table, **data)

    # I should implement multiple games in a single SteamGames instance later
    # it should look like list(game.df.loc[:, 'id']) or something like that
    @property
    def id(self):
        return self.df.loc[0, 'id']

    @property
    def name(self):
        return self.df.loc[0, 'name']

    @property
    def market_id(self):
        return self.df.loc[0, 'market_id']

    @staticmethod
    def get_all() -> 'SteamGames':
        cols = SteamGames._get_class_columns()
        data = SteamGamesRepository.get_all(cols)
        return SteamGames._from_db('default', data)

    @staticmethod
    def get_all_by_id(game_ids: list) -> 'SteamGames':
        cols = SteamGames._get_class_columns()
        game_ids = [str(game_id) for game_id in game_ids]
        data = SteamGamesRepository.get_all_by_id(game_ids, cols)
        return SteamGames._from_db('default', data)

    @staticmethod
    def get_all_with_trading_cards_not_registered() -> 'SteamGames':
        table = 'default'
        data = SteamGamesRepository.get_all_with_trading_cards_not_registered()
        return SteamGames._from_db(table, data)

    def get_market_ids(self) -> list:
        if self.empty:
            all_games = SteamGames.get_all()
            return list(all_games.df['market_id'])
        return list(self.df['market_id'])
