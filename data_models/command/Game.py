from .BasePersistenceModel import BasePersistenceModel


class Game(BasePersistenceModel, name='game'):

    def save(self, source: str = '', update_game_name: bool = True, update_has_trading_cards: bool = False) -> None:
        persist_method = {
            'inventory': self._load_from_inventory,
            'profile_badge': self._load_from_profile_badge,
            'update_has_no_trading_cards': self._update_has_trading_cards,
        }.get(source)
        persist_method()

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

    def _load_from_inventory(self) -> None:
        self._df.drop_duplicates(subset='market_id', inplace=True)
        self._df['has_trading_cards'] = True
        self._insert_into_staging(df=self._df, staging_table_name=self.table_name(table_type='staging'))
        query = self._upsert_game_query(update_game_name=True)
        self._db_execute(query=query)

    def _load_from_profile_badge(self) -> None:
        self._df.drop_duplicates(subset='market_id', inplace=True)
        self._df['has_trading_cards'] = True
        self._insert_into_staging(df=self._df, staging_table_name=self.table_name(table_type='staging'))
        query = self._upsert_game_query(update_game_name=False)
        self._db_execute(query=query)

    def _update_has_trading_cards(self) -> None:
        game_id = self._df.loc[0, 'game_id']
        query = self._update_has_no_trading_cards_query(game_id=game_id)
        self._db_execute(query=query)

    def _upsert_game_query(self, update_game_name: bool) -> str:
        public = self.table_name(table_type='public')
        staging = self.table_name(table_type='staging')
        update_game_name_clause = 'AND p.name = s.name' if update_game_name else ''
        return f"""
        BEGIN TRANSACTION;
        
        DELETE FROM {staging} s 
        USING {public} p
        WHERE
        	p.market_id = s.market_id
        	{update_game_name_clause};

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
            , has_trading_cards = {public}.has_trading_cards;
        
        TRUNCATE TABLE {staging}; 
        
        COMMIT;
        """

    def _update_has_no_trading_cards_query(self, game_id: int) -> str:
        public = self.table_name(table_type='public')
        return f"""
            UPDATE {public} 
            SET has_trading_cards = False
            WHERE id = {game_id};
        """