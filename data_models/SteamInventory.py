import pandas as pd
from datetime import datetime

from repositories.SteamInventoryRepository import SteamInventoryRepository
from data_models.PandasDataModel import PandasDataModel
from data_models.PandasUtils import PandasUtils


class SteamInventory(PandasDataModel):

    __columns = ['id', 'user_id', 'game_id', 'name', 'type_id', 'class_id', 'asset_id', 'marketable', 'url_name']
    __columns_description = ['id', 'game_id', 'class_id', 'type_id', 'name', 'url_name']
    __columns_asset = ['id', 'user_id', 'description_id', 'asset_id', 'created_at', 'removed_at', 'marketable']
    __columns_item_type = ['id', 'name']

    def __init__(self, table: str = '', **data):
        cols = self.__get_columns(table)
        class_name = self.__class__.__name__
        super().__init__(class_name, cols, **data)

    @classmethod
    def __get_columns(cls, table: str = '') -> list:
        cols = {
            '': cls.__columns.copy(),
            'descriptions': cls.__columns_description.copy(),
            'assets': cls.__columns_asset.copy(),
            'item_types': cls.__columns_item_type.copy(),
        }.get(table, [])
        return cols

    @classmethod
    def __from_db(cls, table: str, db_data: list[tuple]):
        zipped_data = zip(*db_data)
        dict_data = dict(zip(cls.__get_columns(table), zipped_data))
        return cls(table, **dict_data)

    def save(self, table: str = '', user_id: int = 0) -> None:
        if table == '':
            raise TypeError('Saving inventory requires table name')
        if table == 'descriptions':
            self.__save_descriptions()
        if table == 'assets':
            self.__save_assets(user_id)
        if table == 'item_types':
            zipped_data = PandasUtils.zip_df_columns(self.df, self.__get_columns(table))
            SteamInventoryRepository.insert_item_types(zipped_data)

    def __save_descriptions(self, table: str = 'descriptions') -> None:
        new = self.df.drop_duplicates()
        saved = self.get_all(table).df
        to_save = PandasUtils.df_set_difference(new, saved, ['class_id', 'url_name'])
        if not to_save.empty:
            cols_to_insert = self.__get_columns(table)
            cols_to_insert.remove('id')
            zipped_data = PandasUtils.zip_df_columns(to_save, cols_to_insert)
            SteamInventoryRepository.upsert_descriptions(zipped_data, cols_to_insert)

    def __save_assets(self, user_id: int = 0, table: str = 'assets') -> None:
        if user_id == 0:
            return

        new_inv = self.df
        last_inv = SteamInventory.get_current_inventory_from_db(user_id)
        to_remove = PandasUtils.df_set_difference(last_inv.df, new_inv, 'asset_id')
        to_upsert_without_id = PandasUtils.df_set_difference(new_inv, last_inv.df, ['asset_id', 'marketable'])
        to_upsert = pd.merge(to_upsert_without_id.drop(columns='id'), last_inv.df[['id', 'asset_id']], how='left')

        if not to_remove.empty:
            to_remove['removed_at'] = str(datetime.now())
            zipped_data = PandasUtils.zip_df_columns(to_remove, ['id', 'removed_at'])
            SteamInventoryRepository.update_removed_assets(zipped_data)

        if not to_upsert.empty:
            class_id_to_descript_id = SteamInventory.__class_id_to_description_id_relationship()
            to_upsert = pd.merge(to_upsert, class_id_to_descript_id, how='left')
            to_upsert['created_at'] = str(datetime.now())
            to_upsert['removed_at'] = 'None'

            cols_to_insert = self.__get_columns(table)
            cols_to_insert.remove('id')
            zipped_data = PandasUtils.zip_df_columns(to_upsert, cols_to_insert)
            SteamInventoryRepository.upsert_new_assets(zipped_data, cols_to_insert)

    @staticmethod
    def __last_saved_date(user_id: int) -> str:
        last_saved_date = SteamInventoryRepository.last_inventory_saved_date(user_id)
        if not last_saved_date:
            last_saved_date = '1970-01-01'
        else:
            last_saved_date = str(last_saved_date[0][0])
        return last_saved_date

    @staticmethod
    def __class_id_to_description_id_relationship() -> pd.DataFrame:
        data = SteamInventoryRepository.get_all('descriptions')
        df_relationship = SteamInventory.__from_db('descriptions', data).df
        df_relationship = df_relationship[['id', 'class_id']].copy()
        df_relationship.rename(columns={'id': 'description_id'}, inplace=True)
        return df_relationship

    @staticmethod
    def get_all(table: str = 'assets') -> 'SteamInventory':
        data = SteamInventoryRepository.get_all(table)
        return SteamInventory.__from_db(table, data)

    @staticmethod
    def get_current_inventory_from_db(user_id: int) -> 'SteamInventory':
        data = SteamInventoryRepository.get_current_by_user_id(user_id)
        return SteamInventory.__from_db('assets', data)

    @staticmethod
    def get_current_inventory_size(user_id: int) -> int:
        return SteamInventoryRepository.get_current_size_by_user_id(user_id)

    @staticmethod
    def get_item_types() -> dict:
        data = SteamInventoryRepository.get_all('types')
        return dict(data)

    @staticmethod
    def get_overview_marketable_cards(user_id: int) -> dict:
        data = SteamInventoryRepository.get_overview_marketable_cards(user_id)
        return dict(data)

    @staticmethod
    def get_booster_pack_assets_id(user_id: int, game_name: str) -> list:
        data = SteamInventoryRepository.get_booster_pack_assets_id(user_id, game_name)
        assets_id_list = [row[0] for row in data]
        return assets_id_list

    @staticmethod
    def get_marketable_cards_asset_ids(user_id: int, game_name: str) -> dict:
        data = SteamInventoryRepository.get_marketable_cards_asset_ids(user_id, game_name)
        data_formatted = {f'{row[0]}-{row[1]}': [] for row in data}
        for card_index in data_formatted.keys():
            data_formatted[card_index] = [
                row[2] for row in data if card_index == f'{row[0]}-{row[1]}'
            ]
        return data_formatted
