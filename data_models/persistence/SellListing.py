from .BasePersistenceModel import BasePersistenceModel


class SellListing(BasePersistenceModel, name='sell_listing'):

    def save(self, user_id: int) -> None:
        self._df['user_id'] = user_id
        self._df.drop_duplicates(subset='steam_sell_listing_id', inplace=True)
        self._insert_into_staging(df=self._df, staging_table_name=self.table_name(table_type='staging'))
        self._transfer_staging_to_public()

    @staticmethod
    def table_name(table_type: str) -> str:
        return {
            'public': 'public.sell_listing',
            'staging': 'staging.sell_listing',
        }.get(table_type, '')

    @staticmethod
    def table_columns(table_type: str) -> list:
        return {
            'public': [
                'id', 'steam_sell_listing_id', 'asset_id', 'user_id', 'active', 'price_buyer', 'price_to_receive',
                'steam_created_at', 'created_at', 'removed_at'
            ],
            'staging': [
                'steam_sell_listing_id', 'steam_asset_id', 'user_id', 'price_buyer', 'price_to_receive',
                'steam_created_at', 'created_at'
            ],
        }.get(table_type, [])

    def _transfer_staging_to_public(self) -> None:
        query = self._upsert_sell_listings_query()
        self._db_execute(query=query)

    def _upsert_sell_listings_query(self):
        public = self.table_name(table_type='public')
        staging = self.table_name(table_type='staging')
        return f"""
            BEGIN TRANSACTION;
            
            -- inactivating those not present in staging
            WITH to_inactivate AS (
            	SELECT id
            	FROM {public} psl 
            	LEFT JOIN {staging} ssl
            	ON psl.steam_sell_listing_id = ssl.steam_sell_listing_id
            	WHERE
            		active
            		AND ssl.steam_sell_listing_id IS NULL
            	)
            UPDATE {public} psl 
            SET
            	active = False,
            	removed_at = NOW()::TIMESTAMP
            FROM to_inactivate
            WHERE psl.id = to_inactivate.id;
            
            -- removing from staging those active in prod
            DELETE FROM {staging} ssl
            USING {public} psl
            WHERE 
            	ssl.steam_sell_listing_id = psl.steam_sell_listing_id
            	AND psl.active;
            
            -- upserting staging to prod
            INSERT INTO {public} (
                  steam_sell_listing_id
                , asset_id
                , user_id
                , active
                , price_buyer
                , price_to_receive
                , steam_created_at
                , created_at
                , removed_at
            )
            SELECT
	            ssl.steam_sell_listing_id,
	            isa.id AS asset_id,
	            ssl.user_id,
	            True AS active,
	            ssl.price_buyer,
	            ssl.price_to_receive,
	            ssl.steam_created_at,
	            ssl.created_at,
	            NULL AS removed_at
            FROM {staging} ssl
            LEFT JOIN public.item_steam_assets isa ON isa.asset_id = ssl.steam_asset_id
            ON CONFLICT (steam_sell_listing_id)
            DO UPDATE
            SET
            	active = True,
            	removed_at = NULL;
            
            TRUNCATE TABLE {staging}; 
            
            COMMIT;
        """