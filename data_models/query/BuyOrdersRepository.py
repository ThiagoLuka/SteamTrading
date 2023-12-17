from data_models.db.DBController import DBController


class BuyOrdersRepository:

    @staticmethod
    def get_current_buy_orders(user_id: int) -> list[tuple]:
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
        FROM public.buy_orders bo
        INNER JOIN public.items_steam is2 ON is2.id = bo.item_steam_id
        INNER JOIN public.user_game_trade ugt
            ON ugt.user_id = bo.user_id AND is2.game_id = ugt.game_id
        WHERE active AND bo.user_id = '{user_id}';
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_inactive_with_created_at_rank(user_id: int) -> list[tuple]:
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
        FROM public.buy_orders bo
        INNER JOIN public.items_steam is2 ON is2.id = bo.item_steam_id
        INNER JOIN public.user_game_trade ugt
            ON ugt.user_id = bo.user_id AND is2.game_id = ugt.game_id
        WHERE NOT active AND bo.user_id = '{user_id}';
        """
        result = DBController.execute(query=query, get_result=True)
        return result
