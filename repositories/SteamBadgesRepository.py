from repositories.QueryBuilderPG import QueryBuilderPG
from db.DBController import DBController


class SteamBadgesRepository:

    @staticmethod
    def get_all(badge_type: str, columns: list) -> list[tuple]:
        query = f""" SELECT {', '.join(columns)} FROM {badge_type}_badges;"""
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_all_active_by_user_id(user_id: int, columns: list) -> list[tuple]:
        query = f"""
            SELECT {', '.join(columns)} FROM user_badges
            WHERE user_id = '{user_id}' AND active = True;
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_all_by_game_name(game_name: str, columns: list) -> list[tuple]:
        query = f"""
            SELECT {', '.join(columns)} FROM game_badges
            INNER JOIN games ON games.id = game_badges.game_id
            WHERE games.name = '{game_name}';
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_user_badges_with_type_details(user_id: int, badge_type: str, columns: list) -> list[tuple]:
        query = f"""
            SELECT {', '.join(columns)} FROM user_badges
            INNER JOIN {badge_type}_badges ON {badge_type}_badges.id = user_badges.{badge_type}_badge_id
            WHERE user_id = '{user_id}';
        """
        result = DBController.execute(query=query, get_result=True)
        return result

    @staticmethod
    def get_user_total_experience(user_id: int) -> int:
        query = f"""
            SELECT sum(experience) FROM user_badges
            WHERE user_id = {user_id} AND active = True;
        """
        result = DBController.execute(query=query, get_result=True)
        return result[0][0]

    @staticmethod
    def upsert_multiple_game_badges(game_badges: zip, columns: list[str]) -> None:
        values = QueryBuilderPG.unzip_to_query_values_str(game_badges)
        query = f"""
            INSERT INTO game_badges ({', '.join(columns)})
            VALUES {values}
            ON CONFLICT (game_id, level, foil) DO UPDATE
            SET name = EXCLUDED.name;
        """
        DBController.execute(query=query)

    @staticmethod
    def insert_multiple_badges(badge_type: str, pure_badges: zip, columns: list[str]) -> None:
        values = QueryBuilderPG.unzip_to_query_values_str(pure_badges)
        query = f"""
            INSERT INTO {badge_type}_badges ({', '.join(columns)})
            VALUES {values};
        """
        DBController.execute(query=query)

    @staticmethod
    def set_user_badges_to_inactive(user_badges_id: list[int]) -> None:
        for u_badge_id in user_badges_id:
            query = f"""
                UPDATE user_badges
                SET active = false
                WHERE id = {u_badge_id};
            """
            DBController.execute(query=query)
