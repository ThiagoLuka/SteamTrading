from datetime import datetime, date

from lxml import html


class MarketMainPageCleaner:

    def __init__(self):
        self.__total_count = 0
        self.__listing_html_elements = []
        self.__lisintg_info_cleaned = []

    def __add__(self, other: dict):
        self.__total_count = int(other['total_count'])
        new_listings_html_table: str = other['results_html']
        listings_html_table = html.fromstring(new_listings_html_table)
        listings_html_elements = listings_html_table.get_element_by_id(
            'tabContentsMyActiveMarketListingsRows').getchildren()
        self.__listing_html_elements.extend(listings_html_elements)
        return self

    @property
    def total_count(self) -> int:
        return self.__total_count

    @property
    def listings_downloaded(self) -> int:
        return len(self.__listing_html_elements)

    def has_more_items_to_download(self) -> bool:
        if self.__total_count == 0:
            return True
        return self.__total_count > len(self.__listing_html_elements)

    def clean(self) -> list[dict]:
        for html_elem in self.__listing_html_elements:
            elem_cleaned: dict = {}

            steam_sell_listing_id, steam_asset_id = self._get_steam_sell_listing_id_and_asset_id(html_elem)
            price_buyer, price_to_receive = self._get_price_buyer_and_price_to_receive(html_elem)
            steam_created_date = self._get_steam_created_date(html_elem)

            elem_cleaned['steam_sell_listing_id'] = steam_sell_listing_id
            elem_cleaned['steam_asset_id'] = steam_asset_id
            elem_cleaned['price_buyer'] = price_buyer
            elem_cleaned['price_to_receive'] = price_to_receive
            elem_cleaned['steam_created_at'] = steam_created_date

            self.__lisintg_info_cleaned.append(elem_cleaned)
        self.__listing_html_elements = []
        return self.__lisintg_info_cleaned

    @staticmethod
    def _get_steam_sell_listing_id_and_asset_id(html_elem) -> tuple[str, str]:
        for (element, attribute, link, pos) in html_elem.find_class('market_listing_cancel_button')[0].iterlinks():
            cancel_listing_link_cleaned = link.replace("'", '').replace(')', '').split(', ')
            steam_sell_listing_id = cancel_listing_link_cleaned[1]
            steam_asset_id = cancel_listing_link_cleaned[4]
        return steam_sell_listing_id, steam_asset_id

    @staticmethod
    def _get_price_buyer_and_price_to_receive(html_elem) -> tuple[int, int]:
        prices_text = html_elem.getchildren()[2].text_content()
        price_buyer, price_to_receive = prices_text.strip().replace('R$ ', '').replace(',', '').split()
        price_buyer = int(price_buyer)
        price_to_receive = int(price_to_receive.replace('(', '').replace(')', ''))
        return price_buyer, price_to_receive

    @staticmethod
    def _get_steam_created_date(html_elem) -> date:
        str_date = html_elem.getchildren()[3].text_content().strip() + ' ' + str(datetime.today().year)
        steam_created_date = datetime.strptime(str_date, '%d %b %Y').date()
        return steam_created_date