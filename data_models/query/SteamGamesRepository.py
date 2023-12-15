from data_models.QueryBuilderPG import QueryBuilderPG
from data_models.db.DBController import DBController


class SteamGamesRepository:

    def get_all_by_ids_new(self, ids: list[int], with_items: bool) -> list[tuple]:
        ids = [str(i) for i in ids]
        query = self._with_items_query(ids) if with_items else self._without_items_query(ids)
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def _with_items_query(ids: list[str]):
        return f"""
        SELECT
              g.id
            , g.name
            , g.market_id
            , g.has_trading_cards
            , is2.id AS item_id
            , is2.name AS item_name
            , ist.name AS steam_item_type
            , is2.market_url_name AS item_market_url_name
            , itc.set_number
        FROM public.games g
        LEFT JOIN public.items_steam is2 ON is2.game_id = g.id
        LEFT JOIN public.item_trading_cards itc ON itc.item_steam_id = is2.id
        LEFT JOIN public.item_steam_types ist ON ist.id = is2.item_steam_type_id
        WHERE
            g.id IN ({', '.join(ids)});
        """

    @staticmethod
    def _without_items_query(ids: list[str]) -> str:
        return f"""
        SELECT
              id
            , name
            , market_id
            , has_trading_cards
        FROM public.games g
        WHERE
            id IN ({', '.join(ids)});
        """

    @staticmethod
    def get_has_trading_cards_but_none_found() -> list[tuple]:
        query = """
            SELECT DISTINCT g.id AS id
            FROM games g
            LEFT JOIN item_trading_cards itc ON itc.game_id = g.id
            WHERE
                has_trading_cards AND set_numberIS NULL;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_item_type_id(type_name: str) -> int:
        type_name = QueryBuilderPG.sanitize_string(type_name)
        query = f"""
            SELECT id
            FROM item_steam_types
            WHERE name = '{type_name}';
        """
        result = DBController.execute(query=query, get_result=True)
        return result[0][0]

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
