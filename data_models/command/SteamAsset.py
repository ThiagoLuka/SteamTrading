from .BasePersistenceModel import BasePersistenceModel


class SteamAsset(BasePersistenceModel, name='steam_asset'):

    def save(self, source: str, **kwargs):
        if   source == 'inventory':
            self._load_standard(user_id=kwargs['user_id'])
        elif source == 'market_item_page':
            self._set_origin_price_from_buy_order_update(
                user_id=kwargs['user_id'],
                item_id=kwargs['item_id'],
                new_quantity=kwargs['buy_order_new_quantity'],
            )

    @staticmethod
    def table_name(table_type: str) -> str:
        return {
            'public': 'public.steam_asset',
            'staging': 'staging.steam_asset',
        }.get(table_type, '')

    def _load_standard(self, user_id: int) -> None:
        self._df['user_id'] = user_id
        self._df.drop_duplicates(subset=['steam_asset_id', 'user_id'], inplace=True)
        self._insert_into_staging(df=self._df, staging_table_name=self.table_name(table_type='staging'))
        query = self._upsert_all_assets_query()
        self._db_execute(query=query)

    def _set_origin_price_from_buy_order_update(self, user_id: int, item_id: int, new_quantity: int) -> None:
        query = self._set_origin_price_from_buy_order_query(user_id=user_id, item_id=item_id, new_quantity=new_quantity)
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
        	    ON pa.user_id = sa.user_id AND pa.steam_asset_id = sa.steam_asset_id
        	WHERE pa.active AND sa.created_at IS NULL
        	)
        UPDATE {public_table} pa
        SET 
              removed_at = to_remove.removed_at
            , active = False
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
        	  is2.id AS item_id
        	, sa.user_id AS user_id
        	, sa.steam_asset_id AS steam_asset_id
        	, sa.marketable AS marketable 
        	, sa.tradable AS tradable
        	, True AS active
        	, sa.created_at AS created_at
        FROM {staging_table} sa
        LEFT JOIN {public_item_description_table} isd ON sa.class_id = isd.class_id 
        LEFT JOIN {public_item_table} is2 ON isd.item_id = is2.id;
        
        -- deleting from tmp_staging those that doesnt need upserting
        DELETE FROM tmp_staging sa
        USING {public_table} pa
        WHERE
        	sa.item_id = pa.item_id
        	AND sa.steam_asset_id = pa.steam_asset_id
        	AND sa.user_id = pa.user_id
        	AND sa.marketable = pa.marketable
        	AND sa.tradable = pa.tradable
        	AND sa.active = pa.active;
        
        -- upserting new assets
        INSERT INTO {public_table} (
        	  item_id
        	, user_id
        	, steam_asset_id
        	, active
        	, marketable
        	, tradable
        	, origin
        	, origin_price
        	, destination
        	, destination_price
        	, created_at
        	, removed_at
        )
        SELECT
        	  item_id
        	, user_id
        	, steam_asset_id
        	, True AS active
        	, marketable
        	, tradable
        	, 'Undefined' AS origin
        	, 0 AS origin_price
        	, 'Unknown' AS destination
        	, 0 AS destination_price
        	, created_at
        	, NULL AS removed_at
        FROM tmp_staging
        ON CONFLICT (user_id, steam_asset_id)
        DO UPDATE
        SET
        	item_id = EXCLUDED.item_id,
        	active = EXCLUDED.active,
        	marketable = EXCLUDED.marketable,
        	tradable = EXCLUDED.tradable,
        	created_at = {public_table}.created_at,
        	removed_at = EXCLUDED.removed_at;
        
        DROP TABLE tmp_staging;
        """

    def _set_origin_price_from_buy_order_query(
        self,
        user_id: int,
        item_id: int,
        new_quantity: int
    ) -> str:
        public = self.table_name(table_type='public')
        public_buy_order = self.models['buy_order'].table_name(table_type='public')
        return f"""
        WITH
        	old_buy_order AS (
        		SELECT price, qtd_current
        		FROM {public_buy_order} bo 
        		WHERE 
        			user_id = {user_id}
        			AND item_id = {item_id}
        		ORDER BY created_at DESC 
        		LIMIT 1
        	),
        	assets_to_update AS (
        		SELECT sa.id
        		FROM {public} sa 
        		WHERE
        			user_id = {user_id}
        			AND item_id = {item_id}
        			AND origin = 'Undefined'
        		ORDER BY created_at DESC
        		LIMIT (SELECT qtd_current FROM old_buy_order) - {new_quantity}
        	)
        UPDATE {public} sa
        SET
        	  origin = 'Buy Order'
        	, origin_price = (SELECT price FROM old_buy_order)
        FROM assets_to_update
        WHERE sa.id = assets_to_update.id;
        """