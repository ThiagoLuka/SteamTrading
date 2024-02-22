from .BasePersistenceModel import BasePersistenceModel


class BuyOrder(BasePersistenceModel, name='buy_order'):

    def save(self, source: str, **kwargs) -> None:
        if   source == 'market_item_page':
            self._load_standard(user_id=kwargs['user_id'], empty_buy_order=kwargs['empty_buy_order'])
        elif source == 'create_buy_order':
            self._load_standard(user_id=kwargs['user_id'], empty_buy_order=False)
        elif source == 'cancel_buy_order':
            self._set_to_inactive(steam_buy_order_id=kwargs['steam_buy_order_id'], conclusion='Canceled')

    @staticmethod
    def table_name(table_type: str) -> str:
        return {
            'public': 'public.buy_order',
            'staging': 'staging.buy_order',
        }.get(table_type, '')

    def _load_standard(self, user_id: int, empty_buy_order: bool) -> None:
        self._df['user_id'] = user_id
        self._insert_into_staging(df=self._df, staging_table_name=self.table_name(table_type='staging'))
        query = self._empty_buy_order_query() if empty_buy_order else self._upsert_buy_order_query()
        self._db_execute(query=query)

    def _set_to_inactive(self, steam_buy_order_id: str, conclusion: str) -> None:
        public = self.table_name(table_type='public')
        query = f"""
        UPDATE {public} pbo
        SET
              active = False
            , qtd_current = 0
            , conclusion = '{conclusion}'
            , updated_at = NOW()::TIMESTAMP
            , removed_at = NOW()::TIMESTAMP
        WHERE
            steam_buy_order_id = '{steam_buy_order_id}';
        """
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
            , conclusion = 'Vanished'
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
        item_table = self.models['steam_item'].table_name(table_type='public')
        return f"""
        BEGIN TRANSACTION;
        
        INSERT INTO {public} (
	          game_id 
	        , item_id 
	        , user_id 
	        , steam_buy_order_id 
	        , active 
	        , price 
	        , qtd_start 
	        , qtd_current 
	        , conclusion
	        , created_at 
	        , updated_at 
	        , removed_at 
        )
        SELECT 
	          si.game_id 
	        , s.item_id 
	        , s.user_id 
	        , s.steam_buy_order_id 
	        , True AS active 
	        , s.price 
	        , s.quantity AS qtd_start 
	        , s.quantity AS qtd_current 
	        , 'Undefined' AS conclusion
	        , s.created_at AS created_at 
	        , s.created_at AS updated_at 
	        , NULL AS removed_at 
        FROM {staging} s
        INNER JOIN {item_table} si ON s.item_id = si.id
        ON CONFLICT (steam_buy_order_id)
        DO UPDATE
        SET
        	  active = True
        	, qtd_current = EXCLUDED.qtd_current
        	, conclusion = EXCLUDED.conclusion
        	, updated_at = EXCLUDED.created_at
        	, removed_at = NULL
        ;
        
        TRUNCATE TABLE {staging};
        COMMIT;
        """
