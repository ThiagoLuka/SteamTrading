from db.DBController import DBController


class SteamInventoryRepository:

    @staticmethod
    def get_current_size_by_user_id(user_id: int) -> int:
        query = f"""
            SELECT COUNT(id) FROM item_steam_assets
            WHERE
                user_id = '{user_id}'
                AND removed_at IS NULL;
        """
        result = DBController.execute(query=query, get_result=True)
        return result[0][0]

    @staticmethod
    def get_booster_pack_assets_id(user_id: int, game_id: int) -> list[tuple]:
        query = f"""
            SELECT
                asset_id,
                isa.item_steam_id 
            FROM item_steam_assets isa 
            INNER JOIN items_steam is2 ON is2.id = isa.item_steam_id
            INNER JOIN item_steam_types ist ON ist.id = is2.item_steam_type_id
            WHERE
                user_id = '{user_id}'
                AND is2.game_id = '{game_id}'
                AND ist."name" = 'Booster Pack'
                AND removed_at IS NULL;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_overview_marketable_cards(user_id: int) -> list[tuple]:
        query = f"""
            SELECT
                games.name AS game_name,
                COUNT(assets.id) AS marketable_cards
            FROM item_steam_assets assets
            INNER JOIN items_steam ON items_steam.id = assets.item_steam_id
            INNER JOIN item_steam_types ON items_steam.item_steam_type_id = item_steam_types.id
            INNER JOIN games ON games.id = items_steam.game_id
            WHERE
                user_id = '{user_id}'
                AND assets.marketable = True
                AND item_steam_types.name = 'Trading Card'
                AND removed_at IS NULL
            GROUP BY game_name
            ORDER BY game_name;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_game_ids_with_oldest_marketable_cards(n_of_games: int, user_id: int) -> list[tuple]:
        query = f"""
            WITH table_a AS (
                SELECT
                    is2.game_id,
                    user_id,
                    MIN(created_at) OVER (PARTITION BY is2.game_id) AS first_asset_timestamp
                FROM item_steam_assets isa 
                INNER JOIN items_steam is2 ON isa.item_steam_id = is2.id
                INNER JOIN item_trading_cards itc ON itc.item_steam_id = is2.id 
                WHERE
                    marketable
                    AND removed_at IS NULL
                    AND NOT foil
                    AND user_id = {user_id}
            )
            SELECT 
                DISTINCT(table_a.game_id), first_asset_timestamp
            FROM table_a, user_game_trade ugt
            WHERE
                ugt.game_id = table_a.game_id
                AND ugt.user_id = table_a.user_id
            ORDER BY first_asset_timestamp
            LIMIT {n_of_games};
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_game_ids_with_booster_packs(n_of_games: int, user_id: int):
        query = f"""
            SELECT DISTINCT(is2.game_id) 
            FROM item_steam_assets isa 
            INNER JOIN items_steam is2 ON isa.item_steam_id = is2.id 
            INNER JOIN item_steam_types ist ON is2.item_steam_type_id = ist.id 
            WHERE
	            ist.name = 'Booster Pack'
	            AND removed_at IS NULL
	            AND user_id = {user_id}
	        LIMIT {n_of_games};
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_marketable_cards_asset_ids(user_id: int, game_id: int) -> list[tuple]:
        query = f"""
            SELECT 
                is2.name
                , isa.asset_id
            FROM items_steam is2 
            INNER JOIN item_steam_assets isa ON is2.id = isa.item_steam_id
            WHERE 
                user_id = '{user_id}'
                AND item_steam_type_id = '2'  -- item_type = card
                AND marketable = True 
                AND is2.game_id = '{game_id}'
                AND isa.removed_at IS NULL;
        """
        result = DBController.execute(query=query, get_result=True)
        return result
