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
