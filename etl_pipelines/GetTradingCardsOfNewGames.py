import requests
from typing import Union

from user_interfaces.GenericUI import GenericUI
from etl_pipelines.CheckItemMarketUrlName import CheckItemMarketUrlName
from web_crawlers import SteamWebCrawler
from web_page_cleaning.GameCardsPageCleaner import GameCardsPageCleaner
from data_models.SteamGames import SteamGames
from data_models.ItemsSteam import ItemsSteam
from data_models.TradingCards import TradingCards


class GetTradingCardsOfNewGames:

    def __init__(self, web_crawler: SteamWebCrawler):
        self.__crawler = web_crawler

    def run(self) -> None:
        games = SteamGames.get_all_with_trading_cards_not_registered()
        if games.empty:
            return

        progress_total: int = len(games.get_market_ids())
        progress_text = 'Getting new trading cards'
        GenericUI.progress_completed(progress=0, total=progress_total, text=progress_text)

        booster_pack_item_id = ItemsSteam.get_item_type_id('Booster Pack')
        trading_card_item_id = ItemsSteam.get_item_type_id('Trading Card')

        for index, game in enumerate(games):

            custom_status_code, page_response = self.__get_cards_page(game['market_id'])
            if custom_status_code != 200:
                print(f'\n{custom_status_code}: {page_response}\n')
                GenericUI.progress_completed(progress=index + 1, total=progress_total, text=progress_text)
                continue

            page_cleaner = GameCardsPageCleaner(page_response.content)

            if page_cleaner.page_has_no_cards():
                print(f"\n{game['name']} has no cards.")
                SteamGames.update_to_has_no_cards(game['id'])
                GenericUI.progress_completed(progress=index + 1, total=progress_total, text=progress_text)
                continue

            booster_pack_name = f"{game['name']} Booster Pack"
            verified_bp_url_name = self.__get_verified_booster_pack_url_name(game['market_id'], booster_pack_name)
            if not verified_bp_url_name:
                print(f"\nCouldn't find booster pack of {game['name']}.")
            else:
                self.__save_booster_pack(game['id'], booster_pack_name, verified_bp_url_name, booster_pack_item_id)

            trading_cards_info: dict[str: list] = page_cleaner.get_cards_info(game['market_id'])
            if not page_cleaner.url_names_found:
                new_url_names = self.__get_verified_cards_url_name(
                    trading_cards_info['names'],
                    game_market_id=game['market_id'],
                )
                if len(trading_cards_info['names']) != len(new_url_names):  # all new urls were not found
                    GenericUI.progress_completed(progress=index + 1, total=progress_total, text=progress_text)
                    print(f"\nCouldn't find all the trading cards of {game['name']}.")
                    continue
                trading_cards_info['url_names'] = new_url_names
            self.__save_trading_cards(game['id'], trading_cards_info, trading_card_item_id)

            GenericUI.progress_completed(progress=index + 1, total=progress_total, text=progress_text)

    def __get_cards_page(self, game_market_id: str) -> (int, Union[requests.Response, str]):
        custom_status_code, response = self.__crawler.interact(
            'game_cards_page',
            logged_in=True,
            game_market_id=game_market_id
        )
        return custom_status_code, response

    def __get_verified_booster_pack_url_name(self, game_market_id: str, booster_pack_name: str) -> str:
        verified_booster_pack_url_name = CheckItemMarketUrlName(self.__crawler).run(
            item_type='booster_pack',
            game_market_id=game_market_id,
            booster_pack_name=booster_pack_name,
        )
        return verified_booster_pack_url_name

    def __get_verified_cards_url_name(self, trading_cards_names: list[str], game_market_id: str) -> list[str]:
        new_url_names = []
        for card_name in trading_cards_names:
            verified_card_url_name = CheckItemMarketUrlName(self.__crawler).run(
                item_type='trading_card',
                game_market_id=game_market_id,
                card_name=card_name,
            )
            if verified_card_url_name:
                new_url_names.append(verified_card_url_name)
        return new_url_names

    @staticmethod
    def __save_booster_pack(game_id: int, booster_pack_name: str, url_name: str, type_id: int) -> None:
        ItemsSteam(
            table='items_steam',
            game_id=game_id,
            item_steam_type_id=type_id,
            name=booster_pack_name,
            market_url_name=url_name,
        ).save()
        item_id: int = ItemsSteam.get_ids_by_market_url_names([url_name])[0]
        TradingCards(
            table='item_booster_packs',
            item_steam_id=item_id,
            game_id=game_id
        ).save()

    @staticmethod
    def __save_trading_cards(game_id: int, trading_cards_info: dict, type_id: int) -> None:
        names = trading_cards_info['names']
        set_numbers = trading_cards_info['set_numbers']
        url_names = trading_cards_info['url_names']

        number_of_cards = len(set_numbers)
        ItemsSteam(
            table='items_steam',
            game_id=[game_id] * number_of_cards,
            item_steam_type_id=[type_id] * number_of_cards,
            name=names,
            market_url_name=url_names,
        ).save()
        item_ids: list = ItemsSteam.get_ids_by_market_url_names(url_names)
        TradingCards(
            table='item_trading_cards',
            item_steam_id=item_ids,
            game_id=[game_id] * number_of_cards,
            set_number=set_numbers,
            foil=[0] * number_of_cards
        ).save()
