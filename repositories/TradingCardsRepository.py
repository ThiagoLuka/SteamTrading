from repositories.QueryBuilderPG import QueryBuilderPG
from db.DBController import DBController


class TradingCardsRepository:

    @staticmethod
    def get_all(table: str, columns: list) -> list[tuple]:
        query = f"""
            SELECT {', '.join(columns)}
            FROM {table};
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def insert_multiples(table: str, columns: list, items: zip) -> None:
        values = QueryBuilderPG.unzip_to_query_values_str(items)
        query = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES {values};
        """
        DBController.execute(query=query)

    @staticmethod
    def update_booster_packs_opened(game_id: int, times_opened: int, foil_quantity: int) -> None:
        query = f"""
            UPDATE item_booster_packs
            SET
                times_opened = times_opened + {times_opened},
                foil_quantity = foil_quantity + {foil_quantity}
            WHERE game_id = {game_id};
        """
        DBController.execute(query=query)