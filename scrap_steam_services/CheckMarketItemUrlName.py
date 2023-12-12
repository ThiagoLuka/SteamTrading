import requests

from steam_user.SteamUser import SteamUser
from scrap_steam_services.web_page_cleaning import MarketItemPageCleaner


class CheckMarketItemUrlName:

    def __init__(self, steam_user: SteamUser):
        self.__steam_user = steam_user

    def run(self, **additional_info) -> str:
        verified_url_name = ''

        if additional_info['item_type'] == 'booster_pack':
            verified_url_name = self.__booster_pack(**additional_info)
        elif additional_info['item_type'] == 'trading_card':
            verified_url_name = self.__trading_card(**additional_info)

        return verified_url_name

    def __booster_pack(self, **additional_info) -> str:
        booster_pack_name = additional_info['booster_pack_name']
        game_market_id: str = additional_info['game_market_id']

        # I'm fully aware I shouldn't be doing the following 'fix string' statements
        # But I really don't see why I should bother any further with such irrational exceptions
        if 'Mass Effect™: Andromeda Deluxe Edition Booster Pack' == booster_pack_name:
            booster_pack_name = booster_pack_name.replace(' Deluxe Edition', '')
        booster_pack_name = booster_pack_name.replace('/', '-')
        booster_pack_name = booster_pack_name.replace('ö', 'ö')
        # Perhaps this one could be solved by the right encoding? Dunno, but I won't take a deep dive into that

        booster_pack_url_name = requests.utils.quote(f'{booster_pack_name}')
        url_valid: bool = self.__item_url_is_valid(game_market_id, booster_pack_url_name)
        if url_valid:
            return booster_pack_url_name

        return ''

    def __trading_card(self, **additional_info) -> str:
        card_name: str = additional_info['card_name']
        game_market_id: str = additional_info['game_market_id']

        card_url_name = requests.utils.quote(f'{card_name}')
        url_valid: bool = self.__item_url_is_valid(game_market_id, card_url_name)
        if url_valid:
            return card_url_name

        card_name_with_parenthesis = f'{card_name} (Trading Card)'
        card_url_name = requests.utils.quote(f'{card_name_with_parenthesis}')
        url_valid: bool = self.__item_url_is_valid(game_market_id, card_url_name)
        if url_valid:
            return card_url_name

        return ''

    def __item_url_is_valid(self, game_market_id: str, item_url_name: str) -> bool:
        custom_status_code, response = self.__steam_user.web_crawler.interact(
            'item_market_page',
            game_market_id=game_market_id,
            item_url_name=item_url_name,
        )
        page_cleaner = MarketItemPageCleaner(response.content)
        return page_cleaner.item_url_is_valid()
