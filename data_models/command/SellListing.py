from .BasePersistenceModel import BasePersistenceModel


class SellListing(BasePersistenceModel, name='sell_listing'):

    def save(self, source: str, **kwargs) -> None:
        if   source == 'main_market_page':
            self._load_standard(user_id=kwargs['user_id'])
        elif source == 'remove_sell_listing':
            self._set_to_inactive(steam_sell_listing_id=kwargs['steam_sell_listing_id'])

    @staticmethod
    def table_name(table_type: str) -> str:
        return {
            'public': 'public.sell_listing',
            'staging': 'staging.sell_listing',
        }.get(table_type, '')

    def _load_standard(self, user_id: int):
        self._df['user_id'] = user_id
        self._df.drop_duplicates(subset='steam_sell_listing_id', inplace=True)
        self._insert_into_staging(df=self._df, staging_table_name=self.table_name(table_type='staging'))
        query = self._upsert_sell_listings_query()
        self._db_execute(query=query)

    def _set_to_inactive(self, steam_sell_listing_id: str) -> None:
        public = self.table_name(table_type='public')
        query = f"""
        UPDATE {public} sl
        SET
              active = False
            , conclusion = 'Canceled'
            , removed_at = NOW()::TIMESTAMP
        WHERE
            steam_sell_listing_id = '{steam_sell_listing_id}';
        """
        self._db_execute(query=query)

    def _upsert_sell_listings_query(self) -> str:
        public = self.table_name(table_type='public')
        staging = self.table_name(table_type='staging')
        inventory_table_name = self.models['steam_asset'].table_name(table_type='public')
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
            	  active = False
            	, conclusion = 'Vanished'
            	, removed_at = NOW()::TIMESTAMP
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
	              game_id
	            , item_id
	            , asset_id
	            , user_id
	            , steam_sell_listing_id
	            , active 
	            , price_buyer  
	            , price_to_receive  
	            , conclusion  
	            , steam_created_at  
	            , created_at  
	            , removed_at 
            )
            SELECT
	              isa.game_id
	            , isa.item_id
	            , isa.id AS asset_id
	            , isa.user_id
	            , ssl.steam_sell_listing_id
	            , True AS active  
	            , ssl.price_buyer  
	            , ssl.price_to_receive  
	            , 'Undefined' AS conclusion  
	            , ssl.steam_created_at  
	            , ssl.created_at  
	            , NULL AS removed_at 
            FROM {staging} ssl
            INNER JOIN {inventory_table_name} isa ON
                isa.user_id = ssl.user_id
                AND isa.steam_asset_id = ssl.steam_asset_id
            ON CONFLICT (steam_sell_listing_id)
            DO UPDATE
            SET
            	  active = True
            	, conclusion = 'Undefined'
            	, removed_at = NULL;
            
            TRUNCATE TABLE {staging}; 
            
            COMMIT;
        """