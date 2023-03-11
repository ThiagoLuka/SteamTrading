import requests


class InventoryPageCleaner:

    def __init__(self):
        self.__inventory: dict = {
            'assets': [],
            'descriptions': [],
            'more_items': True,
            'last_assetid': '',
            'total_inventory_count': 0,
        }

    def __len__(self):
        return len(self.__inventory['assets'])

    def __add__(self, other: dict):
        self.__inventory['assets'].extend(other['assets'])
        self.__inventory['descriptions'].extend(other['descriptions'])
        if 'more_items' not in other.keys():
            self.__inventory['more_items'] = False
        self.__inventory['last_assetid'] = self.__inventory['assets'][-1]['assetid']
        self.__inventory['total_inventory_count'] = other['total_inventory_count']
        return self

    @property
    def empty(self) -> bool:
        return not bool(len(self))

    @property
    def full_size(self) -> int:
        return self.__inventory['total_inventory_count']

    @property
    def more_items(self) -> bool:
        return self.__inventory['more_items']

    @property
    def last_assetid(self) -> str:
        return self.__inventory['last_assetid']

    def get_games_with_market_id(self) -> set[tuple[str, str]]:
        def get_game_name_in_description(description: dict) -> str:
            for tag in description['tags']:
                if tag['category'] == 'Game':
                    return tag['localized_tag_name']
        return {
            (
                get_game_name_in_description(description),
                str(description['market_fee_app']),
            )
            for description
            in self.__inventory['descriptions']
        }

    def get_game_market_ids_for_descripts(self) -> list[int]:
        # return [d['market_fee_app'] for d in descripts_raw]
        # market_fee_app was my first choice to get market_ids,
        # but it's not as reliable as market_hash_name, not sure why
        return [int(d['market_hash_name'].split('-')[0]) for d in self.__inventory['descriptions']]

    def get_class_ids(self, item_type: str) -> list[str]:
        return [item['classid'] for item in self.__inventory[item_type]]

    def get_item_types_with_item_names(self) -> list[tuple[str, str]]:
        def get_item_type_id_and_name_from_tag(description: dict) -> tuple:
            for tag in description['tags']:
                if tag['category'] == 'item_class':
                    return tag['internal_name'].replace('item_class_', ''), tag['localized_tag_name']
        return [
            get_item_type_id_and_name_from_tag(description)
            for description
            in self.__inventory['descriptions']
        ]

    def get_descript_names(self) -> list[str]:
        return [d['name'] for d in self.__inventory['descriptions']]

    def get_item_url_names(self) -> list[str]:
        # just like market_fee_app, market_name is not as reliable as market_hash_name
        # url_names = [requests.utils.quote(d['market_name']) for d in descripts_raw]
        def get_url_name_from_market_hash(market_hash_name):
            hash_splitted = market_hash_name.split('-')
            hash_splitted.pop(0)
            url_name_raw = '-'.join(hash_splitted)
            url_name = requests.utils.quote(url_name_raw)
            return url_name
        return [get_url_name_from_market_hash(d['market_hash_name']) for d in self.__inventory['descriptions']]

    def get_asset_ids(self) -> list[str]:
        return [a['assetid'] for a in self.__inventory['assets']]

    def get_asset_marketable_info(self) -> list[int]:
        instance_ids_to_marketable: dict = {d['instanceid']: d['marketable'] for d in self.__inventory['descriptions']}
        asset_instances = [a['instanceid'] for a in self.__inventory['assets']]
        marketables = [instance_ids_to_marketable[instance] for instance in asset_instances]
        return marketables
