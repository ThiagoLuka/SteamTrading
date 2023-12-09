from repositories.SteamInventoryRepository import SteamInventoryRepository
from data_models.PandasDataModel import PandasDataModel


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
    def get_game_ids_with_booster_packs_to_be_opened(n_of_games: int, user_id: int) -> list:
        data = SteamInventoryRepository.get_game_ids_with_booster_packs(n_of_games, user_id)
        game_ids = [row[0] for row in data]
        return game_ids

    @staticmethod
    def get_booster_pack_assets_id(user_id: int, game_id: int) -> list:
        data = SteamInventoryRepository.get_booster_pack_assets_id(user_id, game_id)
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
