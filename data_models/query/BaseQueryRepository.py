from typing import Union

from data_models.db.DBController import DBController


class BaseQueryRepository:

    @staticmethod
    def query_tables(table_type: str) -> str:
        return {
            'game': 'public.games',
            'user': 'public.users',
            'user_game': 'public.user_game_trade',
            'bagde_game': 'public.game_badges',
            'badge_user': 'public.user_badges',
            'badge_pure': 'public.pure_badges',
            'steam_item': 'public.items_steam',
            'steam_item_trading_card': 'public.item_trading_cards',
            'steam_item_type': 'public.item_steam_types',
            'steam_item_description': 'public.item_steam_descriptions',
            'inventory': 'public.steam_asset',
            'sell_listing': 'public.sell_listing',
            'buy_order': 'public.buy_order',
        }.get(table_type)

    @staticmethod
    def _db_execute(query: str) -> Union[list[tuple], int]:
        return DBController.execute(query=query, get_result=True)
