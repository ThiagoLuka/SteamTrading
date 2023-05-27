from user_interfaces.InputValidation import InputValidation


class SteamTraderUI:

    @staticmethod
    def run() -> int:
        print(
            '\n-- MENU STEAM TRADER --\n'
            '1 - Overview: marketable cards by game\n'
            '2 - Update buy orders\n'
            '3 - Open booster packs\n'
            '4 - Sell cards of a game\n'
            '0 - Back to main menu'
        )
        return InputValidation.int_within_range(0, 4)

    @staticmethod
    def overview_marketable_cards(data: dict, inv_total_size: int) -> None:
        min_cards_text = "Don't show games with less than x cards: "
        minimum_cards = InputValidation.int_within_range(0, 100, min_cards_text)
        total_marketable_cards = 0
        total_shown = 0
        print('\nCards ||     Game')
        for game_name, cards_qtd in data.items():
            total_marketable_cards += cards_qtd
            if cards_qtd >= minimum_cards:
                total_shown += cards_qtd
                print(f'{cards_qtd:>4}  ||  {game_name}')
        print(f'\nCards displayed:  {total_shown:>5}')
        print(f'Total marketable: {total_marketable_cards:>5}')
        print(f'Inventory size:   {inv_total_size:>5}')

    @staticmethod
    def update_buy_orders_prompt_message():
        return InputValidation.int_within_range(0, 100, 'How many games do you wish to update? ')

    @staticmethod
    def view_trading_cards_to_sell(cards: dict) -> None:
        total_cards = 0
        print('Cards ||     Name')
        for card_index in cards.keys():
            print(f'{len(cards[card_index]):>4}  ||  {card_index}')
            total_cards += len(cards[card_index])
        print(f'Total cards: {total_cards}')

    @staticmethod
    def set_prices_for_cards(cards: dict) -> dict:
        SteamTraderUI.view_trading_cards_to_sell(cards)
        asset_ids_with_prices: dict = {}
        print('Set prices:')
        for card_name, assets in cards.items():
            price = InputValidation.int_within_range(0, 100, f'  {card_name}: ')
            asset_ids_with_prices.update({asset_id: price for asset_id in assets})
        return asset_ids_with_prices

    @staticmethod
    def buy_orders_header(game_name: str) -> None:
        print(f'\n Buy orders from: {game_name}')

    @staticmethod
    def show_buy_order(qtd: int, price: int, item_name: str) -> None:
        if qtd == 0:
            print(f" {qtd:>3} @  R$ {price / 100:.2f}*  {item_name}")
        else:
            print(f" {qtd:>3} @  R$ {price / 100:.2f}   {item_name}")
