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

    def get_game_info(self) -> list[dict]:
        game_info = []
        for description in self.__inventory['descriptions']:
            game_info.append({
                'name': self._get_game_name(description),
                'market_id': self._get_game_market_id(description),
            })
        return game_info

    def get_steam_item_info(self) -> list[dict]:
        steam_item_info = []
        for description in self.__inventory['descriptions']:
            steam_item_type_id, steam_item_type_name = self._get_item_type_id_and_name(description)
            steam_item_info.append({
                'game_market_id': self._get_game_market_id(description),
                'market_url_name': self._get_item_market_url_name(description),
                'name': self._get_item_name(description),
                'steam_item_type_id': steam_item_type_id,
                'steam_item_type_name': steam_item_type_name,
                'class_id': self._get_class_id(description),
            })
        return steam_item_info

    def get_asset_info(self) -> list[dict]:
        steam_asset_info = []
        for asset in self.__inventory['assets']:
            steam_asset_info.append({
                'class_id': self._get_class_id(asset),
                'asset_id': self._get_asset_id(asset),
                'marketable': self._get_marketable(
                    descriptions=self.__inventory['descriptions'],
                    instance_id=self._get_instance_id(asset),
                    class_id=self._get_class_id(asset),
                )
            })
        return steam_asset_info

    @staticmethod
    def _get_game_name(description: dict) -> str:
        for tag in description['tags']:
            if tag['category'] == 'Game':
                return tag['localized_tag_name']

    @staticmethod
    def _get_game_market_id(description: dict) -> str:
        return str(description['market_fee_app'])

    @staticmethod
    def _get_item_market_url_name(description: dict) -> str:
        market_hash_name = description['market_hash_name']
        hash_splitted = market_hash_name.split('-')
        hash_splitted.pop(0)
        url_name_raw = '-'.join(hash_splitted)
        url_name = requests.utils.quote(url_name_raw)
        return url_name

    @staticmethod
    def _get_item_name(description: dict) -> str:
        return description['name']

    @staticmethod
    def _get_class_id(item: dict) -> str:
        return item['classid']

    @staticmethod
    def _get_item_type_id_and_name(description: dict) -> tuple[int, str]:
        for tag in description['tags']:
            if tag['category'] == 'item_class':
                return int(tag['internal_name'].replace('item_class_', '')), tag['localized_tag_name']

    @staticmethod
    def _get_asset_id(asset: dict) -> str:
        return asset['assetid']

    @staticmethod
    def _get_instance_id(asset: dict) -> str:
        return asset['instanceid']

    @staticmethod
    def _get_marketable(descriptions: list, instance_id: str, class_id: str) -> int:
        for d in descriptions:
            if d['instanceid'] == instance_id and d['classid'] == class_id:
                return d['marketable']

    def get_game_booster_pack_asset_ids(self, game_market_id: str) -> list[str]:
        desc = self.__inventory['descriptions']
        assets = self.__inventory['assets']
        game_desc = [d for d in desc if str(d['market_fee_app']) == game_market_id]
        bp_class_id: set[str] = {d['classid'] for d in game_desc if d['type'] == 'Booster Pack'}
        bp_asset_ids = [asset['assetid'] for asset in assets if asset['classid'] in bp_class_id]
        return bp_asset_ids

    @staticmethod
    def get_foil_from_item_description(description: dict) -> int:
        tags = description['tags']
        border_tag = [tag for tag in tags if tag['category'] == 'cardborder'][0]
        raw_border = border_tag['internal_name']
        border_foil = int(raw_border.replace('cardborder_', ''))
        return border_foil

