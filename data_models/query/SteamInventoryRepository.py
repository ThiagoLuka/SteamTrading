from .BaseQueryRepository import BaseQueryRepository


class SteamInventoryRepository(BaseQueryRepository):

    @classmethod
    def get_current_inventory(cls, user_id: int) -> list[tuple]:
        inventory = cls.query_tables(table_type='inventory')
        query = f"""
        SELECT
              isa.id AS id
            , isa.game_id
            , isa.item_id
            , isa.steam_asset_id
            , isa.origin
            , isa.origin_price
            , isa.marketable
            , isa.created_at
        FROM {inventory} isa
        WHERE isa.active AND isa.user_id = '{user_id}';
        """
        result = cls._db_execute(query=query)
        return result
