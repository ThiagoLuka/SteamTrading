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
                asset_table=asset_table
            )
        elif source == 'remove_sell_listing':
            self._from_sell_listing(
                asset_table=asset_table
            )

    @staticmethod
    def table_name(table_type: str) -> str:
        return {
            'asset_from_buy_order': 'public.asset_from_buy_order',
            'asset_from_booster_pack_origin': '',
            'asset_from_sell_listing_origin': '',
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

    def _from_booster_pack(self, asset_table: str) -> None:
        pass

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