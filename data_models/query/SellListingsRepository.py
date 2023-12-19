from .BaseQueryRepository import BaseQueryRepository


class SellListingsRepository(BaseQueryRepository):

    @classmethod
    def get_current_sell_listings(cls, user_id: int) -> list[tuple]:
        query = f"""
        SELECT
              sl.id
            , is2.game_id
            , is2.id AS item_id
            , sl.steam_sell_listing_id
            , sl.price_buyer
            , sl.price_to_receive
            , sl.steam_created_at
            , sl.created_at
            , sl.removed_at
        FROM public.sell_listing sl
        INNER JOIN item_steam_assets isa ON isa.id = sl.asset_id
        INNER JOIN public.items_steam is2 ON is2.id = isa.item_steam_id
        WHERE active AND sl.user_id = '{user_id}';
        """
        result = cls._db_execute(query=query)
        return result
