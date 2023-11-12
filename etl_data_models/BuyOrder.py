import pandas as pd

from data_models.PandasUtils import PandasUtils
from repositories.QueryBuilderPG import QueryBuilderPG
from db.DBController import DBController


class BuyOrder:

    def __init__(self, data: list[dict]):
        self._df = pd.DataFrame(data)

    @property
    def df(self) -> pd.DataFrame:
        return self._df.copy()

    def save(self, user_id: int, empty_buy_order: bool = False) -> None:
        self._df['user_id'] = user_id
        self._insert_into_staging(self._df, self._staging_table_name)
        self._transfer_staging_to_public(empty_buy_order=empty_buy_order)

    @property
    def _staging_table_name(self) -> str:
        return 'staging.buy_order'

    @property
    def _staging_table_columns(self) -> list:
        return ['steam_buy_order_id', 'item_id', 'user_id', 'price', 'quantity']

    @property
    def _public_table_name(self) -> str:
        return 'public.buy_orders'

    @property
    def _public_table_columns(self) -> list:
        return ['buy_order_id', 'steam_buy_order_id', 'user_id', 'item_steam_id', 'active', 'price',
                'qtd_start', 'qtd_estimate', 'qtd_current', 'created_at', 'updated_at', 'removed_at']

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

    def _transfer_staging_to_public(self, empty_buy_order: bool) -> None:
        if empty_buy_order:
            query = self._empty_buy_order_query()
        else:
            query = self._upsert_buy_order_query()
        DBController.execute(query=query)

    @staticmethod
    def _empty_buy_order_query() -> str:
        return f"""
            BEGIN TRANSACTION;
            WITH
            	id_to_inactivate AS (
            		SELECT buy_order_id AS id FROM buy_orders
                    WHERE
                        (item_steam_id, user_id) = (SELECT item_id, user_id FROM staging.buy_order)
                        AND active
                    ORDER BY created_at DESC
                    LIMIT 1
            	)
            UPDATE public.buy_orders
            SET
            	  active = False
            	, qtd_estimate = 0
            	, qtd_current = 0
            	, updated_at = NOW()::TIMESTAMP
            	, removed_at = NOW()::TIMESTAMP
            WHERE public.buy_orders.buy_order_id = (SELECT id FROM id_to_inactivate);
            TRUNCATE TABLE staging.buy_order;
            COMMIT;
        """

    @staticmethod
    def _upsert_buy_order_query() -> str:
        return f"""
            BEGIN TRANSACTION;
            INSERT INTO public.buy_orders (
                  steam_buy_order_id
                , user_id
                , item_steam_id
                , active
                , price
                , qtd_start
                , qtd_estimate
                , qtd_current
                , created_at
                , updated_at
                , removed_at
            )
            SELECT 
            	steam_buy_order_id,
            	user_id,
            	item_id,
            	True AS active,
            	price,
            	quantity AS qtd_start,
            	quantity AS qtd_estimate,
            	quantity AS qtd_current,
            	NOW()::TIMESTAMP AS created_at,
            	NOW()::TIMESTAMP AS updated_at,
            	NULL AS removed_at
            FROM staging.buy_order 
            ON CONFLICT (steam_buy_order_id)
            DO UPDATE
            SET
            	  user_id = buy_orders.user_id
            	, item_steam_id = buy_orders.item_steam_id
            	, active = True
            	, price = buy_orders.price
            	, qtd_start = buy_orders.qtd_start
            	, qtd_estimate = EXCLUDED.qtd_estimate
            	, qtd_current = EXCLUDED.qtd_estimate
            	, created_at = buy_orders.created_at
            	, updated_at = NOW()::TIMESTAMP
            	, removed_at = NULL
            ;
            TRUNCATE TABLE staging.buy_order;
            COMMIT;
        """
