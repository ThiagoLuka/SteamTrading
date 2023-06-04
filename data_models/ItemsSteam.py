from typing import Optional

import pandas as pd

from data_models.PandasDataModel import PandasDataModel
from data_models.PandasUtils import PandasUtils
from repositories.ItemsSteamRepository import ItemsSteamRepository


class ItemsSteam(
    PandasDataModel,
    tables={
        'items_steam',
        'item_steam_types',
        'item_steam_descriptions',
    },
    columns={
        'default': ('id', 'game_id', 'type_name', 'name', 'market_url_name'),
        'items_steam': ('id', 'game_id', 'item_steam_type_id', 'name', 'market_url_name'),
        'item_steam_types': ('id', 'name'),
        'item_steam_descriptions': ('item_steam_id', 'class_id')
    },
    repository=ItemsSteamRepository
):

    def __init__(self, table: str = 'default', **data):
        super().__init__(table, **data)

    def __iter__(self):
        for index, row in self.df.iterrows():
            yield ItemsSteam('items_steam', **dict(row))

    def save(self):
        if self.columns == ItemsSteam._get_class_columns('default'):
            self.__save_default()
        elif self.columns == ItemsSteam._get_class_columns('items_steam'):
            self.__save_items_steam()
        elif self.columns == ItemsSteam._get_class_columns('item_steam_types'):
            self.__save_types()
        elif self.columns == ItemsSteam._get_class_columns('item_steam_descriptions'):
            self.__save_descriptions()

    def __save_default(self):
        pass

    def __save_items_steam(self) -> None:
        saved = ItemsSteam.get_all()
        new_and_update = PandasUtils.df_set_difference(self.df, saved.df, ['game_id', 'market_url_name'])
        if new_and_update.empty:
            return
        new_and_update.drop_duplicates(inplace=True)
        cols_to_insert = self._get_class_columns('items_steam')
        cols_to_insert.remove('id')
        zipped_data = PandasUtils.zip_df_columns(new_and_update, cols_to_insert)
        ItemsSteamRepository.upsert_multiple_items(zipped_data, cols_to_insert)

    def __save_types(self) -> None:
        saved_types: list[tuple] = ItemsSteamRepository.get_all_types()
        # it's always just a couple types, it's okay to iterate over it
        # this method has to be refactored soon
        for index, row in self.df.iterrows():
            values = tuple(dict(row).values())
            values = int(values[0]), values[1]
            if values in saved_types:
                continue
            type_id = values[0]
            type_name = values[1]
            ItemsSteamRepository.upsert_item_type(type_id, type_name)

    def __save_descriptions(self) -> None:
        saved = ItemsSteam.get_all_class_ids()
        to_save = self.df[~self.df['class_id'].isin(saved)]
        if to_save.empty:
            return
        to_save.drop_duplicates(inplace=True)
        cols_to_insert = self._get_class_columns('item_steam_descriptions')
        zipped_data = PandasUtils.zip_df_columns(to_save, cols_to_insert)
        ItemsSteamRepository.insert_item_description(zipped_data, cols_to_insert)

    @staticmethod
    def get_all(columns: list = None, with_type_names: bool = False) -> 'ItemsSteam':
        table = 'items_steam'
        if not columns:
            columns = ItemsSteam._get_class_columns(table)
        if with_type_names:
            table = 'default'
            columns = ItemsSteam._get_class_columns(table)
            columns[columns.index('id')] = 'items_steam.id'
            columns[columns.index('type_name')] = 'item_steam_types.name'
            columns[columns.index('name')] = 'items_steam.name'
        data = ItemsSteamRepository.get_all(columns, with_type_names)
        return ItemsSteam._from_db(table, data)

    @staticmethod
    def get_all_types() -> dict:
        return dict(ItemsSteamRepository.get_all_types())

    @staticmethod
    def get_all_descriptions():
        data = ItemsSteamRepository.get_all_descriptions()
        return ItemsSteam._from_db('item_steam_descriptions', data)

    @staticmethod
    def get_all_class_ids() -> list[str]:
        class_ids = [class_id[0] for class_id in ItemsSteamRepository.get_all_class_ids()]
        return class_ids

    @staticmethod
    def get_item_type_id(item_type_name: str) -> int:
        item_type_id: list = ItemsSteamRepository.get_item_type_id(item_type_name)
        if item_type_id:
            item_type_id: int = item_type_id[0][0]
            return item_type_id
        # if type does not exist in db, it's given a ridiculous big id and saved.
        # this id should be replaced as soon as it's found during an inventory scrap
        ridiculous_big_id: int = {
            'Booster Pack': 10000,
            'Trading Card': 10001,
        }.get(item_type_name, None)
        if not ridiculous_big_id:
            raise Exception('Unknown item type requested.')
        ItemsSteam('item_steam_types', id=ridiculous_big_id, name=item_type_name).save()
        return ridiculous_big_id

    @staticmethod
    def get_ids_by_market_url_names(url_names: list[str]) -> list[int]:
        url_name_to_id = dict(ItemsSteamRepository.get_ids_by_market_url_names(url_names))
        ids = [url_name_to_id[url_name] for url_name in url_names]
        return ids

    @staticmethod
    def get_ids_by_game_id_and_market_url_name(game_ids: list, market_url_names: list) -> list:
        df = pd.DataFrame(data={'game_id': game_ids, 'market_url_name': market_url_names})
        df_to_query = df.drop_duplicates()
        zipped_tuples_to_search_for = PandasUtils.zip_df_columns(df_to_query, ['game_id', 'market_url_name'])
        columns = ItemsSteam._get_class_columns('items_steam')
        db_data = ItemsSteamRepository.get_by_game_id_and_market_url_names(columns, zipped_tuples_to_search_for)
        items = ItemsSteam._from_db('items_steam', db_data).df
        df_result = pd.merge(df, items[['id', 'game_id', 'market_url_name']])
        ids = df_result['id'].to_list()
        return ids

    @staticmethod
    def get_booster_pack_and_cards_market_url(game_id: str, booster_pack_last: bool = False) -> 'ItemsSteam':
        booster_pack = ItemsSteam._from_db(
            'items_steam',
            ItemsSteamRepository.get_booster_pack(
                ['items_steam.id as id', 'items_steam.game_id', 'item_steam_type_id', 'name', 'market_url_name'],
                game_id
            )
        )
        cards = ItemsSteam._from_db(
            'items_steam',
            ItemsSteamRepository.get_game_cards(
                ['items_steam.id as id', 'items_steam.game_id', 'item_steam_type_id', 'name', 'market_url_name'],
                game_id
            )
        )
        if booster_pack_last:
            items = cards + booster_pack
        else:
            items = booster_pack + cards
        return items

    @staticmethod
    def get_game_items(game_id: str, item_types: Optional[list] = None):
        cols = ItemsSteam._get_class_columns()
        cols[cols.index('id')] = 'items_steam.id'
        cols[cols.index('type_name')] = 'item_steam_types.name'
        cols[cols.index('name')] = 'items_steam.name as name'
        data = ItemsSteamRepository.get_all_by_game(columns=cols, game_id=game_id, item_types=item_types)
        return ItemsSteam._from_db('default', data)
