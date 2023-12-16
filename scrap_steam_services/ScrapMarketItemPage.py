from __future__ import annotations
from typing import TYPE_CHECKING
import time

from user_interfaces.GenericUI import GenericUI
from scrap_steam_services.web_page_cleaning import MarketItemPageCleaner
from data_models.SteamGamesNew import SteamGamesNew
from data_models import PersistToDB

if TYPE_CHECKING:
    from steam_user.SteamUser import SteamUser


class ScrapMarketItemPage:

    def __init__(self, steam_user: SteamUser):
        self.__steam_user = steam_user
        self.__retries = 4

    def update_games_buy_orders(self, game_ids: list[int]) -> None:
        games = SteamGamesNew(game_ids=game_ids, with_items=True)
        for index, game_id in enumerate(game_ids):
            progress_text = f"{index+1:02d} - {games.name(game_id=game_id)}"
            GenericUI.progress_completed(progress=0, total=1, text=progress_text)
            item_keys = ['item_id', 'item_name', 'item_market_url_name']
            items = games.get_trading_cards_and_booster_pack(game_id=game_id, item_keys=item_keys, foil=False)
            for index2, item in enumerate(items):
                retries_left = self.__retries
                while True:
                    time.sleep(7)  # avoiding too many requests
                    try:
                        market_item_page_cleaner = self._full_extraction(
                            game_market_id=games.market_id(game_id=game_id),
                            item_market_url_name=item['item_market_url_name']
                        )
                        cleaned_data = market_item_page_cleaner.get_buy_order()
                        empty_buy_order = not any(cleaned_data.values())
                        cleaned_data['item_id'] = item['item_id']
                        PersistToDB.persist(
                            'buy_order',
                            [cleaned_data],
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
