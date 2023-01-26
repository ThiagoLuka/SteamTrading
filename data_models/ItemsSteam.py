from data_models.PandasDataModel import PandasDataModelNew
from data_models.PandasUtils import PandasUtils
from repositories.ItemsSteamRepository import ItemsSteamRepository


class ItemsSteam(
    PandasDataModelNew,
    tables={
        'items_steam',
        'item_steam_types'
    },
    columns={
        'default': ('id', 'game_id', 'type_name', 'name', 'market_url_name', 'market_item_name_id'),
        'items_steam': ('id', 'game_id', 'item_steam_type_id', 'name', 'market_url_name', 'market_item_name_id'),
        'item_steam_types': ('id', 'name'),
    },
    repository=ItemsSteamRepository
):

    def __init__(self, table: str = 'default', **data):
        super().__init__(table, **data)

    def save(self):
        if self.columns == ItemsSteam._get_class_columns('default'):
            self.__save_default()
        elif self.columns == ItemsSteam._get_class_columns('items_steam'):
            self.__save_items_steam()
        elif self.columns == ItemsSteam._get_class_columns('item_steam_types'):
            self.__save_types()

    def __save_default(self):
        pass

    def __save_items_steam(self) -> None:
        saved = ItemsSteam.get_all()
        new_and_update = PandasUtils.df_set_difference(self.df, saved.df, ['game_id', 'market_url_name'])
        if new_and_update.empty:
            return
        cols_to_insert = self._get_class_columns('items_steam')
        cols_to_insert.remove('id')
        zipped_data = PandasUtils.zip_df_columns(new_and_update, cols_to_insert)
        ItemsSteamRepository.upsert_multiple_items(zipped_data, cols_to_insert)

    def __save_types(self):
        saved_types: list[tuple] = ItemsSteamRepository.get_all_types()
        for row in self:
            values = tuple(row.values())
            if values in saved_types:
                continue
            type_id = values[0]
            type_name = values[1]
            ItemsSteamRepository.upsert_item_type(type_id, type_name)

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
