import requests
from typing import Union

from user_interfaces.GenericUI import GenericUI
from steam_user.SteamUser import SteamUser
from scrap_steam_services import CheckMarketItemUrlName
from scrap_steam_services.web_page_cleaning import ProfileGameCardsPageCleaner
from data_models.SteamGames import SteamGames
from data_models.ItemsSteam import ItemsSteam
from data_models import PersistToDB


class ScrapProfileGameCardsPage:

    def __init__(self, steam_user: SteamUser):
        self.__steam_user = steam_user

    def get_new_trading_cards(self) -> None:
        games = SteamGames.get_all_with_trading_cards_not_registered()
        if games.empty:
            return

        progress_total: int = len(games.get_market_ids())
        progress_text = 'Getting new trading cards'
        GenericUI.progress_completed(progress=0, total=progress_total, text=progress_text)

        booster_pack_item_id = ItemsSteam.get_item_type_id('Booster Pack')
        trading_card_item_id = ItemsSteam.get_item_type_id('Trading Card')

        for index, game in enumerate(games):

            # verify if page exists
            custom_status_code, page_response = self.__get_cards_page(game['market_id'])
            if custom_status_code != 200:
                print(f'\n{custom_status_code}: {page_response}\n')
                GenericUI.progress_completed(progress=index + 1, total=progress_total, text=progress_text)
                continue

            page_cleaner = ProfileGameCardsPageCleaner(page_response.content)

            # verify if page has cards (it might not!)
            if page_cleaner.page_has_no_cards():
                print(f"\n{game['name']} has no cards.")
                PersistToDB.persist(
                    'game',
                    [{'game_id': game['id']}],
                    source='update_has_no_trading_cards'
                )
                GenericUI.progress_completed(progress=index + 1, total=progress_total, text=progress_text)
                continue

            booster_pack_name = f"{game['name']} Booster Pack"
            verified_bp_url_name = self.__get_verified_url_name(item_name=booster_pack_name, game_market_id=game['market_id'])
            if not verified_bp_url_name:
                print(f"\nCouldn't find booster pack of {game['name']}.")
                continue

            booster_pack = {
                'game_market_id': game['market_id'],
                'market_url_name': verified_bp_url_name,
                'name': booster_pack_name,
                'steam_item_type_id': booster_pack_item_id,
                'set_number': 0,
                'foil': False,
            }

            trading_cards: list[dict] = page_cleaner.get_cards_info(game['market_id'])

            # getting cards through verified url name function. If not all found, continue loop
            # I'm not sure if that still works, but it's an exception case, so I hope it doesn't happend that often
            if not page_cleaner.url_names_found:
                all_new_url_names_found = True
                for item in trading_cards:
                    new_url_name = self.__get_verified_url_name(item_name=item['name'], game_market_id=game['market_id'])
                    item['market_url_name'] = new_url_name
                    if not new_url_name:
                        all_new_url_names_found = False
                if not all_new_url_names_found:
                    GenericUI.progress_completed(progress=index + 1, total=progress_total, text=progress_text)
                    print(f"\nCouldn't find all the trading cards of {game['name']}.")
                    continue

            # add foil and card's steam_item_type_id to trading_cards
            for card in trading_cards:
                card.update({
                    'game_market_id': game['market_id'],
                    'steam_item_type_id': trading_card_item_id,
                    'foil': False,
                })

            PersistToDB.persist(
                'steam_item',
                [booster_pack, *trading_cards],
                source='profile_game_cards',
            )

            GenericUI.progress_completed(progress=index + 1, total=progress_total, text=progress_text)

    def __get_cards_page(self, game_market_id: str) -> (int, Union[requests.Response, str]):
        custom_status_code, response = self.__steam_user.web_crawler.interact(
            'game_cards_page',
            logged_in=True,
            game_market_id=game_market_id
        )
        return custom_status_code, response

    def __get_verified_url_name(self, item_name: str, game_market_id: str) -> str:
        item_url_name = CheckMarketItemUrlName(
            self.__steam_user
        ).run(
            item_type='trading_card',
            game_market_id=game_market_id,
            card_name=item_name,
        )
        return item_url_name
