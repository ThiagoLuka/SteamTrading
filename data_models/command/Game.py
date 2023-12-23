from .BasePersistenceModel import BasePersistenceModel


class Game(BasePersistenceModel, name='game'):

    def save(self, source: str, **kwargs) -> None:
        if   source == 'inventory':
            self._load_standard(update_game_name=kwargs['update_game_name'])
        elif source == 'profile_badge':
            self._load_standard(update_game_name=kwargs['update_game_name'])
        elif source == 'profile_game_cards':
            self._set_has_no_trading_cards(game_id=kwargs['game_id'])

    @staticmethod
    def table_name(table_type: str) -> str:
        return {
            'public': 'public.steam_game',
            'staging': 'staging.game',
        }.get(table_type, '')

    def _load_standard(self, update_game_name: bool) -> None:
        self._df.drop_duplicates(subset='market_id', inplace=True)
        self._df['has_trading_cards'] = True
        self._insert_into_staging(df=self._df, staging_table_name=self.table_name(table_type='staging'))
        query = self._upsert_game_query(update_game_name=update_game_name)
        self._db_execute(query=query)

    def _set_has_no_trading_cards(self, game_id: int) -> None:
        query = self._set_has_no_trading_cards_query(game_id=game_id)
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

    def _set_has_no_trading_cards_query(self, game_id: int) -> str:
        public = self.table_name(table_type='public')
        return f"""
            UPDATE {public} 
            SET has_trading_cards = False
            WHERE id = {game_id};
        """