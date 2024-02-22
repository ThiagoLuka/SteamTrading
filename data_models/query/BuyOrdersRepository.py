from .BaseQueryRepository import BaseQueryRepository


class BuyOrdersRepository(BaseQueryRepository):

    @classmethod
    def get_current_buy_orders(cls, user_id: int) -> list[tuple]:
        buy_order = cls.query_tables(table_type='buy_order')
        user_game = cls.query_tables(table_type='user_game')
        query = f"""
        SELECT
              bo.id AS id
            , bo.game_id
            , bo.item_id
            , bo.steam_buy_order_id
            , bo.price AS price
            , bo.qtd_start
            , bo.qtd_current
            , bo.created_at
            , bo.updated_at
            , bo.removed_at
        FROM {buy_order} bo
        INNER JOIN {user_game} ugt ON
            bo.user_id = ugt.user_id AND bo.game_id = ugt.game_id
        WHERE active AND bo.user_id = '{user_id}';
        """
        result = cls._db_execute(query=query)
        return result

    @classmethod
    def get_inactive_with_created_at_rank(cls, user_id: int) -> list[tuple]:
        buy_order = cls.query_tables(table_type='buy_order')
        user_game = cls.query_tables(table_type='user_game')
        query = f"""
        SELECT
              bo.id AS id
            , bo.game_id
            , bo.item_id
            , bo.steam_buy_order_id
            , bo.price
            , bo.qtd_start
            , bo.qtd_current
            , bo.created_at
            , bo.updated_at
            , bo.removed_at
            , RANK() OVER (PARTITION BY item_id ORDER BY created_at DESC) AS created_rank
        FROM {buy_order} bo
        INNER JOIN {user_game} ugt ON
            bo.user_id = ugt.user_id AND bo.game_id = ugt.game_id
        WHERE NOT bo.active AND bo.user_id = '{user_id}';
        """
        result = cls._db_execute(query=query)
        return result
