import requests

from data_models.SteamInventory import SteamInventory
from data_models.SteamGames import SteamGames


class InventoryPageCleaner:

    def __init__(self, inventory: dict):
        self.__inventory: dict = inventory
        if 'more_items' not in self.__inventory.keys():
            self.__inventory['more_items'] = 0
        if 'last_assetid' not in self.__inventory.keys():
            self.__inventory['last_assetid'] = self.__inventory['assets'][-1]['assetid']

    def __len__(self):
        return int(self.__inventory['total_inventory_count'])

    def __add__(self, other: dict):
        self.__inventory['descriptions'].extend(other['descriptions'])
        self.__inventory['assets'].extend(other['assets'])
        if 'more_items' not in other.keys():
            self.__inventory['more_items'] = 0
        self.__inventory['last_assetid'] = self.__inventory['assets'][-1]['assetid']
        return self

    @property
    def more_items(self) -> bool:
        return bool(self.__inventory['more_items'])

    @property
    def last_assetid(self) -> str:
        return self.__inventory['last_assetid']

    def save_new_games(self) -> None:
        inventory_game_market_ids = {d['market_fee_app'] for d in self.__inventory['descriptions']}
        saved_game_market_ids = SteamGames().get_market_ids()

        new_market_ids = []
        for game_market_id in inventory_game_market_ids:
            if str(game_market_id) not in saved_game_market_ids:
                new_market_ids.append(game_market_id)

        for d in self.__inventory['descriptions']:
            if d['market_fee_app'] in new_market_ids:
                tags = d['tags']
                game_name = next(tag['localized_tag_name'] for tag in tags if tag['category'] == 'Game')
                SteamGames(
                    name=game_name, market_id=d['market_fee_app']
                ).save()

    def to_descriptions(self) -> SteamInventory:
        descripts_raw = self.__inventory['descriptions']
        game_ids = self.__get_game_ids(descripts_raw)
        class_ids = [d['classid'] for d in descripts_raw]
        type_ids = self.__get_item_types(descripts_raw)
        names = [d['name'] for d in descripts_raw]
        url_names = self.__get_url_names(descripts_raw)
        descripts = SteamInventory(
            game_id=game_ids, name=names, type_id=type_ids, class_id=class_ids, url_name=url_names,
        )
        return descripts

    def to_assets(self, user_id: int) -> SteamInventory:
        assets_raw = self.__inventory['assets']
        descripts_raw = self.__inventory['descriptions']
        user_ids = [user_id] * len(assets_raw)
        class_ids = [a['classid'] for a in assets_raw]
        asset_ids = [a['assetid'] for a in assets_raw]
        marketables = self.__get_asset_marketable(assets_raw, descripts_raw)
        assets = SteamInventory(user_id=user_ids, class_id=class_ids, asset_id=asset_ids, marketable=marketables)
        return assets

    @staticmethod
    def __get_game_ids(descripts_raw: list[dict]) -> list:
        # market_fee_app is not as reliable as market_hash_name, not sure why
        # game_market_ids = [d['market_fee_app'] for d in descripts_raw]
        game_market_ids = [int(d['market_hash_name'].split('-')[0]) for d in descripts_raw]
        game_ids = SteamGames.get_ids_list_by_market_ids_list(game_market_ids)
        return game_ids

    def __get_item_types(self, descripts_raw: list[dict]) -> list[str]:
        type_ids = []
        type_names: dict = {}
        for d in descripts_raw:
            tags = d['tags']
            for tag in tags:
                if tag['category'] == 'item_class':
                    type_id = tag['internal_name'].replace('item_class_', '')
                    type_ids.append(type_id)
                    type_names.update({type_id: tag['localized_tag_name']})

        self.__save_new_item_types(type_names)

        return type_ids

    @staticmethod
    def __save_new_item_types(type_names: dict) -> None:
        saved_type_ids = SteamInventory.get_item_types()
        for type_id in type_names.keys():
            if int(type_id) not in saved_type_ids:
                SteamInventory(
                    id=type_id, name=type_names[type_id]
                ).save('item_types')

    @staticmethod
    def __get_url_names(descripts_raw: list[dict]) -> list[str]:
        # just like market_fee_app, market_name is not as reliable as market_hash_name
        # url_names = [requests.utils.quote(d['market_name']) for d in descripts_raw]
        def get_url_name_from_market_hash(market_hash_name):
            hash_splitted = market_hash_name.split('-')
            hash_splitted.pop(0)
            url_name_raw = '-'.join(hash_splitted)
            url_name = requests.utils.quote(url_name_raw)
            return url_name
        url_names = [get_url_name_from_market_hash(d['market_hash_name']) for d in descripts_raw]
        return url_names

    @staticmethod
    def __get_asset_marketable(assets_raw: list[dict], descripts_raw: list[dict]) -> list:
        instance_id_marketable: dict = {d['instanceid']: d['marketable'] for d in descripts_raw}
        asset_instances = [a['instanceid'] for a in assets_raw]
        marketables = [instance_id_marketable[instance] for instance in asset_instances]
        return marketables
