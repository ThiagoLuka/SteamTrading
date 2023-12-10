from data_models.PandasDataModel import PandasDataModel
from data_models.query.ItemsSteamRepository import ItemsSteamRepository


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
    def get_booster_pack_and_cards_market_url(
            game_id: str, booster_pack_last: bool = False, include_foil: bool = False) -> 'ItemsSteam':
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
        if include_foil:
            foil = ItemsSteam._from_db(
                'items_steam',
                ItemsSteamRepository.get_foil_game_cards(
                    ['items_steam.id as id', 'items_steam.game_id', 'item_steam_type_id', 'name', 'market_url_name'],
                    game_id
                )
            )
            items += foil
        return items
