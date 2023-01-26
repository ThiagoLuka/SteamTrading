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
    def get_all_types() -> list[tuple]:
        query = f"""
            SELECT id, name
            FROM item_steam_types;
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
