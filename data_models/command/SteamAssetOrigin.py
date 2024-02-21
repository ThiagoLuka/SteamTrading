from .BasePersistenceModel import BasePersistenceModel


class SteamAssetOrigin(BasePersistenceModel, name='steam_asset_origin'):

    def save(self, source: str, **kwargs):
        asset_table = self.models['steam_asset'].table_name(table_type='public')
        if   source == 'buy_order':
            self._from_buy_order(
                asset_table=asset_table,
                user_id=kwargs['user_id'],
                item_id=kwargs['item_id'],
                new_quantity=kwargs['buy_order_new_quantity'],
            )
        elif source == 'open_booster_pack':
            self._from_booster_pack(
                asset_table=asset_table,
                user_id=kwargs['user_id'],
                game_id=kwargs['game_id'],
                booster_packs_opened=kwargs['booster_packs_opened'],
            )
        elif source == 'remove_sell_listing':
            self._from_sell_listing(
                asset_table=asset_table
            )

    @staticmethod
    def table_name(table_type: str) -> str:
        return {
            'asset_from_buy_order': 'public.asset_from_buy_order',
            'asset_from_booster_pack': 'public.asset_from_booster_pack',
        }.get(table_type, '')

    def _from_buy_order(self, asset_table: str, user_id: int, item_id: int, new_quantity: int) -> None:
        asset_from_buy_order_table = self.table_name('asset_from_buy_order')
        buy_order_table = self.models['buy_order'].table_name(table_type='public')
        query = self._from_buy_order_query(
            asset_from_buy_order_table=asset_from_buy_order_table,
            asset_table=asset_table,
            buy_order_table=buy_order_table,
            user_id=user_id,
            item_id=item_id,
            new_quantity=new_quantity,
        )
        self._db_execute(query=query)

    def _from_booster_pack(self, asset_table: str, user_id: int, game_id: int, booster_packs_opened: int) -> None:
        asset_from_booster_pack_table = self.table_name('asset_from_booster_pack')
        item_table = self.models['steam_item'].table_name(table_type='public')
        query = self._from_booster_pack_query(
            asset_from_booster_pack_table=asset_from_booster_pack_table,
            asset_table=asset_table,
            item_table=item_table,
            user_id=user_id,
            game_id=game_id,
            booster_packs_opened=booster_packs_opened,
        )
        self._db_execute(query=query)

    def _from_sell_listing(self, asset_table: str) -> None:
        pass

    @staticmethod
    def _from_buy_order_query(
        asset_from_buy_order_table,
        asset_table: str,
        buy_order_table: str,
        user_id: int,
        item_id: int,
        new_quantity: int
    ) -> str:
        return f"""
        START TRANSACTION;
        
        CREATE TEMP TABLE assets_to_update AS
        WITH
        	old_buy_order AS (
        		SELECT
        		    id,
        		    price,
        		    qtd_current
        		FROM {buy_order_table} bo 
        		WHERE 
        			user_id = {user_id}
        			AND item_id = {item_id}
        		ORDER BY created_at DESC 
        		LIMIT 1
        	)
        SELECT
            sa.id AS asset_id,
            (SELECT id FROM old_buy_order) AS buy_order_id,
            (SELECT price FROM old_buy_order) AS price
        FROM {asset_table} sa 
        WHERE
        	user_id = {user_id}
        	AND item_id = {item_id}
        	AND origin = 'Undefined'
        ORDER BY created_at DESC
        LIMIT (SELECT qtd_current FROM old_buy_order) - {new_quantity};
        
        
        INSERT INTO {asset_from_buy_order_table} (
        	  asset_id
        	, buy_order_id
        )
        SELECT
        	  asset_id
        	, buy_order_id
        FROM assets_to_update;

        UPDATE {asset_table} sa
        SET
        	  origin = 'Buy Order'
        	, origin_price = price
        FROM assets_to_update
        WHERE sa.id = assets_to_update.asset_id;
        
        DROP TABLE assets_to_update;
        
        COMMIT;
        """

    @staticmethod
    def _from_booster_pack_query(
        asset_from_booster_pack_table,
        asset_table: str,
        item_table: str,
        user_id: int,
        game_id: int,
        booster_packs_opened: int,
    ) -> str:
        return f"""
        START TRANSACTION;
        
        CREATE TEMP TABLE assets_to_update AS
        WITH 
        	opened_booster_packs AS (
        		SELECT 
        			sa.id AS bp_id,
        			sa.origin_price,
        			ROW_NUMBER() OVER (ORDER BY sa.created_at DESC) AS bp_number
        		FROM {asset_table} sa 
        		INNER JOIN {item_table} si ON sa.item_id = si.id 
        		WHERE
        			not sa.active 
        			AND sa.user_id = {user_id}
        			AND si.game_id = {game_id}
        			AND si.steam_item_type_id = 5  -- booster pack
        			AND sa.conclusion = 'Undefined'
        		LIMIT {booster_packs_opened}
        	),
        	cards_from_booster_pack AS (
        		SELECT
        			sa.id AS tc_id,
        			( ( ROW_NUMBER() OVER (ORDER BY sa.created_at DESC) - 1 ) / 3 ) + 1 AS bp_number,
        			( ROW_NUMBER() OVER (ORDER BY sa.created_at DESC) % 3 ) + 1 AS card_number
        		FROM {asset_table} sa 
        		INNER JOIN {item_table} si ON sa.item_id = si.id
        		WHERE
        			sa.active
        			AND sa.user_id = {user_id}
        			AND si.game_id = {game_id}
        			AND si.steam_item_type_id = 2 -- trading card
        			AND sa.origin = 'Undefined'
        	)
        SELECT 
        	obps.bp_id AS booster_pack_asset_id,
        	cfbp.tc_id AS trading_card_asset_id,
        	obps.origin_price AS booster_pack_conclusion_price,
        	CASE 
        		WHEN card_number = 1 THEN ( obps.origin_price / 3 ) + ( obps.origin_price % 3 ) 
        		ELSE obps.origin_price / 3
        	END AS trading_card_origin_price
        FROM opened_booster_packs obps
        INNER JOIN cards_from_booster_pack cfbp ON cfbp.bp_number = obps.bp_number;
        
        
        INSERT INTO {asset_from_booster_pack_table} (
        	  asset_id
        	, booster_pack_asset_id
        )
        SELECT
        	  trading_card_asset_id
        	, booster_pack_asset_id
        FROM assets_to_update;
        
        WITH
            distinct_booster_pack AS (
                SELECT
                    DISTINCT(booster_pack_asset_id) AS asset_id,
                    booster_pack_conclusion_price
                FROM assets_to_update
            )
        UPDATE {asset_table} sa
        SET
        	  conclusion = 'Booster Pack opened'
        	, conclusion_price = booster_pack_conclusion_price
        FROM distinct_booster_pack
        WHERE sa.id = distinct_booster_pack.asset_id;
        
        UPDATE {asset_table} sa
        SET
              origin = 'Booster Pack'
            , origin_price = trading_card_origin_price
        FROM assets_to_update
        WHERE sa.id = assets_to_update.trading_card_asset_id;
        
        DROP TABLE assets_to_update;
        
        COMMIT;
        """