from .BaseQueryRepository import BaseQueryRepository


class SteamInventoryRepository(BaseQueryRepository):

    @classmethod
    def get_current_inventory(cls, user_id: int) -> list[tuple]:
        inventory = cls.query_tables(table_type='inventory')
        item = cls.query_tables(table_type='steam_item')
        query = f"""
        SELECT
              isa.id AS id
            , is2.game_id
            , isa.item_id
            , isa.steam_asset_id
            , isa.origin
            , isa.origin_price
            , isa.marketable
            , isa.created_at
        FROM {inventory} isa
        INNER JOIN {item} is2 ON is2.id = isa.item_id
        WHERE isa.active AND isa.user_id = '{user_id}';
        """
        result = cls._db_execute(query=query)
        return result
