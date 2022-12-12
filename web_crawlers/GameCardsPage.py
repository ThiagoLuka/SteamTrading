import requests

from lxml import html

from user_interfaces.GenericUI import GenericUI
from web_crawlers.SteamWebPage import SteamWebPage
from data_models.SteamGames import SteamGames
from data_models.SteamTradingCards import SteamTradingCards


class GameCardsPage(SteamWebPage, name='get_trading_cards'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'steam_id', 'games'

    @staticmethod
    def required_cookies() -> tuple:
        return ()

    def interact(self, cookies: dict, **kwargs):
        games: SteamGames = kwargs['games']
        steam_id: str = kwargs['steam_id']

        progress_total: int = len(games.get_market_ids())
        progress_text = 'Getting new trading cards'
        GenericUI.progress_completed(progress=0, total=progress_total, text=progress_text)

        for index, game in enumerate(games):

            raw_page = self.__extract_raw_gamecards_page(cookies, steam_id, game['market_id'])

            if not raw_page.find_class('badge_card_set_cards'):
                GenericUI.progress_completed(progress=index + 1, total=progress_total, text=progress_text)
                continue

            trading_cards = self.__transform_raw_to_trading_cards(raw_page, game['id'], game['market_id'])

            trading_cards.save()
            GenericUI.progress_completed(progress=index + 1, total=progress_total, text=progress_text)

    def __extract_raw_gamecards_page(self, cookies: dict, steam_id: str, market_id: str) -> html.HtmlElement:
        url = f"{super().BASESTEAMURL}profiles/{steam_id}/gamecards/{market_id}"
        response = requests.get(url, cookies=cookies)
        page = html.fromstring(response.content)
        return page

    def __transform_raw_to_trading_cards(
            self, page: html.HtmlElement, game_id: int, game_market_id: str
    ) -> SteamTradingCards:
        trading_cards = SteamTradingCards()

        names, set_numbers = self.__get_card_name_and_set_number(page)

        url_names = self.__get_url_names(page, len(names), game_market_id)

        tcg_info = list(zip(set_numbers, names, url_names))
        for card in tcg_info:
            trading_cards += SteamTradingCards(game_id=game_id, set_number=card[0], name=card[1], url_name=card[2])

        return trading_cards

    @staticmethod
    def __get_card_name_and_set_number(page: html.HtmlElement) -> tuple[list, list]:
        div_with_cards_info = page.find_class('badge_card_set_cards')[0]
        card_texts = div_with_cards_info.find_class('badge_card_set_text')

        card_names = []
        set_numbers = []

        for card_text_index in range(0, len(card_texts), 2):
            card_name_raw = card_texts[card_text_index].text_content()
            card_name = card_name_raw.replace('\r', '').replace('\n', '').replace('\t', '')
            if '(' == card_name[0]:
                card_name_list_temp = card_name.split(')')
                card_name_list_temp.pop(0)
                card_name = ')'.join(card_name_list_temp)
            card_names.append(card_name)

            set_number = int(card_texts[card_text_index + 1].text_content().split()[0])
            set_numbers.append(set_number)

        return card_names, set_numbers

    @staticmethod
    def __get_url_names(page: html.HtmlElement, set_size: int, game_market_id: str) -> list:
        url_names = []
        all_links: list = page.xpath('//@href')
        link_with_card_url_names: str = ''

        for link in all_links:
            if 'multisell' in link or 'multibuy' in link:
                link_with_card_url_names = link

        if not link_with_card_url_names:
            for i in range(set_size):
                url_names.append('None')
            return url_names

        url_names_on_odd_indexes = link_with_card_url_names.replace('&qty', '').split('[]=')
        url_names_on_odd_indexes.pop()
        for index in range(0, len(url_names_on_odd_indexes), 2):
            url_name = url_names_on_odd_indexes[index+1]
            url_name = url_name.replace(f'{game_market_id}-', '')
            url_names.append(url_name)
        return url_names
