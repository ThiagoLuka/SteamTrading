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
    def get_foil_game_cards(columns: list, game_id: str) -> list[tuple]:
        query = f"""
            SELECT {', '.join(columns)}
            FROM items_steam
            WHERE
	            game_id = {game_id}
	            AND name LIKE '%Foil%';
        """
        result = DBController.execute(query=query, get_result=True)
        return result
