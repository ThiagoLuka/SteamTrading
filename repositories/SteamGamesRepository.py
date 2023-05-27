from repositories.QueryBuilderPG import QueryBuilderPG
from db.DBController import DBController


class SteamGamesRepository:

    @staticmethod
    def get_all(columns: list) -> list[tuple]:
        query = f"""SELECT {', '.join(columns)} FROM games;"""
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_all_with_trading_cards_not_registered() -> list[tuple]:
        query = """
            SELECT
                DISTINCT games.id AS id,
                games.name AS name,
                market_id
            FROM games
            FULL OUTER JOIN item_trading_cards ON item_trading_cards.game_id = games.id
            WHERE
                has_trading_cards = True
                AND item_trading_cards.id IS NULL;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_all_by_id(ids: list[str], columns: list):
        query = f"""
            SELECT {', '.join(columns)} FROM games
            WHERE id IN ({', '.join(ids)});
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_by_name(name: str, columns: list) -> list[tuple]:
        name = QueryBuilderPG.sanitize_string(name)
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

    @staticmethod
    def update_to_has_no_cards(game_id: int) -> None:
        query = f"""
            UPDATE games
            SET has_trading_cards = False
            WHERE games.id = {game_id}
        """
        DBController.execute(query=query)
