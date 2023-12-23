from .BasePersistenceModel import BasePersistenceModel


class SteamBadge(BasePersistenceModel, name='steam_badge'):

    def save(self, source: str, **kwargs) -> None:
        if source == 'profile_badge':
            self._load_standard(user_id=kwargs['user_id'])

    @staticmethod
    def table_name(table_type: str) -> str:
        return {
            'staging': 'staging.steam_badge',
            'public_game_badge': 'public.game_badges',
            'public_pure_badge': 'public.pure_badges',
            'public_user_badge': 'public.user_badges',
        }.get(table_type, '')

    def _load_standard(self, user_id: int):
        self._df['user_id'] = user_id
        self._insert_into_staging(df=self._df, staging_table_name=self.table_name(table_type='staging'))
        query = self._upsert_badge_full_query()
        self._db_execute(query=query)

    def _upsert_badge_full_query(self) -> str:
        staging = self.table_name(table_type='staging')
        game_badge = self.table_name(table_type='public_game_badge')
        pure_badge = self.table_name(table_type='public_pure_badge')
        user_badge = self.table_name(table_type='public_user_badge')
        public_game = self.models['game'].table_name(table_type='public')
        return f"""
        BEGIN TRANSACTION;
        
        {self._insert_game_badge(
            staging_table=staging,
            public_game_badges_table=game_badge,
            public_game_table=public_game,
        )}
        
        {self._upsert_user_badge_with_game_badge(
            staging_table=staging,
            public_user_badges_table=user_badge,
            public_game_badges_table=game_badge,
            public_game_table=public_game,
        )}
        
        {self._insert_pure_badge(
            staging_table=staging,
            public_pure_badges_table=pure_badge,
        )}
        
        {self._update_user_badge_with_pure_badge(
            staging_table=staging,
            public_pure_badges_table=pure_badge,
            public_user_badges_table=user_badge,
        )}
        
        TRUNCATE TABLE {staging}; 
        
        COMMIT;
        """

    @staticmethod
    def _insert_game_badge(
        staging_table: str,
        public_game_badges_table: str,
        public_game_table: str
    ) -> str:
        return f"""
        CREATE TEMPORARY TABLE tmp_staging AS 
        SELECT 
        	  g.id AS game_id
        	, sb."name" 
        	, REPLACE(sb.level, '.0', '')::INT AS level
        	, sb.foil
        FROM {staging_table} sb 
        INNER JOIN {public_game_table} g ON g.market_id = sb.game_market_id;
        
        -- deleting from staging items that doesnt need inserting
        DELETE FROM tmp_staging s
        USING {public_game_badges_table} gb
        WHERE 
        	s.game_id = gb.game_id
        	AND s.level = gb.level
        	AND s.foil = gb.foil;
        
        -- inserting new badges
        INSERT INTO {public_game_badges_table} (
        	game_id, "name", "level", foil
        )
        SELECT
        	game_id, "name", "level", foil
        FROM tmp_staging;
        
        DROP TABLE tmp_staging;
        """

    @staticmethod
    def _upsert_user_badge_with_game_badge(
        staging_table: str,
        public_user_badges_table: str,
        public_game_badges_table: str,
        public_game_table: str
    ) -> str:
        return f"""
        CREATE TEMPORARY TABLE tmp_staging AS
        SELECT 
        	  s.user_id AS user_id 
        	, gb.id AS game_badge_id
        	, s.experience
        	, s.unlocked_at
        FROM {staging_table} s
        INNER JOIN {public_game_table} g ON g.market_id = s.game_market_id
        INNER JOIN {public_game_badges_table} gb ON
        	g.id = gb.game_id AND s.foil = gb.foil AND REPLACE(s.level, '.0', '')::INT = gb."level";
        
        -- set to inactive those not present in staging
        WITH active_user_game_badges_not_in_staging AS (
        	SELECT id
        	FROM {public_user_badges_table} ub
        	LEFT JOIN tmp_staging s
        		ON ub.user_id = s.user_id AND ub.game_badge_id = s.game_badge_id
        	WHERE
        		s.user_id IS NULL
        		AND ub.pure_badge_id IS NULL
        		AND ub.active
        )
        UPDATE {public_user_badges_table} ub
        SET active = False
        FROM active_user_game_badges_not_in_staging ans
        WHERE ub.id = ans.id;
        
        -- deleting from staging items that doesnt need upserting
        DELETE FROM tmp_staging s
        USING {public_user_badges_table} ub
        WHERE
        	s.user_id = ub.user_id
        	AND s.game_badge_id = ub.game_badge_id;
        
        -- inserting user_game_badges in user_badges
        INSERT INTO {public_user_badges_table} (
        	  user_id
        	, game_badge_id
        	, pure_badge_id
        	, experience
        	, unlocked_at
        	, active
        )
        SELECT
        	  user_id
        	, game_badge_id
        	, NULL AS pure_badge_id
        	, experience
        	, unlocked_at
        	, True AS active
        FROM tmp_staging s;
        
        DROP TABLE tmp_staging;
        """

    @staticmethod
    def _insert_pure_badge(
        staging_table: str,
        public_pure_badges_table: str,
    ) -> str:
        return f"""
        CREATE TEMPORARY TABLE tmp_staging AS 
        SELECT 
        	  REPLACE(pure_badge_page_id, '.0', '')::INT AS page_id
        	, sb."name"
        FROM {staging_table} sb
        WHERE sb.pure_badge_page_id IS NOT NULL;
        
        -- deleting from staging items that doesnt need inserting
        DELETE FROM tmp_staging s
        USING {public_pure_badges_table} pb
        WHERE s.page_id = pb.page_id;
        
        -- inserting new badges
        INSERT INTO {public_pure_badges_table} (
        	page_id, "name"
        )
        SELECT
        	page_id, "name"
        FROM tmp_staging;
        
        DROP TABLE tmp_staging;
        """

    @staticmethod
    def _update_user_badge_with_pure_badge(
        staging_table: str,
        public_pure_badges_table: str,
        public_user_badges_table: str,
    ) -> str:
        return f"""
        CREATE TEMPORARY TABLE tmp_staging AS 
        SELECT 
        	  s.user_id AS user_id 
        	, pb.id AS pure_badge_id 
        	, s.experience
        	, s.unlocked_at
        FROM {staging_table} s
        INNER JOIN {public_pure_badges_table} pb
        	ON pb.page_id = REPLACE(s.pure_badge_page_id, '.0', '')::INT ;
        
        -- deleting from staging items that doesnt need inserting
        DELETE FROM tmp_staging s
        USING {public_user_badges_table} ub
        WHERE
        	s.user_id = ub.user_id
        	AND s.pure_badge_id = ub.pure_badge_id
        	AND s.experience = ub.experience
        	AND s.unlocked_at = ub.unlocked_at;
        
        -- updating pure badges in user_badge
        UPDATE {public_user_badges_table} ub
        SET	
        	experience = s.experience,
        	unlocked_at = s.unlocked_at 
        FROM tmp_staging s
        WHERE
        	s.user_id = ub.user_id
        	AND s.pure_badge_id = ub.pure_badge_id;
        
        DROP TABLE tmp_staging;
        """
