from repositories.QueryBuilderPG import QueryBuilderPG
from db.DBController import DBController


class SteamTradingCardsRepository:

    @staticmethod
    def get_all() -> list[tuple]:
        query = f""" SELECT * FROM trading_cards;"""
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def insert_multiple_tcgs(tradings_cards: zip) -> None:
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
