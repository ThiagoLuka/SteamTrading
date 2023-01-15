import requests
from typing import Union

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

        number_of_pages = page_cleaner.get_number_of_pages()

        games: SteamGames = page_cleaner.to_games()
        badges: SteamBadges = page_cleaner.to_badges()
        GenericUI.progress_completed(progress=1, total=number_of_pages, text=progress_text)

        for page_number in range(2, number_of_pages + 1):
            custom_status_code, page_response = self.__get_page(web_crawler, logged_in, page=page_number)
            page_cleaner = ProfileBadgesPageCleaner(page_response.content)
            games += page_cleaner.to_games()
            badges += page_cleaner.to_badges()
            GenericUI.progress_completed(progress=page_number, total=number_of_pages, text=progress_text)

        games.save()
        badges.save(user_id)

    @staticmethod
    def __get_page(
            web_crawler: SteamWebCrawler, logged_in: bool, page: int = None
    ) -> (int, Union[requests.Response, str]):
        custom_status_code, response = web_crawler.interact(
            'get_profile_badges',
            logged_in=logged_in,
            page=page,
        )
        return custom_status_code, response
