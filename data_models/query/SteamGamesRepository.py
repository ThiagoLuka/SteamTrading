from data_models.QueryUtils import QueryUtils
from .BaseQueryRepository import BaseQueryRepository


class SteamGamesRepository(BaseQueryRepository):

    @classmethod
    def get_all_games_by_ids(cls, ids: list[int], with_items: bool) -> list[tuple]:
        ids = [str(i) for i in ids]
        query = cls._with_items_query(ids) if with_items else cls._without_items_query(ids)
        result = cls._db_execute(query=query)
        return result

    @classmethod
    def _without_items_query(cls, ids: list[str]) -> str:
        game = cls.query_tables(table_type='game')
        return f"""
        SELECT
              id
            , name
            , market_id
            , has_trading_cards
        FROM {game} g
        WHERE
            id IN ({', '.join(ids)});
        """

    @classmethod
    def _with_items_query(cls, ids: list[str]):
        game = cls.query_tables(table_type='game')
        item = cls.query_tables(table_type='steam_item')
        trading_card = cls.query_tables(table_type='steam_item_trading_card')
        item_type = cls.query_tables(table_type='steam_item_type')
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
            , itc.foil
        FROM {game} g
        LEFT JOIN {item} is2 ON is2.game_id = g.id
        LEFT JOIN {trading_card} itc ON itc.item_id = is2.id
        LEFT JOIN {item_type} ist ON ist.id = is2.item_steam_type_id
        WHERE
            g.id IN ({', '.join(ids)});
        """

    @classmethod
    def get_has_trading_cards_but_none_found(cls) -> list[tuple]:
        game = cls.query_tables(table_type='game')
        trading_card = cls.query_tables(table_type='steam_item_trading_card')
        query = f"""
            SELECT DISTINCT g.id AS id
            FROM {game} g
            LEFT JOIN {trading_card} itc ON itc.game_id = g.id
            WHERE
                has_trading_cards AND set_number IS NULL;
        """
        result = cls._db_execute(query=query)
        return result

    @classmethod
    def get_item_type_id(cls, type_name: str) -> int:
        type_name = QueryUtils.sanitize_string(type_name)
        item_type = cls.query_tables(table_type='steam_item_type')
        query = f"""
            SELECT id
            FROM {item_type} ist
            WHERE name = '{type_name}';
        """
        result = cls._db_execute(query=query)
        return result[0][0]
