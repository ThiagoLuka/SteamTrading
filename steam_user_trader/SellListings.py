import pandas as pd

from data_models import QueryDB


class SellListings:

    def __init__(self, user_id: int):
        self._user_id = user_id
        self._df = pd.DataFrame()
        self.reload_current()

    @property
    def df(self) -> pd.DataFrame:
        return self._df.copy()

    def reload_current(self) -> None:
        columns = ['id', 'game_id', 'item_id', 'steam_id', 'price_buyer', 'price_to_receive', 'steam_created_at', 'created_at', 'removed_at']
        db_data = QueryDB.get_repo('sell_listing').get_current_sell_listings(user_id=self._user_id)
        self._df = pd.DataFrame(db_data, columns=columns)
