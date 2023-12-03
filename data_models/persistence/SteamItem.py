from .BasePersistenceModel import BasePersistenceModel


class SteamItem(BasePersistenceModel, name='steam_item'):

    def save(self, update_item_name: bool = True) -> None:
        self._df.drop_duplicates(subset=['game_market_id', 'market_url_name'], inplace=True)
        self._insert_into_staging(df=self._df, staging_table_name=self.table_name(table_type='staging'))
        self._transfer_staging_to_public(update_item_name=update_item_name)

    @staticmethod
    def table_name(table_type: str) -> str:
        return {
            'public': 'public.items_steam',
            'staging': 'staging.steam_item',
            'item_type': 'public.item_steam_types',
            'description': 'public.item_steam_descriptions',
        }.get(table_type, '')

    @staticmethod
    def table_columns(table_type: str) -> list:
        return {
            'public': ['id', 'game_id', 'item_steam_type_id', 'name', 'market_url_name'],
            'staging': [
                'game_market_id', 'market_url_name', 'name', 'steam_item_type_id', 'steam_item_type_name', 'class_id'
            ],
            'item_type': ['id', 'name'],
            'description': ['item_steam_id', 'class_id'],
        }.get(table_type, [])

    def _transfer_staging_to_public(self, update_item_name: bool) -> None:
        query = self._upsert_item_full_query(update_item_name=update_item_name)
        self._db_execute(query=query)

    def _upsert_item_full_query(self, update_item_name: bool) -> str:
        public = self.table_name(table_type='public')
        staging = self.table_name(table_type='staging')
        public_item_type = self.table_name(table_type='item_type')
        public_description = self.table_name(table_type='description')
        public_game = self.models['game'].table_name(table_type='public')
        return f"""
        BEGIN TRANSACTION;
            
        {self._upsert_item_types_query(
            staging_table=staging,
            public_item_type_table=public_item_type,
        )}

        {self._upsert_items_query(
            staging_table=staging,
            public_table=public,
            public_game_table=public_game,
            update_item_name=update_item_name,
        )}
        
        {self._insert_item_descriptions_query(
            staging_table=staging,
            public_table=public,
            public_game_table=public_game,
            public_description_table=public_description,
        )}
        
        TRUNCATE TABLE {staging}; 
        
        COMMIT;
        """

    @staticmethod
    def _upsert_item_types_query(
        staging_table: str,
        public_item_type_table: str
    ) -> str:
        return f"""
        -- upserting item types
        INSERT INTO {public_item_type_table} (
              id
            , name
        )
        SELECT
              DISTINCT(steam_item_type_id) AS id
            , steam_item_type_name AS name
        FROM {staging_table} s
        LEFT JOIN {public_item_type_table} p
        ON s.steam_item_type_id = p.id AND s.steam_item_type_name = p.name
        WHERE p.id IS NULL
        ON CONFLICT (id)
        DO UPDATE SET name = EXCLUDED.name;
        """

    @staticmethod
    def _upsert_items_query(
        staging_table: str,
        public_table: str,
        public_game_table: str,
        update_item_name: bool
    ) -> str:
        update_item_name_clause = 'AND pgmi.item_name = s.name' if update_item_name else ''
        return f"""
        CREATE TEMPORARY TABLE tmp_staging AS
        SELECT * FROM {staging_table};
        
        -- deleting from staging items that doesnt need upserting
        WITH public_with_game_market_id AS (
        	SELECT
        		g.market_id AS game_market_id,
        		is2.market_url_name AS item_market_url_name,
        		is2.name as item_name
        	FROM {public_table} is2 
        	INNER JOIN {public_game_table} g ON g.id = is2.game_id
        )
        DELETE FROM tmp_staging s
        USING public_with_game_market_id pgmi
        WHERE
        	pgmi.game_market_id = s.game_market_id 
        	AND pgmi.item_market_url_name = s.market_url_name
        	{update_item_name_clause};
        
        -- upserting new items
        INSERT INTO {public_table} (
              game_id
            , item_steam_type_id
            , name
            , market_url_name
        )
        SELECT
              g.id AS game_id
            , steam_item_type_id
            , s.name
            , market_url_name
        FROM tmp_staging s
        INNER JOIN {public_game_table} g ON s.game_market_id = g.market_id
        ON CONFLICT (game_id, market_url_name)
        DO UPDATE
        SET
            item_steam_type_id = EXCLUDED.item_steam_type_id,
            name = EXCLUDED.name;
        
        DROP TABLE tmp_staging;
        """

    @staticmethod
    def _insert_item_descriptions_query(
        staging_table: str,
        public_table: str,
        public_game_table: str,
        public_description_table: str
    ) -> str:
        return f"""
        CREATE TEMPORARY TABLE tmp_staging AS
        SELECT * FROM {staging_table};
        
        -- deleting from staging items with description already saved
        DELETE FROM tmp_staging s
        USING {public_description_table} pd
        WHERE s.class_id = pd.class_id;
        
        -- inserting new descriptions
        WITH staging_with_steam_item_id AS (
            SELECT p.id AS steam_item_id, s.*
            FROM tmp_staging s
            INNER JOIN {public_game_table} g ON s.game_market_id = g.market_id
            INNER JOIN {public_table} p
                ON p.game_id = g.id AND s.market_url_name = p.market_url_name
        )
        INSERT INTO {public_description_table} (
              item_steam_id
            , class_id
        )
        SELECT
              steam_item_id
            , class_id
        FROM staging_with_steam_item_id;
        
        DROP TABLE tmp_staging;
        """
