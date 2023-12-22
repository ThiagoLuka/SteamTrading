from data_models.db.DBController import DBController


class SteamUserRepository:

    @staticmethod
    def save_user(steam_id: str, steam_alias: str = '') -> None:
        query = f"""
            INSERT INTO steam_user (steam_id, steam_alias)
            VALUES ('{steam_id}', '{steam_alias}')
            ON CONFLICT (steam_id) DO UPDATE
            SET steam_alias = EXCLUDED.steam_alias;
        """
        DBController.execute(query=query)

    @staticmethod
    def get_by_steam_id(steam_id: str) -> list[tuple]:
        query = f"""
            SELECT id, steam_id, steam_alias
            FROM steam_user
            WHERE steam_id = '{steam_id}';
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_games_allowed(user_id: int) -> list[tuple]:
        query = f"""
        SELECT game_id
        FROM steam_user_marketable_game
        WHERE user_id = '{user_id}';
        """
        result = DBController.execute(query=query, get_result=True)
        return result
