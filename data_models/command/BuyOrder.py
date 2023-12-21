from .BasePersistenceModel import BasePersistenceModel


class BuyOrder(BasePersistenceModel, name='buy_order'):

    def save(self, user_id: int, empty_buy_order: bool = False) -> None:
        self._df['user_id'] = user_id
        self._insert_into_staging(df=self._df, staging_table_name=self.table_name(table_type='staging'))
        self._transfer_staging_to_public(empty_buy_order=empty_buy_order)

    @staticmethod
    def table_name(table_type: str) -> str:
        return {
            'public': 'public.buy_order',
            'staging': 'staging.buy_order',
        }.get(table_type, '')

    @staticmethod
    def table_columns(table_type: str) -> list:
        return {
            'public': [
                'buy_order_id', 'steam_buy_order_id', 'user_id', 'item_steam_id', 'active', 'price',
                'qtd_start', 'qtd_estimate', 'qtd_current', 'created_at', 'updated_at', 'removed_at'
            ],
            'staging': ['steam_buy_order_id', 'item_id', 'user_id', 'price', 'quantity', 'created_at'],
        }.get(table_type, [])

    def _transfer_staging_to_public(self, empty_buy_order: bool) -> None:
        if empty_buy_order:
            query = self._empty_buy_order_query()
        else:
            query = self._upsert_buy_order_query()
        self._db_execute(query=query)

    def _empty_buy_order_query(self) -> str:
        public = self.table_name(table_type='public')
        staging = self.table_name(table_type='staging')
        return f"""
            BEGIN TRANSACTION;
            
            UPDATE {public} pbo
            SET
            	  active = False
            	, qtd_current = 0
            	, updated_at = s.created_at
            	, removed_at = s.created_at
            FROM {staging} s
            WHERE 
                pbo.active
                AND pbo.item_id = s.item_id
                AND pbo.user_id = s.user_id;
            
            TRUNCATE TABLE {staging};
            COMMIT;
        """

    def _upsert_buy_order_query(self) -> str:
        public = self.table_name(table_type='public')
        staging = self.table_name(table_type='staging')
        return f"""
            BEGIN TRANSACTION;
            
            INSERT INTO {public} (
                  steam_buy_order_id
                , user_id
                , item_id
                , active
                , price
                , qtd_start
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
            	quantity AS qtd_current,
            	created_at AS created_at,
            	created_at AS updated_at,
            	NULL AS removed_at
            FROM {staging} s
            ON CONFLICT (steam_buy_order_id)
            DO UPDATE
            SET
            	  active = True
            	, qtd_current = EXCLUDED.qtd_current
            	, updated_at = EXCLUDED.created_at
            	, removed_at = NULL
            ;
            
            TRUNCATE TABLE {staging};
            COMMIT;
        """
