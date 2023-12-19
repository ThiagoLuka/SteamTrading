from .BaseQueryRepository import BaseQueryRepository


class SteamBadgesRepository(BaseQueryRepository):

    @classmethod
    def get_user_total_experience(cls, user_id: int) -> int:
        query = f"""
            SELECT sum(experience)
            FROM user_badges
            WHERE
                user_id = {user_id} AND active = True;
        """
        result = cls._db_execute(query=query)
        return result[0][0]
