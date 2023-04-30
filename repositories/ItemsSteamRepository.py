from typing import Optional

from repositories.QueryBuilderPG import QueryBuilderPG
from db.DBController import DBController


class ItemsSteamRepository:

    @staticmethod
    def get_all(columns: list, with_type_names: bool) -> list[tuple]:
        query = f"""
            SELECT {', '.join(columns)}
            FROM items_steam
            {'JOIN item_steam_types '
                'ON items_steam.item_steam_type_id = item_steam_types.id'
            if with_type_names else ''};
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_all_by_game(columns: list, game_id: str, item_types: Optional[list] = None):
        if item_types:
            item_types = "'" + "', '".join(item_types) + "'"
        query = f"""
            SELECT {', '.join(columns)}
            FROM items_steam
            JOIN item_steam_types
                ON items_steam.item_steam_type_id = item_steam_types.id
            WHERE
                game_id = {game_id}
                {f'AND item_steam_types.name IN ({item_types})' if item_types else ''};
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_all_types() -> list[tuple]:
        query = f"""
            SELECT id, name
            FROM item_steam_types;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_all_descriptions() -> list[tuple]:
        query = f"""
            SELECT item_steam_id, class_id
            FROM item_steam_descriptions;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_all_class_ids() -> list[tuple[str]]:
        query = f"""
            SELECT class_id
            FROM item_steam_descriptions;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_item_type_id(type_name: str) -> list[tuple]:
        type_name = QueryBuilderPG.sanitize_string(type_name)
        query = f"""
            SELECT id
            FROM item_steam_types
            WHERE name = '{type_name}';
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_ids_by_market_url_names(url_names: list[str]) -> list[tuple]:
        query = f"""
            SELECT market_url_name, id
            FROM items_steam
            WHERE market_url_name IN ('{"', '".join(url_names)}')
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_by_game_id_and_market_url_names(columns: list, game_ids_and_market_url_names: zip) -> list[tuple]:
        target_tuples = QueryBuilderPG.unzip_to_query_values_str(game_ids_and_market_url_names)
        query = f"""
            SELECT {', '.join(columns)}
            FROM items_steam
            WHERE (game_id, market_url_name) IN ({target_tuples})
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_booster_pack(columns: list, game_id: str) -> list[tuple]:
        query = f"""
            SELECT {', '.join(columns)}
            FROM items_steam
            INNER JOIN item_booster_packs ibp ON items_steam.id = ibp.item_steam_id
            WHERE items_steam.game_id = '{game_id}';
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_game_cards(columns: list, game_id: str) -> list[tuple]:
        query = f"""
            SELECT {', '.join(columns)}
            FROM items_steam
            INNER JOIN item_trading_cards itc ON items_steam.id = itc.item_steam_id
            WHERE
                items_steam.game_id = '{game_id}'
                AND foil = False
            ORDER BY set_number;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def upsert_multiple_items(items: zip, columns: list) -> None:
        values = QueryBuilderPG.unzip_to_query_values_str(items)
        query = f"""
            INSERT INTO items_steam ({', '.join(columns)})
            VALUES {values};
        """
        DBController.execute(query=query)

    @staticmethod
    def upsert_item_type(type_id: int, type_name: str) -> None:
        type_name = QueryBuilderPG.sanitize_string(type_name)
        query = f"""
            INSERT INTO item_steam_types (id, name)
            VALUES ({type_id}, '{type_name}')
            ON CONFLICT (name) DO UPDATE
            SET id = EXCLUDED.id;
        """
        DBController.execute(query=query)

    @staticmethod
    def insert_item_description(descripts: zip, columns: list) -> None:
        values = QueryBuilderPG.unzip_to_query_values_str(descripts)
        query = f"""
            INSERT INTO item_steam_descriptions ({', '.join(columns)})
            VALUES {values};
        """
        DBController.execute(query=query)
