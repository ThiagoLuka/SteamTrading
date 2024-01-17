from data_models.command import (
    BasePersistenceModel,
    BuyOrder,
    Game,
    SellListing,
    SteamAsset,
    SteamAssetOrigin,
    SteamBadge,
    SteamItem,
)


class PersistToDB:

    @staticmethod
    def persist(data_type: str, source: str, data: list[dict] = None, **kwargs):
        data_persistence_reference = {
            'game': Game,
            'steam_item': SteamItem,
            'steam_badge': SteamBadge,
            'steam_asset': SteamAsset,
            'steam_asset_origin': SteamAssetOrigin,
            'buy_order': BuyOrder,
            'sell_listing': SellListing,
        }.get(data_type, BasePersistenceModel)
        data_persistence_reference(
            data=data
        ).save(source=source, **kwargs)
