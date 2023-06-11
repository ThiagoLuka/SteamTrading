import pandas as pd
from datetime import datetime

from repositories.SteamInventoryRepository import SteamInventoryRepository
from data_models.PandasDataModel import PandasDataModel
from data_models.PandasUtils import PandasUtils
from data_models.ItemsSteam import ItemsSteam


class SteamInventory(
    PandasDataModel,
    tables={
        'item_steam_assets'
    },
    columns={
        'default': ('id', 'item_steam_id', 'user_id', 'asset_id', 'marketable', 'created_at', 'removed_at'),
        'cleaning': ('class_id', 'asset_id', 'marketable')
    },
    repository=SteamInventoryRepository
):

    def __init__(self, table: str = 'default', **data):
        super().__init__(table, **data)

    def save(self, user_id: int = 0):
        if user_id == 0:
            return

        new_inv = self.df
        new_inv = self.__add_item_steam_id(new_inv)

        last_inv = SteamInventory.get_current_inventory_from_db(user_id).df
        to_remove = PandasUtils.df_set_difference(last_inv, new_inv, 'asset_id').copy()
        to_upsert_without_id = PandasUtils.df_set_difference(new_inv, last_inv, ['asset_id', 'marketable'])
        to_upsert = pd.merge(to_upsert_without_id, last_inv[['id', 'asset_id']], how='left')

        if not to_remove.empty:
            to_remove['removed_at'] = str(datetime.now())
            zipped_data = PandasUtils.zip_df_columns(to_remove, ['id', 'removed_at'])
            SteamInventoryRepository.update_removed_assets(zipped_data)

        if not to_upsert.empty:
            to_upsert['user_id'] = user_id
            to_upsert['created_at'] = str(datetime.now())
            to_upsert['removed_at'] = 'None'

            cols_to_insert = self._get_class_columns('default')
            cols_to_insert.remove('id')
            zipped_data = PandasUtils.zip_df_columns(to_upsert, cols_to_insert)
            SteamInventoryRepository.upsert_new_assets(zipped_data, cols_to_insert)

    @staticmethod
    def __add_item_steam_id(new_inv: pd.DataFrame) -> pd.DataFrame:
        descriptions = ItemsSteam.get_all_descriptions().df
        new_inv = pd.merge(new_inv, descriptions)
        return new_inv

    @staticmethod
    def get_current_inventory_from_db(user_id: int):
        cols = SteamInventory._get_class_columns('default')
        data = SteamInventoryRepository.get_current_by_user_id(user_id, cols)
        return SteamInventory._from_db('default', data)

    @staticmethod
    def get_current_inventory_size(user_id: int) -> int:
        return SteamInventoryRepository.get_current_size_by_user_id(user_id)

    @staticmethod
    def get_overview_marketable_cards(user_id: int) -> dict:
        data = SteamInventoryRepository.get_overview_marketable_cards(user_id)
        return dict(data)

    @staticmethod
    def get_game_ids_with_cards_to_be_sold(n_of_games: int, user_id: int) -> list:
        game_ids_and_date = SteamInventoryRepository.get_game_ids_with_oldest_marketable_cards(n_of_games, user_id)
        game_ids = [game_id for game_id, timestamp in game_ids_and_date]
        return game_ids

    @staticmethod
    def get_booster_pack_assets_id(user_id: int, game_name: str) -> list:
        data = SteamInventoryRepository.get_booster_pack_assets_id(user_id, game_name)
        assets_id_list = [row[0] for row in data]
        return assets_id_list

    @staticmethod
    def get_marketable_cards_asset_ids(user_id: int, game_id: int):
        data = SteamInventoryRepository.get_marketable_cards_asset_ids(user_id, game_id)
        cards_asset_ids: dict = {}
        for row in data:
            card_name, asset_id = row[0], row[1]
            if card_name not in cards_asset_ids.keys():
                cards_asset_ids.update({card_name: []})
            cards_asset_ids[card_name].append(asset_id)
        return cards_asset_ids
