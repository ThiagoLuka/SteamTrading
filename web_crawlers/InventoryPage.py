import requests

from user_interfaces.GenericUI import GenericUI
from web_crawlers.SteamWebPage import SteamWebPage
from data_models.SteamInventory import SteamInventory
from data_models.SteamGames import SteamGames
from data_models.SteamTradingCards import SteamTradingCards


class InventoryPage(SteamWebPage, name='get_inventory'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'user_id', 'steam_id',

    @staticmethod
    def required_cookies() -> tuple:
        return 'steamMachineAuth', 'steamLoginSecure',

    def interact(self, cookies: dict, **kwargs) -> SteamInventory:
        user_id: int = kwargs['user_id']
        steam_id: str = kwargs['steam_id']

        # Extract
        descripts_raw, assets_raw = self.__download_raw_inventory(steam_id, cookies)

        # Transform
        descripts: SteamInventory = self.__transform_raw_descriptions(descripts_raw)
        assets: SteamInventory = self.__transform_raw_assets(assets_raw, descripts_raw, user_id)

        # Load
        descripts.save('descriptions')
        SteamTradingCards.set_relationship_with_item_descripts(SteamInventory.get_all('descriptions').df)
        assets.save('assets', user_id)

        inventory = SteamInventory.get_current_inventory_from_db(user_id)
        return inventory

    def __download_raw_inventory(self, steam_id: str, cookies: dict) -> tuple[list, list]:
        progress_text = 'Downloading inventory'
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)

        progress_counter = 0
        items_per_page = 2000

        first_page_url = f'{super().BASESTEAMURL}inventory/{steam_id}/753/6?count={items_per_page}'
        inventory_page = requests.get(first_page_url, cookies=cookies).json()

        inventory_size = inventory_page['total_inventory_count']
        progress_counter += 1
        progress = progress_counter * items_per_page
        GenericUI.progress_completed(progress=progress, total=inventory_size, text=progress_text)

        descripts: list = inventory_page['descriptions']
        assets: list = inventory_page['assets']
        while 'more_items' in inventory_page.keys():
            next_page_url = f"{first_page_url}&start_assetid={inventory_page['last_assetid']}"
            inventory_page = requests.get(next_page_url, cookies=cookies).json()

            descripts.extend(inventory_page['descriptions'])
            assets.extend(inventory_page['assets'])

            progress_counter += 1
            progress = progress_counter * items_per_page
            GenericUI.progress_completed(progress=progress, total=inventory_size, text=progress_text)
        GenericUI.progress_completed(progress=1, total=1, text=progress_text)

        return descripts, assets

    def __transform_raw_descriptions(self, descripts_raw: list[dict]) -> SteamInventory:
        game_ids = self.__get_game_ids(descripts_raw)
        class_ids = [d['classid'] for d in descripts_raw]
        type_ids = self.__get_item_types(descripts_raw)
        names = [d['name'] for d in descripts_raw]
        url_names = self.__get_url_names(descripts_raw)
        descripts = SteamInventory(
            game_id=game_ids, name=names, type_id=type_ids, class_id=class_ids, url_name=url_names,
        )
        return descripts

    def __transform_raw_assets(self, assets_raw: list[dict], descripts_raw: list[dict], user_id: int) -> SteamInventory:
        user_ids = [user_id] * len(assets_raw)
        class_ids = [a['classid'] for a in assets_raw]
        asset_ids = [a['assetid'] for a in assets_raw]
        marketables = self.__get_asset_marketable(assets_raw, descripts_raw)
        assets = SteamInventory(user_id=user_ids, class_id=class_ids, asset_id=asset_ids, marketable=marketables)
        return assets

    def __get_game_ids(self, descripts_raw: list[dict]) -> list:
        self.__save_new_games(descripts_raw)
        # market_fee_app is not as reliable as market_hash_name, not sure why
        # game_market_ids = [d['market_fee_app'] for d in descripts_raw]
        game_market_ids = [int(d['market_hash_name'].split('-')[0]) for d in descripts_raw]
        game_ids = SteamGames.get_ids_list_by_market_ids_list(game_market_ids)
        return game_ids

    @staticmethod
    def __save_new_games(descripts_raw: list[dict]) -> None:
        inventory_game_market_ids = {d['market_fee_app'] for d in descripts_raw}
        saved_game_market_ids = SteamGames().get_market_ids()

        new_market_ids = []
        for game_market_id in inventory_game_market_ids:
            if str(game_market_id) not in saved_game_market_ids:
                new_market_ids.append(game_market_id)

        for d in descripts_raw:
            if d['market_fee_app'] in new_market_ids:
                tags = d['tags']
                game_name = next(tag['localized_tag_name'] for tag in tags if tag['category'] == 'Game')
                SteamGames(
                    name=game_name, market_id=d['market_fee_app']
                ).save()

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
        def get_url_name_from_market_hash_name(market_hash_name):
            hash_splitted = market_hash_name.split('-')
            hash_splitted.pop(0)
            url_name_raw = '-'.join(hash_splitted)
            url_name = requests.utils.quote(url_name_raw)
            return url_name
        url_names = [get_url_name_from_market_hash_name(d['market_hash_name']) for d in descripts_raw]
        return url_names

    @staticmethod
    def __get_asset_marketable(assets_raw: list[dict], descripts_raw: list[dict]) -> list:
        instance_id_marketable: dict = {d['instanceid']: d['marketable'] for d in descripts_raw}
        asset_instances = [a['instanceid'] for a in assets_raw]
        marketables = [instance_id_marketable[instance] for instance in asset_instances]
        return marketables
