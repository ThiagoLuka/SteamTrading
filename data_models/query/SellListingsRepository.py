from .BaseQueryRepository import BaseQueryRepository


class SellListingsRepository(BaseQueryRepository):

    @classmethod
    def get_current_sell_listings(cls, user_id: int) -> list[tuple]:
        sell_listing = cls.query_tables(table_type='sell_listing')
        query = f"""
        SELECT
              sl.id
            , sl.game_id
            , sl.id AS item_id
            , sl.asset_id AS asset_id
            , sl.steam_sell_listing_id
            , sl.price_buyer
            , sl.price_to_receive
            , sl.steam_created_at
            , sl.created_at
            , sl.removed_at
        FROM {sell_listing} sl
        WHERE sl.active AND sl.user_id = '{user_id}';
        """
        result = cls._db_execute(query=query)
        return result

    @classmethod
    def get_buyer_to_seller_price_dict(cls) -> list[tuple]:
        buyer_to_seller_price = cls.query_tables(table_type='buyer_to_seller_price')
        query = f"""
        SELECT
              price_buyer
            , price_seller
        FROM {buyer_to_seller_price}
        ORDER BY price_buyer;
        """
        result = cls._db_execute(query=query)
        return result
