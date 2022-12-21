from repositories.QueryBuilderPG import QueryBuilderPG
from db.DBController import DBController


class SteamInventoryRepository:

    @staticmethod
    def get_all(table_name: str = 'assets') -> list[tuple]:
        query = f"""SELECT * FROM item_{table_name};"""
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_current_by_user_id(user_id: int) -> list[tuple]:
        query = f"""
            SELECT * FROM item_assets
            WHERE
                user_id = '{user_id}'
                AND removed_at IS NULL;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_current_size_by_user_id(user_id: int) -> int:
        query = f"""
            SELECT COUNT(asset_id) FROM item_assets
            WHERE
                user_id = '{user_id}'
                AND removed_at IS NULL;
        """
        result = DBController.execute(query=query, get_result=True)
        return result[0][0]

    @staticmethod
    def last_inventory_saved_date(user_id: int) -> list[tuple]:
        query = f"""
            SELECT created_at
            FROM item_assets
            WHERE user_id = {user_id}
            ORDER BY created_at DESC
            LIMIT 1;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_booster_pack_assets_id(user_id: int, game_name: str) -> list[tuple]:
        game_name = QueryBuilderPG.sanitize_string(game_name)
        query = f"""
            SELECT asset_id
            FROM item_assets i_assets
            INNER JOIN item_descriptions ON item_descriptions.id = i_assets.description_id
            INNER JOIN item_types ON item_descriptions.type_id = item_types.id
            INNER JOIN games ON games.id = item_descriptions.game_id
            WHERE
                user_id = '{user_id}'
                AND games.name = '{game_name}'
                AND item_types.name = 'Booster Pack'
                AND removed_at IS NULL;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_overview_marketable_cards(user_id: int) -> list[tuple]:
        query = f"""
            SELECT
                games.name AS game_name,
                COUNT(i_assets.id) AS marketable_cards
            FROM item_assets i_assets
            INNER JOIN item_descriptions ON item_descriptions.id = i_assets.description_id
            INNER JOIN item_types ON item_descriptions.type_id = item_types.id
            INNER JOIN games ON games.id = item_descriptions.game_id
            WHERE
                user_id = '{user_id}'
                AND marketable = True
                AND item_types.name = 'Trading Card'
                AND removed_at IS NULL
            GROUP BY game_name;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_marketable_cards_asset_ids(user_id: int, game_name: str) -> list[tuple]:
        game_name = QueryBuilderPG.sanitize_string(game_name)
        query = f"""
            SELECT
                tc.set_number,
                tc.name AS card_name,
                i_assets.asset_id AS asset_id
            FROM item_assets i_assets
            INNER JOIN item_descriptions i_descripts ON i_descripts.id = i_assets.description_id
            INNER JOIN item_types ON i_descripts.type_id = item_types.id
            INNER JOIN games ON games.id = i_descripts.game_id
            INNER JOIN trading_cards_to_item_descripts tctid ON tctid.description_id = i_descripts.id
            INNER JOIN trading_cards tc ON tc.id = tctid.trading_card_id
            WHERE
                user_id = '{user_id}'
                AND marketable = True
                AND games.name = '{game_name}'
                AND item_types.name = 'Trading Card'
                AND tctid.foil = False
                AND removed_at IS NULL
            ORDER BY tc.set_number;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def upsert_descriptions(descripts: zip, cols_to_insert: list[str]) -> None:
        columns = QueryBuilderPG.cols_to_insert_list_to_str(cols_to_insert)
        values = QueryBuilderPG.unzip_to_values_query_str(descripts)
        query = f"""
            INSERT INTO item_descriptions {columns}
            VALUES {values}
            ON CONFLICT (class_id) DO UPDATE
            SET url_name = EXCLUDED.url_name;
        """
        DBController.execute(query=query)

    @staticmethod
    def upsert_new_assets(assets: zip, cols_to_insert: list[str]) -> None:
        columns = QueryBuilderPG.cols_to_insert_list_to_str(cols_to_insert)
        values = QueryBuilderPG.unzip_to_values_query_str(assets)
        query = f"""
            INSERT INTO item_assets {columns}
            VALUES {values}
            ON CONFLICT (asset_id) DO UPDATE
            SET marketable = EXCLUDED.marketable;
        """
        DBController.execute(query=query)

    @staticmethod
    def update_removed_assets(assets: zip) -> None:
        values = QueryBuilderPG.unzip_to_values_query_str(assets)
        query = f"""
            UPDATE item_assets
            SET
                removed_at = update.removed_at::timestamp
            FROM (
                VALUES {values}
            ) AS update(id, removed_at)
            WHERE
                item_assets.id = update.id::int;
        """
        DBController.execute(query=query)

    @staticmethod
    def insert_item_types(item_types: zip) -> None:
        values = QueryBuilderPG.unzip_to_values_query_str(item_types)
        query = f"""
            INSERT INTO item_types
            VALUES {values};
        """
        DBController.execute(query=query)
