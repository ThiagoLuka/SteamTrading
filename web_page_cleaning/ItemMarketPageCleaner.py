from lxml import html


class ItemMarketPageCleaner:

    def __init__(self, page_bytes: bytes):
        self.__page: html.HtmlElement = html.fromstring(page_bytes)

    def item_url_is_valid(self) -> bool:
        if self.__page.find_class('market_listing_iteminfo'):
            return True
        elif self.__page.find_class('market_listing_table_message'):
            return False
        else:
            raise Exception('Unknown page response')

    def get_buy_order_price_and_quantity(self) -> tuple[int, int]:
        """still needs work"""
        pass
        # default_return_value = (0, 0)
        #
        # buy_and_sell_listings = self.__page.find_class('my_listing_section')
        # if not buy_and_sell_listings:
        #     return default_return_value
        #
        # # [0] for sell listings div, [1] for buy orders div
        # buy_order_div = buy_and_sell_listings[1]
        # if buy_order_div.find_class('my_market_header_count')[0].text_content() == '(0)':
        #     return default_return_value
        #
        # raw_buy_order = buy_order_div.find_class('market_listing_price')[0].text_content().split()
        #
        # price = int(raw_buy_order[-1].replace(',', ''))
        # quantity = int(raw_buy_order[0])
        #
        # return price, quantity
