from datetime import datetime

from repositories.QueryBuilderPG import QueryBuilderPG
from db.DBController import DBController


class BuyOrdersRepository:

    @staticmethod
    def get_all(columns: list) -> list[tuple]:
        query = f"""SELECT {', '.join(columns)} FROM buy_orders;"""
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_game_ids_with_most_outdated_orders(n_of_games: int) -> list[tuple]:
        query = f"""
            SELECT
                DISTINCT(is2.game_id), 
                MIN(bo.updated_at) OVER (PARTITION BY is2.game_id ORDER BY bo.updated_at) oldest_updated_item_timestamp
            FROM buy_orders bo 
            INNER JOIN items_steam is2 ON is2.id = bo.item_steam_id 
            WHERE active 
            ORDER BY oldest_updated_item_timestamp
            LIMIT {n_of_games};
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_last_buy_orders(columns: list, steam_item_ids: list, user_id: int) -> list[tuple]:
        steam_item_ids = [str(item) for item in steam_item_ids]
        query = f"""
            SELECT {', '.join(columns)}
            FROM buy_orders
            WHERE
                item_steam_id IN ('{"', '".join(steam_item_ids)}')
                AND user_id = {user_id}
            ORDER BY RANK() OVER (PARTITION BY item_steam_id ORDER BY created_at DESC)
            LIMIT {len(steam_item_ids)};
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def insert_multiple_buy_orders(buy_orders: zip, columns: list) -> None:
        values = QueryBuilderPG.unzip_to_query_values_str(buy_orders)
        query = f"""
            INSERT INTO buy_orders ({', '.join(columns)})
            VALUES {values};
        """
        DBController.execute(query=query)

    @staticmethod
    def update_buy_order(buy_order_id: int, steam_buy_order_id: str, qtd: int) -> None:
        update_time = datetime.now()
        query = f"""
            UPDATE buy_orders
            SET
                steam_buy_order_id = {steam_buy_order_id}
                , qtd_estimate = {qtd}
                , qtd_current = {qtd}
                , updated_at = '{update_time}'
            WHERE buy_orders.buy_order_id = {buy_order_id};
        """
        DBController.execute(query=query)

    @staticmethod
    def set_last_buy_order_to_inactive(steam_item_id: str, user_id: int) -> None:
        update_time = datetime.now()
        query = f"""
            WITH to_update_id AS (
                SELECT buy_order_id FROM buy_orders
                WHERE
                    item_steam_id = '{steam_item_id}'
                    AND user_id = {user_id}
                ORDER BY RANK() OVER (PARTITION BY item_steam_id ORDER BY created_at DESC)
                LIMIT 1
            )
            UPDATE buy_orders
            SET
                active = False
                , qtd_estimate = 0
                , qtd_current = 0
                , updated_at = '{update_time}'
                , removed_at = '{update_time}'
            WHERE buy_orders.buy_order_id = (SELECT * FROM to_update_id);
        """
        DBController.execute(query=query)
