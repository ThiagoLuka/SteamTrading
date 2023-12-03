from .BasePersistenceModel import BasePersistenceModel


class Game(BasePersistenceModel, name='game'):

    def save(self) -> None:
        self._df.drop_duplicates(subset='market_id', inplace=True)
        if 'has_trading_cards' not in list(self._df.columns):
            self._df['has_trading_cards'] = True
        self._insert_into_staging(df=self._df, staging_table_name=self.table_name(table_type='staging'))
        self._transfer_staging_to_public()

    @staticmethod
    def table_name(table_type: str) -> str:
        return {
            'public': 'public.games',
            'staging': 'staging.game',
        }.get(table_type, '')

    @staticmethod
    def table_columns(table_type: str) -> list:
        return {
            'public': ['id', 'name', 'market_id', 'has_trading_cards'],
            'staging': ['name', 'market_id', 'has_trading_cards'],
        }.get(table_type, [])

    def _transfer_staging_to_public(self) -> None:
        query = self._upsert_game_query()
        self._db_execute(query=query)

    def _upsert_game_query(self) -> str:
        public = self.table_name(table_type='public')
        staging = self.table_name(table_type='staging')
        return f"""
        BEGIN TRANSACTION;
        
        DELETE FROM {staging} s 
        USING {public} p
        WHERE
        	p.market_id = s.market_id
        	AND p.name = s.name;

        INSERT INTO {public} (
            name,
            market_id,
            has_trading_cards
        )
        SELECT
            name,
            market_id,
            has_trading_cards
        FROM {staging}
        ON CONFLICT (market_id)
        DO UPDATE
        SET
              name = EXCLUDED.name
            , has_trading_cards = {public}.has_trading_cards
        ;
        
        TRUNCATE TABLE {staging}; 
        
        COMMIT;
        """