import pandas as pd

from data_models.query.SteamGamesRepository import SteamGamesRepository


class SteamGamesNew:

    def __init__(self, game_ids: list = None, with_items: bool = False):
        self._with_items = with_items
        db_data = SteamGamesRepository().get_all_by_ids_new(ids=game_ids, with_items=with_items)
        columns = ['id', 'name', 'market_id', 'has_trading_cards']
        if with_items:
            columns.extend(['item_name', 'item_market_url_name', 'set_number'])
        self._df = pd.DataFrame(db_data, columns=columns)

    def id_name_dict(self) -> dict:
        df = self._df[['id', 'name']].drop_duplicates()
        df.set_index(keys='id', inplace=True)
        return df.to_dict()['name']
