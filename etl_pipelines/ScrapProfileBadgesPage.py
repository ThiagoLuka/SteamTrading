import requests
from typing import Union
import concurrent.futures

from user_interfaces.GenericUI import GenericUI
from web_crawlers import SteamWebCrawler
from web_page_cleaning.ProfileBadgesPageCleaner import ProfileBadgesPageCleaner
from data_models.SteamGames import SteamGames
from data_models.SteamBadges import SteamBadges


class ScrapProfileBadgesPage:

    def run(self, web_crawler: SteamWebCrawler, **required_data) -> None:
        logged_in: bool = required_data['logged_in']
        user_id: int = required_data['user_id']

        progress_text = 'Extracting and cleaning badges data'
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)

        custom_status_code, first_page_response = self.__get_page(web_crawler, logged_in)
        if custom_status_code != 200:
            print(f'\n{custom_status_code}: {first_page_response}\n')
            return

        page_cleaner = ProfileBadgesPageCleaner(first_page_response.content)
        number_of_pages: int = page_cleaner.get_number_of_pages()

        all_page_cleaners = [page_cleaner, *self.__get_next_pages(web_crawler, logged_in, number_of_pages)]

        for index, page_cleaner in enumerate(all_page_cleaners):

            games: list[SteamGames] = []
            for raw_badge in page_cleaner.raw_badges:
                raw_badge_cleaner = page_cleaner.BadgeCleaner(raw_badge)
                games.append(self.__transform_to_games(raw_badge_cleaner))
            all_games = sum(games)
            all_games.save()

            badges: list[SteamBadges] = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_badges = {
                    executor.submit(
                        self.__transform_to_badges,
                        page_cleaner.BadgeCleaner(raw_badge)
                    )
                    for raw_badge
                    in page_cleaner.raw_badges
                }
                for future in concurrent.futures.as_completed(future_badges):
                    badges.append(future.result())
            all_badges = sum(badges)
            all_badges.save(user_id)

            GenericUI.progress_completed(progress=index+1, total=number_of_pages, text=progress_text)

    @staticmethod
    def __get_page(
            web_crawler: SteamWebCrawler, logged_in: bool, page: int = None
    ) -> (int, Union[requests.Response, str]):
        custom_status_code, response = web_crawler.interact(
            'profile_badges',
            logged_in=logged_in,
            page=page,
        )
        return custom_status_code, response

    def __get_next_pages(self, web_crawler: SteamWebCrawler, logged_in: bool, number_of_pages: int) -> list:
        pages = []
        if number_of_pages == 1:
            return pages
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_pages = {
                executor.submit(
                    self.__get_page,
                    web_crawler, logged_in, page
                )
                for page in range(2, number_of_pages+1)
            }
            for future in concurrent.futures.as_completed(future_pages):
                custom_status_code, page_response = future.result()
                pages.append(ProfileBadgesPageCleaner(page_response.content))
        return pages

    @staticmethod
    def __transform_to_games(raw_badge_cleaner: ProfileBadgesPageCleaner.BadgeCleaner) -> SteamGames:
        if not raw_badge_cleaner.is_game_badge():
            return SteamGames()
        market_id = raw_badge_cleaner.get_market_id()  # check type
        game_name = raw_badge_cleaner.get_game_name()
        return SteamGames(name=game_name, market_id=market_id)

    @staticmethod
    def __transform_to_badges(raw_badge_cleaner: ProfileBadgesPageCleaner.BadgeCleaner) -> SteamBadges:
        if not (raw_badge_cleaner.is_completed() and raw_badge_cleaner.have_info()):
            return SteamBadges()
        badge_name = raw_badge_cleaner.get_badge_name()
        level, xp = raw_badge_cleaner.get_level_and_xp()
        foil = raw_badge_cleaner.get_foil()
        pure_badge_page_id = raw_badge_cleaner.get_pure_badge_page_id()
        game_market_id = raw_badge_cleaner.get_market_id()
        game_id = None if game_market_id is None else SteamGames.get_id_by_market_id(game_market_id)
        unlocked_datetime = raw_badge_cleaner.get_unlocked_datetime()
        return SteamBadges(
            name=badge_name, level=level, experience=xp, foil=foil, game_id=game_id,
            pure_badge_page_id=pure_badge_page_id, unlocked_at=unlocked_datetime
        )
