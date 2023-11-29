from .BasePersistenceModel import BasePersistenceModel


class BuyOrder(BasePersistenceModel, name='buy_order'):

    def save(self, user_id: int, empty_buy_order: bool = False) -> None:
        self._df['user_id'] = user_id
        self._db_execute(query=self._insert_into_staging_query(self._df, self.table_name(table_type='staging')))
        self._transfer_staging_to_public(empty_buy_order=empty_buy_order)

    @staticmethod
    def table_name(table_type: str) -> str:
        return {
            'public': 'public.buy_orders',
            'staging': 'staging.buy_order',
        }.get(table_type, '')

    @staticmethod
    def table_columns(table_type: str) -> list:
        return {
            'public': [
                'buy_order_id', 'steam_buy_order_id', 'user_id', 'item_steam_id', 'active', 'price',
                'qtd_start', 'qtd_estimate', 'qtd_current', 'created_at', 'updated_at', 'removed_at'
            ],
            'staging': ['steam_buy_order_id', 'item_id', 'user_id', 'price', 'quantity'],
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
            
            WITH
            	id_to_inactivate AS (
            		SELECT buy_order_id AS id FROM {public}
                    WHERE
                        (item_steam_id, user_id) = (SELECT item_id, user_id FROM {staging})
                        AND active
                    ORDER BY created_at DESC
                    LIMIT 1
            	)
            UPDATE {public}
            SET
            	  active = False
            	, qtd_estimate = 0
            	, qtd_current = 0
            	, updated_at = NOW()::TIMESTAMP
            	, removed_at = NOW()::TIMESTAMP
            WHERE {public}.buy_order_id = (SELECT id FROM id_to_inactivate);
            
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
            FROM {staging} 
            ON CONFLICT (steam_buy_order_id)
            DO UPDATE
            SET
            	  user_id = {public}.user_id
            	, item_steam_id = {public}.item_steam_id
            	, active = True
            	, price = {public}.price
            	, qtd_start = {public}.qtd_start
            	, qtd_estimate = EXCLUDED.qtd_estimate
            	, qtd_current = EXCLUDED.qtd_estimate
            	, created_at = {public}.created_at
            	, updated_at = NOW()::TIMESTAMP
            	, removed_at = NULL
            ;
            
            TRUNCATE TABLE {staging};
            COMMIT;
        """
