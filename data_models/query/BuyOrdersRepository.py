from .BaseQueryRepository import BaseQueryRepository


class BuyOrdersRepository(BaseQueryRepository):

    @classmethod
    def get_current_buy_orders(cls, user_id: int) -> list[tuple]:
        buy_order = cls.query_tables(table_type='buy_order')
        item = cls.query_tables(table_type='steam_item')
        user_game = cls.query_tables(table_type='user_game')
        query = f"""
        SELECT
              bo.buy_order_id AS id
            , is2.game_id
            , bo.item_steam_id
            , bo.steam_buy_order_id
            , bo.price AS price
            , bo.qtd_start
            , bo.qtd_current
            , bo.created_at
            , bo.updated_at
            , bo.removed_at
        FROM {buy_order} bo
        INNER JOIN {item} is2 ON is2.id = bo.item_steam_id
        INNER JOIN {user_game} ugt ON
            ugt.user_id = bo.user_id AND is2.game_id = ugt.game_id
        WHERE active AND bo.user_id = '{user_id}';
        """
        result = cls._db_execute(query=query)
        return result

    @classmethod
    def get_inactive_with_created_at_rank(cls, user_id: int) -> list[tuple]:
        buy_order = cls.query_tables(table_type='buy_order')
        item = cls.query_tables(table_type='steam_item')
        user_game = cls.query_tables(table_type='user_game')
        query = f"""
        SELECT
              bo.buy_order_id AS id
            , is2.game_id
            , bo.item_steam_id
            , bo.steam_buy_order_id
            , bo.price
            , bo.qtd_start
            , bo.qtd_current
            , bo.created_at
            , bo.updated_at
            , bo.removed_at
            , RANK() OVER (PARTITION BY item_steam_id ORDER BY created_at DESC) AS created_rank
        FROM {buy_order} bo
        INNER JOIN {item} is2 ON is2.id = bo.item_steam_id
        INNER JOIN {user_game} ugt ON
            ugt.user_id = bo.user_id AND is2.game_id = ugt.game_id
        WHERE NOT active AND bo.user_id = '{user_id}';
        """
        result = cls._db_execute(query=query)
        return result
