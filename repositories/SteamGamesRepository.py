from repositories.QueryBuilderPG import QueryBuilderPG
from db.DBController import DBController


class SteamGamesRepository:

    @staticmethod
    def get_all() -> list[tuple]:
        query = f"""SELECT * FROM games;"""
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_all_without_trading_cards() -> list[tuple]:
        query = """
            SELECT
                DISTINCT games.id AS id,
                games.name AS name,
                market_id
            FROM games
            FULL OUTER JOIN trading_cards ON trading_cards.game_id = games.id
            WHERE trading_cards.id IS NULL;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_by_name(name: str) -> list[tuple]:
        query = f"""
            SELECT * FROM games
            WHERE name = '{name}';
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_by_market_id(market_id: str) -> list[tuple]:
        query = f"""
            SELECT * FROM games
            WHERE market_id = '{market_id}';
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def upsert_single_game(name: str, market_id: str) -> None:
        name = QueryBuilderPG.sanitize_string(name)
        query = f"""
            INSERT INTO games (name, market_id)
            VALUES ('{name}', '{market_id}')
            ON CONFLICT (market_id) DO UPDATE
            SET name = EXCLUDED.name;
        """
        DBController.execute(query=query)

    @staticmethod
    def upsert_multiple_games(games: zip) -> None:
        values = QueryBuilderPG.unzip_to_values_query_str(games)
        query = f"""
            INSERT INTO games (name, market_id)
            VALUES {values}
            ON CONFLICT (market_id) DO UPDATE
            SET name = EXCLUDED.name;
        """
        DBController.execute(query=query)
