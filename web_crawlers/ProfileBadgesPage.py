import requests
from datetime import date
from typing import Optional

from lxml import html

from user_interfaces.GenericUI import GenericUI
from web_crawlers.SteamWebPage import SteamWebPage
from data_models.SteamGames import SteamGames
from data_models.SteamBadges import SteamBadges


class ProfileBadgesPage(SteamWebPage, name='get_badges'):

    @staticmethod
    def required_user_data() -> tuple:
        return 'user_id', 'steam_id'

    @staticmethod
    def required_cookies() -> tuple:
        return 'timezoneOffset',

    def interact(self, cookies: dict, **kwargs):
        user_id: int = kwargs['user_id']
        steam_id: str = kwargs['steam_id']

        badges_raw = self.__extract_all_badges_raw(steam_id, cookies)

        games = self.__transform_raw_to_games(badges_raw)
        games.save()

        badges = self.__transform_raw_to_badges(badges_raw)
        badges.save(user_id)

    def __extract_all_badges_raw(self, steam_id: str, cookies: dict) -> list[html.HtmlElement]:
        progress_text = 'Extracting data from badges pages'
        GenericUI.progress_completed(progress=0, total=1, text=progress_text)
        url = f"{super().BASESTEAMURL}profiles/{steam_id}/badges/?sort=a"
        response = requests.get(url, cookies=cookies)
        first_page = html.fromstring(response.content)

        all_badges_raw = first_page.find_class('badge_row')

        if first_page.find_class('profile_paging'):
            next_pages_urls = self.__get_next_pages_urls(first_page, url)
            GenericUI.progress_completed(progress=1, total=len(next_pages_urls) + 1, text=progress_text)

            for index, url in enumerate(next_pages_urls):
                response = requests.get(url, cookies=cookies)
                page = html.fromstring(response.content)
                all_badges_raw.extend(page.find_class('badge_row'))
                GenericUI.progress_completed(progress=index + 2, total=len(next_pages_urls) + 1, text=progress_text)
        else:
            GenericUI.progress_completed(progress=1, total=1, text=progress_text)

        return all_badges_raw

    def __transform_raw_to_games(self, badges_raw: list[html.HtmlElement]) -> SteamGames:
        progress_text = 'Cleaning data: games'
        GenericUI.progress_completed(progress=0, total=len(badges_raw), text=progress_text)

        games = SteamGames()
        for index, badge_raw in enumerate(badges_raw):

            # badges not related to games (pure_badges) have '/badges/' in their url and should be ignored
            badge_details_link = badge_raw.find_class('badge_row_overlay')[0].get('href')
            if '/badges/' in badge_details_link:
                GenericUI.progress_completed(progress=index + 1, total=len(badges_raw), text=progress_text)
                continue

            market_id = badge_details_link.split('/')[-2]
            game_name = self.__get_game_name(badge_raw)

            games += SteamGames(name=game_name, market_id=market_id)
            GenericUI.progress_completed(progress=index + 1, total=len(badges_raw), text=progress_text)

        return games

    def __transform_raw_to_badges(self, badges_raw: list[html.HtmlElement]) -> SteamBadges:
        progress_text = 'Cleaning data: badges'
        GenericUI.progress_completed(progress=0, total=len(badges_raw), text=progress_text)

        badges = SteamBadges()
        for index, badge_raw in enumerate(badges_raw):

            # not completed badges are ignored
            if badge_raw.find_class('badge_empty'):
                GenericUI.progress_completed(progress=index + 1, total=len(badges_raw), text=progress_text)
                continue

            # some badges have no info whatsoever. It's a bit weird, and they should be ignored as well
            if not badge_raw.find_class('badge_current')[0].getchildren():
                GenericUI.progress_completed(progress=index + 1, total=len(badges_raw), text=progress_text)
                continue

            badge_name = badge_raw.find_class('badge_info_title')[0].text
            level, xp = self.__get_level_and_xp(badge_raw)
            foil = int('Foil Badge' in badge_raw.find_class('badge_title')[0].text)
            game_id, pure_badge_page_id = self.__get_game_id_and_pure_badge_page_id(badge_raw)
            unlocked_datetime = self.__get_unlocked_datetime(badge_raw)

            badges += SteamBadges(
                name=badge_name, level=level, experience=xp, foil=foil, game_id=game_id,
                pure_badge_page_id=pure_badge_page_id, unlocked_at=unlocked_datetime
            )
            GenericUI.progress_completed(progress=index + 1, total=len(badges_raw), text=progress_text)

        return badges

    @staticmethod
    def __get_next_pages_urls(first_page: html.HtmlElement, first_page_url: str) -> list[str]:
        next_pages_links = []
        divs_with_link = first_page.find_class('pagelink')
        for div in divs_with_link:
            div.make_links_absolute(first_page_url)
            link = div.get('href')
            if link not in next_pages_links:
                next_pages_links.append(link)
        return next_pages_links

    @staticmethod
    def __get_game_name(badge_raw: html.HtmlElement) -> str:
        game_name_raw = badge_raw.find_class('badge_title')[0].text
        if 'Foil Badge' in game_name_raw:
            game_name_raw = game_name_raw.replace('- Foil Badge', '')
        game_name = game_name_raw.replace('\r', '').replace('\n', '').replace('\t', '').replace('\xa0', '')
        return game_name

    @staticmethod
    def __get_level_and_xp(badge_raw: html.HtmlElement) -> tuple[int, int]:
        level_and_xp_raw = badge_raw.find_class('badge_info_description')[0].getchildren()[1].text
        level_and_xp_raw_list = level_and_xp_raw.split()
        if 'Level' in level_and_xp_raw_list:
            level_index = level_and_xp_raw_list.index('Level')
            level_raw = level_and_xp_raw_list[level_index + 1]
            level = int(level_raw.replace(',', ''))
        else:
            level = None
        xp_index = level_and_xp_raw_list.index('XP')
        xp_raw = level_and_xp_raw_list[xp_index - 1]
        xp = int(xp_raw.replace(',', ''))
        return level, xp

    @staticmethod
    def __get_game_id_and_pure_badge_page_id(badge_raw: html.HtmlElement) -> tuple[Optional[int], Optional[int]]:
        badge_details_link = badge_raw.find_class('badge_row_overlay')[0].get('href')
        # badges not related to games (pure_badges) have '/badges/' in their url
        if '/badges/' in badge_details_link:
            game_id = None
            pure_badge_page_id = int(badge_details_link.split('/')[-1])
        else:
            game_market_id = badge_details_link.split('/')[-2]
            game_id = SteamGames.get_id_by_market_id(game_market_id)
            pure_badge_page_id = None
        return game_id, pure_badge_page_id

    @staticmethod
    def __get_unlocked_datetime(badge_raw: html.HtmlElement) -> str:
        unlckd_datetime_raw = badge_raw.find_class('badge_info_unlocked')[0].text
        unlckd_datetime_raw_list = unlckd_datetime_raw.replace('Unlocked', '').replace('@', '').replace(',', '').split()

        unlckd_time_raw = unlckd_datetime_raw_list.pop(-1)
        unlckd_time = unlckd_time_raw.replace('am', ' AM').replace('pm', ' PM')

        unlckd_date_raw_list = unlckd_datetime_raw_list
        if len(unlckd_date_raw_list) == 2:
            unlckd_date_raw_list.append(str(date.today().year))
        unlckd_date_raw = '-'.join(unlckd_date_raw_list)
        unlckd_date = unlckd_date_raw.replace(',', '')

        return f'{unlckd_date} {unlckd_time}'
