from __future__ import annotations
from typing import TYPE_CHECKING
import time

from user_interfaces.GenericUI import GenericUI
from scrap_steam_services.web_page_cleaning import MarketItemPageCleaner
from steam_games import SteamGames
from data_models import PersistToDB

if TYPE_CHECKING:
    from steam_user_trader.SteamUserTrader import SteamUserTrader


class ScrapMarketItemPage:

    def __init__(self, steam_user: SteamUserTrader, retries: int = 7, wait_time: int = 10):
        self.__steam_user = steam_user
        self.__retries = retries
        self.__wait_time = wait_time

    def update_games_buy_orders(self, game_ids: list[int]) -> None:
        games = SteamGames(game_ids=game_ids, with_items=True)
        for index, game_id in enumerate(game_ids):
            self.__steam_user.update_inventory()
            progress_text = f"{index+1:02d} - {games.name(game_id=game_id)}"
            GenericUI.progress_completed(progress=0, total=1, text=progress_text)
            item_keys = ['item_id', 'item_name', 'item_market_url_name']
            items = games.get_trading_cards_and_booster_pack(game_id=game_id, item_keys=item_keys, foil=False)
            for index2, item in enumerate(items):
                retries_left = self.__retries
                while True:
                    time.sleep(self.__wait_time)  # avoiding too many requests
                    try:
                        market_item_page_cleaner = self._full_extraction(
                            game_market_id=games.market_id(game_id=game_id),
                            item_market_url_name=item['item_market_url_name']
                        )
                        cleaned_data = market_item_page_cleaner.get_buy_order()
                        empty_buy_order = not any(cleaned_data.values())
                        cleaned_data['item_id'] = item['item_id']
                        steam_item_name_id = market_item_page_cleaner.get_item_name_id()

                        last_buy_order_was_wrongfully_set_to_empty = cleaned_data['quantity'] > self.__steam_user.buy_orders.active_quantity(item_id=item['item_id'])
                        if not last_buy_order_was_wrongfully_set_to_empty:
                            PersistToDB.persist('steam_asset_origin', source='buy_order',
                                user_id=self.__steam_user.user_id,
                                item_id=item['item_id'],
                                buy_order_new_quantity=cleaned_data['quantity'],
                            )
                        PersistToDB.persist('steam_item', source='market_item_page',
                            item_id=item['item_id'],
                            steam_item_name_id=steam_item_name_id,
                        )
                        PersistToDB.persist('buy_order', source='market_item_page',
                            data=[cleaned_data],
                            user_id=self.__steam_user.user_id,
                            empty_buy_order=empty_buy_order
                        )

                        GenericUI.progress_completed(progress=index2+1, total=len(items), text=progress_text)
                        break
                    except Exception as error:
                        if retries_left == self.__retries:
                            print('')
                        retries_left -= 1
                        print(f"{error}: {item['item_name']}")
                        if not retries_left:
                            raise error

    def _full_extraction(self, game_market_id: str, item_market_url_name: str) -> MarketItemPageCleaner:
        response_status, page_response = self.__steam_user.web_crawler.interact(
            'item_market_page',
            open_web_browser=False,
            game_market_id=game_market_id,
            item_url_name=item_market_url_name,
        )
        page_cleaner = MarketItemPageCleaner(page_response.content)
        return page_cleaner
