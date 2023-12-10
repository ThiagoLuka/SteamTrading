from .BasePersistenceModel import BasePersistenceModel


class SteamItem(BasePersistenceModel, name='steam_item'):

    def save(self, source: str) -> None:
        persist_method = {
            'inventory': self._load_from_inventory,
            'profile_game_cards': self._load_from_profile_game_cards
        }.get(source)
        persist_method()

    @staticmethod
    def table_name(table_type: str) -> str:
        return {
            'public': 'public.items_steam',
            'staging_inventory': 'staging.steam_item_from_inventory',
            'staging_profile_game_cards': 'staging.steam_item_from_profile_game_cards',
            'item_type': 'public.item_steam_types',
            'description': 'public.item_steam_descriptions',
            'trading_card': 'public.item_trading_cards',
        }.get(table_type, '')

    @staticmethod
    def table_columns(table_type: str) -> list:
        return {
            'public': ['id', 'game_id', 'item_steam_type_id', 'name', 'market_url_name'],
            'staging_inventory': ['game_market_id', 'market_url_name', 'name', 'steam_item_type_id', 'steam_item_type_name', 'class_id'],
            'staging_profile_game_cards': ['game_market_id', 'market_url_name', 'name', 'steam_item_type_id', 'set_number', 'foil'],
            'item_type': ['id', 'name'],
            'description': ['item_steam_id', 'class_id'],
            'trading_card': ['id', 'item_steam_id', 'game_id', 'set_number', 'foil'],
        }.get(table_type, [])

    def _load_from_inventory(self) -> None:
        self._df.drop_duplicates(subset=['game_market_id', 'market_url_name'], inplace=True)
        self._insert_into_staging(df=self._df, staging_table_name=self.table_name(table_type='staging_inventory'))
        query = self._upsert_from_inventory_full_query()
        self._db_execute(query=query)

    def _load_from_profile_game_cards(self) -> None:
        self._df.drop_duplicates(subset=['game_market_id', 'market_url_name'], inplace=True)
        self._insert_into_staging(df=self._df, staging_table_name=self.table_name(table_type='staging_profile_game_cards'))
        query = self._upsert_from_profile_game_cards_full_query()
        self._db_execute(query=query)

    def _upsert_from_inventory_full_query(self) -> str:
        public = self.table_name(table_type='public')
        staging = self.table_name(table_type='staging_inventory')
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
            update_item_name=True,
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

    def _upsert_from_profile_game_cards_full_query(self) -> str:
        public = self.table_name(table_type='public')
        staging = self.table_name(table_type='staging_profile_game_cards')
        public_trading_card = self.table_name(table_type='trading_card')
        public_game = self.models['game'].table_name(table_type='public')
        return f"""
        BEGIN TRANSACTION;
        
        {self._upsert_items_query(
            staging_table=staging,
            public_table=public,
            public_game_table=public_game,
            update_item_name=False,
        )}
        
        {self._insert_trading_card(
            staging_table=staging,
            public_table=public_trading_card,
            public_game_table=public_game,
            public_item_table=public,
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

    @staticmethod
    def _insert_trading_card(
        staging_table: str,
        public_table: str,
        public_item_table: str,
        public_game_table: str,
    ) -> str:
        return f"""
        INSERT INTO {public_table} (
        	  item_steam_id
        	, game_id 
        	, set_number 
        	, foil
        )
        SELECT
        	  is2.id AS item_steam_id
        	, g.id AS game_id
        	, s.set_number AS set_number
        	, s.foil AS foil
        FROM {staging_table} s
        INNER JOIN {public_game_table} g ON g.market_id = s.game_market_id
        INNER JOIN {public_item_table} is2
        	ON is2.game_id = g.id AND is2.market_url_name = s.market_url_name
       	WHERE set_number != 0;
        """