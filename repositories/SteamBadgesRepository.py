from db.DBController import DBController


class SteamBadgesRepository:

    @staticmethod
    def get_user_total_experience(user_id: int) -> int:
        query = f"""
            SELECT sum(experience) FROM user_badges
            WHERE user_id = {user_id} AND active = True;
        """
        result = DBController.execute(query=query, get_result=True)
        return result[0][0]
