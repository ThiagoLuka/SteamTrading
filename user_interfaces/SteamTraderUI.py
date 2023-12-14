from user_interfaces.InputValidation import InputValidation


class SteamTraderUI:

    @staticmethod
    def run() -> int:
        print(
            '\n-- MENU STEAM TRADER --\n'
            '1 - Overview: marketable cards by game\n'
            '2 - Update buy orders\n'
            '3 - Create new buy orders\n'
            '4 - Open booster packs\n'
            '5 - Update sell listings\n'
            '6 - Sell cards of a game\n'
            '0 - Back to main menu'
        )
        return InputValidation.int_within_range(0, 6)

    @staticmethod
    def overview_marketable_cards(summary: dict, inv_total_size: int) -> None:
        min_cards_text = "Don't show games with less than x cards: "
        minimum_cards = InputValidation.int_within_range(0, 100, min_cards_text)
        total_shown = 0
        print('\nCards ||     Game')
        for game_name, items_qtd in summary.items():
            if items_qtd >= minimum_cards:
                total_shown += items_qtd
                print(f'{items_qtd:>4}  ||  {game_name}')
        print(f'\nCards displayed:  {total_shown:>5}')
        print(f'Total marketable: {sum(summary.values()):>5}')
        print(f'Inventory size:   {inv_total_size:>5}')

    @staticmethod
    def update_buy_orders_prompt_message() -> int:
        return InputValidation.int_within_range(0, 100, 'How many games do you wish to update? ')

    @staticmethod
    def create_first_buy_order_of_game() -> bool:
        return InputValidation.yes_or_no('First buy order of the game?')

    @staticmethod
    def how_many_games_buy_orders() -> int:
        return InputValidation.int_within_range(0, 100, 'For how many games do you wish to create new buy orders? ')

    @staticmethod
    def sell_cards_prompt_message() -> int:
        return InputValidation.int_within_range(0, 200, 'How many games do you wish to sell cards from? ')

    @staticmethod
    def open_booster_packs() -> int:
        return InputValidation.int_within_range(0, 50, 'How many games do you wish to open booster packs from? ')

    @staticmethod
    def view_trading_cards_to_sell(cards: list) -> None:
        total_cards = 0
        print('\nItems to sell:')
        print('Cards ||     Name')
        for name, qtd, idx in cards:
            print(f'{qtd:>4}  ||  {idx}-{name}')
            total_cards += qtd
        print(f'Total cards: {total_cards}')

    @staticmethod
    def set_sell_price_for_item(item_name: str, item_number: int) -> int:
        return InputValidation.int_within_range(5, 100, f' {item_number}-{item_name}: ')

    @staticmethod
    def set_buy_order_for_item(item_name: str, item_number: int) -> tuple[int, int]:
        print(f' {item_number} - {item_name} ')
        price = InputValidation.int_within_range(0, 150, f' Price: ')
        qtd = InputValidation.int_within_range(50, 200, f' Quantity: ')
        return price, qtd

    @staticmethod
    def create_buy_order_failed() -> None:
        print('Something went wrong with the creation of the buy order')

    @staticmethod
    def set_buy_orders_header() -> None:
        print('\nSetting buy orders')

    @staticmethod
    def buy_orders_header(game_name: str) -> None:
        print(f'\n Buy orders from: {game_name}')

    @staticmethod
    def show_buy_order(qtd: int, price: int, item_name: str) -> None:
        if qtd == 0:
            print(f" {qtd:>3} @  R$ {price / 100:.2f}*  {item_name}")
        else:
            print(f" {qtd:>3} @  R$ {price / 100:.2f}   {item_name}")
