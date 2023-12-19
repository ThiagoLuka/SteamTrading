from data_models.query import (
    BaseQueryRepository,
    SteamGamesRepository,
    SteamInventoryRepository,
    SteamBadgesRepository,
    SellListingsRepository,
    BuyOrdersRepository,
)


class QueryDB:

    @staticmethod
    def get_repo(data_type: str):
        return {
            'games': SteamGamesRepository,
            'inventory': SteamInventoryRepository,
            'badges': SteamBadgesRepository,
            'sell_listing': SellListingsRepository,
            'buy_order': BuyOrdersRepository,
        }.get(data_type, BaseQueryRepository)
