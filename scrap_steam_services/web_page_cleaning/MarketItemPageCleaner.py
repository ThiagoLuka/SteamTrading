from lxml import html


class MarketItemPageCleaner:

    def __init__(self, page_bytes: bytes):
        self.__page: html.HtmlElement = html.fromstring(page_bytes)

    def item_url_is_valid(self) -> bool:
        if self.__page.find_class('market_listing_iteminfo'):
            return True
        elif self.__page.find_class('market_listing_table_message'):
            return False
        else:
            raise Exception('Unknown page response')

    def get_buy_order(self) -> dict:
        listings_div = self.__page.get_element_by_id('tabContentsMyListings')

        sell_listings = listings_div.getchildren()[0]
        buy_order = listings_div.getchildren()[1]

        if not buy_order.find_class('market_listing_price'):
            return {
                'steam_buy_order_id': None,
                'quantity': 0,
                'price': None,
            }

        listing_div_values = dict(buy_order.find_class('market_listing_row market_recent_listing_row')[0].items())
        steam_buy_order_id = listing_div_values['id'].replace('mybuyorder_', '')
        buy_order_data = buy_order.find_class('market_listing_price')[0].text_content().split()
        quantity = int(buy_order_data[0])
        price = int(buy_order_data[-1].replace(',', ''))
        return {
            'steam_buy_order_id': steam_buy_order_id,
            'quantity': quantity,
            'price': price,
        }
