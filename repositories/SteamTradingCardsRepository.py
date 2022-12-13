from repositories.QueryBuilderPG import QueryBuilderPG
from db.DBController import DBController


class SteamTradingCardsRepository:

    @staticmethod
    def get_all(table_name: str = 'trading_cards') -> list[tuple]:
        query = f""" SELECT * FROM {table_name};"""
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def insert_multiple_trading_cards(tradings_cards: zip) -> None:
        values = QueryBuilderPG.unzip_to_values_query_str(tradings_cards)
        query = f"""
            INSERT INTO trading_cards (game_id, set_number, name, url_name)
            VALUES {values}
            ON CONFLICT (game_id, set_number) DO UPDATE
            SET
                name = EXCLUDED.name,
                url_name = EXCLUDED.url_name;
        """
        DBController.execute(query=query)

    @staticmethod
    def insert_trading_cards_to_item_descripts(relationships: zip, cols_to_insert: list[str]) -> None:
        columns = QueryBuilderPG.cols_to_insert_list_to_str(cols_to_insert)
        values = QueryBuilderPG.unzip_to_values_query_str(relationships)
        query = f"""
            INSERT INTO trading_cards_to_item_descripts {columns}
            VALUES {values};
        """
        DBController.execute(query=query)
