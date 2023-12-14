from __future__ import annotations
from typing import TYPE_CHECKING
import requests
import concurrent.futures

from user_interfaces.GenericUI import GenericUI
from scrap_steam_services.web_page_cleaning import ProfileBadgesPageCleaner
from data_models import PersistToDB

if TYPE_CHECKING:
    from steam_user.SteamUser import SteamUser


class ScrapProfileBadgesPage:

    def __init__(self, steam_user: SteamUser):
        self.__steam_user = steam_user
        self.__logged_in = True

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
            user_id=self.__steam_user.user_id,
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
        custom_status_code, response = self.__steam_user.web_crawler.interact(
            'profile_badges',
            logged_in=self.__logged_in,
            page_number=page_number,
        )
        return response
