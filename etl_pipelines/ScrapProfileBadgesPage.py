import requests
import concurrent.futures

from user_interfaces.GenericUI import GenericUI
from web_crawlers import SteamWebCrawler
from web_page_cleaning.ProfileBadgesPageCleaner import ProfileBadgesPageCleaner
from data_models import PersistToDB


class ScrapProfileBadgesPage:

    def __init__(self, web_crawler: SteamWebCrawler, user_id: int, logged_in: bool = True):
        self.__crawler = web_crawler
        self.__user_id = user_id
        self.__logged_in = logged_in

    def get_profile_badges(self) -> None:
        progress_text = 'Extracting and cleaning badges data'
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)

        first_page_cleaner = self._get_first_page()
        number_of_pages = first_page_cleaner.get_number_of_pages()
        all_page_cleaners = [first_page_cleaner, *self._get_next_pages(number_of_pages)]

        games_found_in_badges_page = []
        badges_found = []

        for index, page_cleaner in enumerate(all_page_cleaners):
            games_found_in_badges_page += page_cleaner.get_games_info()
            badges_found += page_cleaner.get_badges_info()
            GenericUI.progress_completed(progress=index+1, total=number_of_pages, text=progress_text)

        PersistToDB.persist(
            'game',
            games_found_in_badges_page,
            source='profile_badge',
        )

        PersistToDB.persist(
            'steam_badge',
            badges_found,
            user_id=self.__user_id,
        )

    def _get_first_page(self) -> ProfileBadgesPageCleaner:
        first_page_response = self._get_page(page_number=1)
        return ProfileBadgesPageCleaner(first_page_response.content)

    def _get_next_pages(self, number_of_pages: int) -> list[ProfileBadgesPageCleaner]:
        pages = []
        if number_of_pages == 1:
            return pages
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_pages = {
                executor.submit(self._get_page, page_number)
                for page_number in range(2, number_of_pages+1)
            }
            for future in concurrent.futures.as_completed(future_pages):
                page_response = future.result()
                pages.append(ProfileBadgesPageCleaner(page_response.content))
        return pages

    def _get_page(self, page_number: int = None) -> requests.Response:
        custom_status_code, response = self.__crawler.interact(
            'profile_badges',
            logged_in=self.__logged_in,
            page_number=page_number,
        )
        return response
