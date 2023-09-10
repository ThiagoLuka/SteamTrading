import pandas as pd

from data_models.PandasUtils import PandasUtils
from repositories.QueryBuilderPG import QueryBuilderPG
from db.DBController import DBController


class SellListing:

    def __init__(self, data: list[dict]):
        self._df = pd.DataFrame(data)

    @property
    def df(self) -> pd.DataFrame:
        return self._df.copy()

    def save(self, user_id: int) -> None:
        self._df['user_id'] = user_id
        self._df.drop_duplicates(subset='steam_sell_listing_id', inplace=True)
        self._insert_into_staging(self._df, self._staging_table_name)
        self._transfer_staging_to_public()

    @property
    def _staging_table_name(self) -> str:
        return 'staging.sell_listing'

    @property
    def _public_table_columns(self) -> list:
        return ['steam_sell_listing_id', 'asset_id', 'user_id', 'active', 'price_buyer', 'price_to_receive',
                'steam_created_at', 'created_at', 'removed_at']

    @staticmethod
    def _insert_into_staging(df, staging_table_name) -> None:
        cols_to_insert = list(df.columns)
        zipped_data = PandasUtils.zip_df_columns(df, cols_to_insert)
        values = QueryBuilderPG.unzip_to_query_values_str(zipped_data)
        query = f"""
            INSERT INTO {staging_table_name}
            ({', '.join(cols_to_insert)})
            VALUES {values};
        """
        DBController.execute(query=query)

    def _transfer_staging_to_public(self) -> None:
        query = f"""
            BEGIN TRANSACTION;
            
            -- inactivating those not present in staging
            WITH to_inactivate AS (
            	SELECT id
            	FROM public.sell_listing psl 
            	LEFT JOIN staging.sell_listing ssl
            	ON psl.steam_sell_listing_id = ssl.steam_sell_listing_id
            	WHERE
            		active
            		AND ssl.steam_sell_listing_id IS NULL
            	)
            UPDATE public.sell_listing psl 
            SET
            	active = False,
            	removed_at = NOW()::TIMESTAMP
            FROM to_inactivate
            WHERE psl.id = to_inactivate.id;
            
            -- removing from staging those active in prod
            DELETE FROM staging.sell_listing ssl
            USING public.sell_listing psl
            WHERE 
            	ssl.steam_sell_listing_id = psl.steam_sell_listing_id
            	AND psl.active;
            
            -- upserting staging to prod
            INSERT INTO public.sell_listing ({', '.join(self._public_table_columns)})
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
            FROM staging.sell_listing ssl
            LEFT JOIN public.item_steam_assets isa ON isa.asset_id = ssl.steam_asset_id
            ON CONFLICT (steam_sell_listing_id)
            DO UPDATE SET
            	active = True,
            	removed_at = NULL;
            
            TRUNCATE TABLE staging.sell_listing; 
            
            COMMIT;
        """
        DBController.execute(query=query)