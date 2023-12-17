from data_models.db.DBController import DBController


class SteamInventoryRepository:

    @staticmethod
    def get_current_inventory(user_id: int) -> list[tuple]:
        query = f"""
        SELECT
              isa.id AS id
            , is2.game_id
            , isa.item_steam_id
            , isa.asset_id AS steam_asset_id
            , isa.marketable
            , isa.created_at
        FROM public.item_steam_assets isa
        INNER JOIN public.items_steam is2 ON is2.id = isa.item_steam_id
        WHERE
            user_id = '{user_id}'
            AND removed_at IS NULL;
        """
        result = DBController.execute(query=query, get_result=True)
        return result
