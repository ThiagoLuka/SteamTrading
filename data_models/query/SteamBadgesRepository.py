from .BaseQueryRepository import BaseQueryRepository


class SteamBadgesRepository(BaseQueryRepository):

    @classmethod
    def get_user_total_experience(cls, user_id: int) -> int:
        badge_user = cls.query_tables(table_type='badge_user')
        query = f"""
            SELECT sum(experience)
            FROM {badge_user} ub
            WHERE
                user_id = {user_id} AND active = True;
        """
        result = cls._db_execute(query=query)
        return result[0][0]
