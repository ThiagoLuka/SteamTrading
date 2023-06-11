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
    def get_game_ids_with_most_outdated_orders(n_of_games: int, user_id: int) -> list[tuple]:
        query = f"""
            SELECT
                DISTINCT(is2.game_id), 
                MIN(bo.updated_at) OVER (PARTITION BY is2.game_id ORDER BY bo.updated_at) oldest_updated_item_timestamp
            FROM buy_orders bo 
            INNER JOIN items_steam is2 ON is2.id = bo.item_steam_id 
            WHERE active AND user_id = {user_id}
            ORDER BY oldest_updated_item_timestamp
            LIMIT {n_of_games};
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_game_ids_to_create_buy_order(n_of_games: int, user_id: int) -> list[tuple]:
        query = f"""
            WITH active_counter AS (
                SELECT
                    is2.game_id,
                    item_steam_id,
                    removed_at,
                    COUNT(CASE WHEN bo.active THEN 1 END) OVER win1 AS active_count,
                    MAX(bo.removed_at) OVER win1 AS last_item_remove_date
                FROM buy_orders bo
                INNER JOIN items_steam is2 ON bo.item_steam_id = is2.id 
                INNER JOIN user_game_trade ugt ON is2.game_id = ugt.game_id 
                WHERE ugt.user_id = {user_id}
                WINDOW win1 AS (PARTITION BY bo.item_steam_id)
            )
            SELECT 
                DISTINCT(game_id), last_item_remove_date
            FROM active_counter
            WHERE active_count = 0
            ORDER BY last_item_remove_date
            LIMIT {n_of_games};
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_game_last_buy_orders(columns: list, game_id: int, user_id: int) -> list[tuple]:
        query = f"""
            WITH table_a AS (
                SELECT
                    bo.*,
                    RANK() OVER (PARTITION BY item_steam_id ORDER BY created_at DESC) AS buy_order_rank
                FROM buy_orders bo
                INNER JOIN items_steam is2 ON bo.item_steam_id = is2.id
                WHERE game_id = {game_id} AND user_id = {user_id}
	        )
            SELECT {', '.join(columns)}
            FROM table_a
            WHERE buy_order_rank = 1;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_item_last_buy_orders(columns: list, steam_item_id: int, user_id: int, amount: int):
        query = f"""
            SELECT {', '.join(columns)}
            FROM buy_orders bo 
            WHERE item_steam_id = {steam_item_id} AND user_id = {user_id}
            ORDER BY removed_at DESC
            LIMIT {amount};
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
    def set_last_buy_order_to_inactive(steam_item_id: int, user_id: int) -> None:
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
