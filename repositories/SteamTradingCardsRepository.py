from repositories.QueryBuilderPG import QueryBuilderPG
from db.DBController import DBController


class SteamTradingCardsRepository:

    @staticmethod
    def get_all(table_name: str, columns: list) -> list[tuple]:
        query = f""" SELECT {', '.join(columns)} FROM {table_name};"""
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def insert_multiple_trading_cards(tradings_cards: zip, columns: list) -> None:
        values = QueryBuilderPG.unzip_to_query_values_str(tradings_cards)
        query = f"""
            INSERT INTO trading_cards ({', '.join(columns)})
            VALUES {values}
            ON CONFLICT (game_id, set_number) DO UPDATE
            SET
                name = EXCLUDED.name,
                url_name = EXCLUDED.url_name;
        """
        DBController.execute(query=query)

    @staticmethod
    def insert_trading_cards_to_item_descripts(relationships: zip, columns: list[str]) -> None:
        values = QueryBuilderPG.unzip_to_query_values_str(relationships)
        query = f"""
            INSERT INTO trading_cards_to_item_descripts ({', '.join(columns)})
            VALUES {values};
        """
        DBController.execute(query=query)
