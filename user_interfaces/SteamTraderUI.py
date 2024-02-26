from datetime import datetime

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
            '5 - Remove old sell listings\n'
            '6 - Update sell listings\n'
            '7 - Sell cards of a game\n'
            '0 - Back to main menu'
        )
        return InputValidation.int_within_range(0, 7)

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
    def create_buy_order_options() -> int:
        print(
            '1 - First buy orders of a game\n'
            '2 - Recreate buy orders of a game\n'
            '3 - Update empty buy orders'
        )
        return InputValidation.int_within_range(1, 3)

    @staticmethod
    def update_buy_orders_prompt_message(option: str) -> int:
        option_str = {
            'outdated': 'Outdated buy order',
            'undefined': 'Undefined assets',
        }.get(option, 'No option')
        return InputValidation.int_within_range(0, 100, f'How many games do you wish to update? ({option_str}) ')

    @staticmethod
    def recreate_buy_order_item() -> bool:
        return InputValidation.yes_or_no("Recreate this item's buy order?")

    @staticmethod
    def continue_with_recreate_buy_orders() -> bool:
        return InputValidation.yes_or_no('Continue with another game?')

    @staticmethod
    def create_buy_orders_for_how_many_outdated_items() -> int:
        return InputValidation.int_within_range(0, 100, 'How many items do you wish to update? ')

    @staticmethod
    def sell_cards_prompt_message() -> int:
        return InputValidation.int_within_range(0, 200, 'How many games do you wish to sell cards from? ')

    @staticmethod
    def open_booster_packs() -> int:
        return InputValidation.int_within_range(0, 50, 'How many games do you wish to open booster packs from? ')

    @staticmethod
    def analyze_game_id_range() -> list[int]:
        lower = InputValidation.int_within_range(0, 800, 'What is the lowest game_id to analyze? ')
        higher = InputValidation.int_within_range(0, 800, 'What is the highest game_id to analyze? ')
        return [lower, higher]

    @staticmethod
    def generate_price_report() -> bool:
        return InputValidation.yes_or_no('Generate a price analysis?')

    @staticmethod
    def starting_price_analysis(show_date: bool = False, file = None) -> None:
        print(f'{datetime.today().date().isoformat() if show_date else ""}\nStarting price analyze...', file=file)

    @staticmethod
    def set_manual_option_prompt_message() -> bool:
        return InputValidation.yes_or_no('Is it going to be manual?')

    @staticmethod
    def show_marketable_items_to_sell_summary(items: list, summary: dict) -> None:
        total_cards = 0
        print('\nItems to sell:')
        print('Cards ||     Name')
        for item_id, item_count in summary.items():
            item = list(filter(lambda steam_item: steam_item['item_id'] == item_id, items))[0]
            print(f"{item_count:>4}  || {item['item_name']}")
            total_cards += item_count
        print(f'Total cards: {total_cards}')

    @staticmethod
    def set_sell_price_for_item() -> int:
        return InputValidation.int_within_range(5, 100, f' Price: ')

    @staticmethod
    def set_buy_order_for_item() -> tuple[int, int]:
        price = InputValidation.int_within_range(3, 150, f' Price: ')
        qtd = InputValidation.int_within_range(50, 200, f' Quantity: ')
        return price, qtd

    @staticmethod
    def show_item_name(item_name: str, set_number: int, file=None) -> None:
        set_number = int(set_number) if str(set_number) != 'nan' else ''
        print(f" {set_number:>2}-{item_name}", file=file)

    @staticmethod
    def create_buy_order_failed() -> None:
        print('\nSomething went wrong with the creation of the buy order')

    @staticmethod
    def cancel_buy_order_failed() -> None:
        print('\nSomething went wrong with the cancel of the buy order')

    @staticmethod
    def comparing_bp_and_cards_prices() -> None:
        print('Comparing booster pack and cards prices...')

    @staticmethod
    def bp_and_card_price_comparison(bp_price: int, card_price: float) -> None:
        print(f'Booster pack seller price        : {bp_price}\n'
              f'Average card seller price times 3: {(3*card_price):.2f}\n')

    @staticmethod
    def game_header_with_counter(game_name: str, index: int = 0, file = None) -> None:
        print(f'\n {index+1:>2}- {game_name}', file=file)

    @staticmethod
    def show_game_recent_buy_orders(items: list[dict], buy_orders_history: dict, file=None) -> None:
        for item in items:
            item_id = item['item_id']
            buy_order = buy_orders_history[item_id][0]
            SteamTraderUI.show_single_buy_order(item=item, buy_order=buy_order, file=file)

    @staticmethod
    def show_item_all_buy_orders(item: dict, buy_orders: list[dict], reverse: bool = False) -> None:
        if reverse:
            buy_orders.reverse()
        for buy_order in buy_orders:
            SteamTraderUI.show_single_buy_order(item=item, buy_order=buy_order, show_name=False)

    @staticmethod
    def show_single_buy_order(item: dict, buy_order: dict, show_name: bool = True, file=None) -> None:
        item_name = item['item_name']
        set_number = int(item['set_number']) if str(item['set_number']) != 'nan' else ''
        qtd = buy_order['qtd_current']
        price = buy_order['price']
        created_at = buy_order['created_at'].date()
        name = f"{set_number:>2}-{item_name}"
        print(f" {created_at} - {qtd:>3} @ R$ {price / 100:>5.2f}  {name if show_name else ''}", file=file)

    @staticmethod
    def remove_old_sell_listing() -> None:
        print('\nRemoving old sell listings...')

    @staticmethod
    def show_item_info_remove_sell_listing(item_name: str, game_name: str, created_at: datetime.date, price_to_receive: int) -> None:
        print(f'\nRemoving: {item_name} - {game_name}'
              f'\nCreated : {created_at}'
              f'\nPrice   : {price_to_receive}\n')
