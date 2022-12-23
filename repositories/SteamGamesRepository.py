from repositories.QueryBuilderPG import QueryBuilderPG
from db.DBController import DBController


class SteamGamesRepository:

    @staticmethod
    def get_all(columns: list) -> list[tuple]:
        query = f"""SELECT {', '.join(columns)} FROM games;"""
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
    def get_by_name(name: str, columns: list) -> list[tuple]:
        query = f"""
            SELECT {', '.join(columns)} FROM games
            WHERE name = '{name}';
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_by_market_id(market_id: str, columns: list) -> list[tuple]:
        query = f"""
            SELECT {', '.join(columns)} FROM games
            WHERE market_id = '{market_id}';
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def upsert_single_game(name: str, market_id: str, columns: list) -> None:
        name = QueryBuilderPG.sanitize_string(name)
        query = f"""
            INSERT INTO games ({', '.join(columns)})
            VALUES ('{name}', '{market_id}')
            ON CONFLICT (market_id) DO UPDATE
            SET name = EXCLUDED.name;
        """
        DBController.execute(query=query)

    @staticmethod
    def upsert_multiple_games(games: zip, columns: list) -> None:
        values = QueryBuilderPG.unzip_to_query_values_str(games)
        query = f"""
            INSERT INTO games ({', '.join(columns)})
            VALUES {values}
            ON CONFLICT (market_id) DO UPDATE
            SET name = EXCLUDED.name;
        """
        DBController.execute(query=query)
