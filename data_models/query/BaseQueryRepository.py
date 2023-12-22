from typing import Union

from data_models.db.DBController import DBController


class BaseQueryRepository:

    @staticmethod
    def query_tables(table_type: str) -> str:
        return {
            'game': 'public.steam_game',
            'user': 'public.steam_user',
            'user_game': 'public.steam_user_marketable_game',
            'bagde_game': 'public.game_badges',
            'badge_user': 'public.user_badges',
            'badge_pure': 'public.pure_badges',
            'steam_item': 'public.steam_item',
            'steam_item_trading_card': 'public.steam_trading_card',
            'steam_item_type': 'public.steam_item_type',
            'steam_item_description': 'public.steam_item_description',
            'inventory': 'public.steam_asset',
            'sell_listing': 'public.sell_listing',
            'buy_order': 'public.buy_order',
        }.get(table_type)

    @staticmethod
    def _db_execute(query: str) -> Union[list[tuple], int]:
        return DBController.execute(query=query, get_result=True)
