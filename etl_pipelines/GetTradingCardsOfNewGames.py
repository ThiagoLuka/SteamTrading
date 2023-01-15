import requests
from typing import Union

from user_interfaces.GenericUI import GenericUI
from web_crawlers import SteamWebCrawler
from web_page_cleaning.GameCardsPageCleaner import GameCardsPageCleaner
from data_models.SteamTradingCards import SteamTradingCards
from data_models.SteamGames import SteamGames
from data_models.SteamInventory import SteamInventory


class GetTradingCardsOfNewGames:

    def run(self, web_crawler: SteamWebCrawler) -> None:
        games = SteamGames.get_all_without_trading_cards()
        if games.empty:
            return

        progress_total: int = len(games.get_market_ids())
        progress_text = 'Getting new trading cards'
        GenericUI.progress_completed(progress=0, total=progress_total, text=progress_text)

        for index, game in enumerate(games):

            custom_status_code, page_response = self.__get_page(web_crawler, game['market_id'])
            if custom_status_code != 200:
                print(f'\n{custom_status_code}: {page_response}\n')
                return

            page_cleaner = GameCardsPageCleaner(page_response.content)

            if page_cleaner.page_has_no_cards():
                GenericUI.progress_completed(progress=index + 1, total=progress_total, text=progress_text)
                continue

            trading_cards: SteamTradingCards = page_cleaner.to_trading_cards(game['id'], game['market_id'])

            trading_cards.save()
            GenericUI.progress_completed(progress=index + 1, total=progress_total, text=progress_text)

        SteamTradingCards.set_relationship_with_item_descripts(SteamInventory.get_all('descriptions').df)

    @staticmethod
    def __get_page(web_crawler: SteamWebCrawler, game_market_id: str) -> (int, Union[requests.Response, str]):
        custom_status_code, response = web_crawler.interact(
            'get_trading_cards',
            logged_in=True,
            game_market_id=game_market_id
        )
        return custom_status_code, response
