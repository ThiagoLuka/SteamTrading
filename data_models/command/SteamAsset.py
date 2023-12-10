from .BasePersistenceModel import BasePersistenceModel


class SteamAsset(BasePersistenceModel, name='steam_asset'):

    def save(self, user_id: int):
        self._df['user_id'] = user_id
        self._df.drop_duplicates(subset=['asset_id', 'user_id'], inplace=True)
        self._insert_into_staging(df=self._df, staging_table_name=self.table_name(table_type='staging'))
        self._transfer_staging_to_public()

    @staticmethod
    def table_name(table_type: str) -> str:
        return {
            'public': 'public.item_steam_assets',
            'staging': 'staging.steam_asset',
        }.get(table_type, '')

    @staticmethod
    def table_columns(table_type: str) -> list:
        return {
            'public': ['id', 'item_steam_id', 'user_id', 'asset_id', 'marketable', 'created_at', 'removed_at'],
            'staging': ['class_id', 'user_id', 'asset_id', 'marketable'],
        }.get(table_type, [])

    def _transfer_staging_to_public(self) -> None:
        query = self._upsert_all_assets_query()
        self._db_execute(query=query)

    def _upsert_all_assets_query(self) -> str:
        public = self.table_name(table_type='public')
        staging = self.table_name(table_type='staging')
        public_item = self.models['steam_item'].table_name(table_type='public')
        public_item_description = self.models['steam_item'].table_name(table_type='description')
        return f"""
        BEGIN TRANSACTION;
        
        {self._update_removed_assets_query(
            staging_table=staging,
            public_table=public,
        )}
        
        {self._upsert_new_assets_query(
            staging_table=staging,
            public_table=public,
            public_item_table=public_item,
            public_item_description_table=public_item_description,
        )}
        
        TRUNCATE TABLE {staging};
        
        COMMIT;
        """

    @staticmethod
    def _update_removed_assets_query(
        staging_table: str,
        public_table: str
    ) -> str:
        return f"""
        -- setting removed_at for those not present in staging anymore
        WITH asset_id_no_longer_in_staging AS (
        	SELECT
        		  pa.id
        		, (SELECT created_at 
        		  FROM staging.steam_asset sa
        		  LIMIT 1) AS removed_at
        	FROM {public_table} pa
        	LEFT JOIN {staging_table} sa
        	ON pa.user_id = sa.user_id AND pa.asset_id = sa.asset_id
        	WHERE
        	    pa.removed_at IS NULL
        	    AND sa.created_at IS NULL
        	)
        UPDATE {public_table} pa
        SET removed_at = to_remove.removed_at
        FROM asset_id_no_longer_in_staging to_remove
        WHERE pa.id = to_remove.id;
        """

    @staticmethod
    def _upsert_new_assets_query(
        staging_table: str,
        public_table: str,
        public_item_table: str,
        public_item_description_table: str,
    ) -> str:
        return f"""
        CREATE TEMP TABLE tmp_staging AS
        SELECT
        	  is2.id AS steam_item_id
        	, sa.user_id AS user_id
        	, sa.asset_id AS asset_id
        	, sa.marketable AS marketable 
        	, True AS active
        	, sa.created_at AS created_at
        FROM {staging_table} sa
        LEFT JOIN {public_item_description_table} isd ON sa.class_id = isd.class_id 
        LEFT JOIN {public_item_table} is2 ON isd.item_steam_id = is2.id;
        
        -- deleting from tmp_staging those that doesnt need upserting
        WITH public_with_active_field AS (
        	SELECT
        		pa.*,
        		CASE 
        			WHEN pa.removed_at IS NULL THEN True
        			ELSE False
        		END AS active
        		FROM {public_table} pa
        )
        DELETE FROM tmp_staging sa
        USING public_with_active_field pa
        WHERE
        	sa.steam_item_id = pa.item_steam_id
        	AND sa.asset_id = pa.asset_id
        	AND sa.user_id = pa.user_id
        	AND sa.marketable = pa.marketable
        	AND sa.active = pa.active;
        
        -- upserting new assets
        INSERT INTO {public_table} (
        	  item_steam_id
        	, user_id
        	, asset_id
        	, marketable
        	, created_at
        	, removed_at
        )
        SELECT
        	  steam_item_id
        	, user_id
        	, asset_id
        	, marketable
        	, created_at
        	, NULL AS removed_at
        FROM tmp_staging
        ON CONFLICT (user_id, asset_id)
        DO UPDATE
        SET
        	item_steam_id = EXCLUDED.item_steam_id,
        	marketable = EXCLUDED.marketable,
        	created_at = {public_table}.created_at,
        	removed_at = EXCLUDED.removed_at;
        
        DROP TABLE tmp_staging;
        """