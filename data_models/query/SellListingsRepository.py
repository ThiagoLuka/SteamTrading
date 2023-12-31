from .BaseQueryRepository import BaseQueryRepository


class SellListingsRepository(BaseQueryRepository):

    @classmethod
    def get_current_sell_listings(cls, user_id: int) -> list[tuple]:
        sell_listing = cls.query_tables(table_type='sell_listing')
        inventory = cls.query_tables(table_type='inventory')
        item = cls.query_tables(table_type='steam_item')
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
        FROM {sell_listing} sl
        INNER JOIN {inventory} isa ON isa.id = sl.asset_id
        INNER JOIN {item} is2 ON is2.id = isa.item_id
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
