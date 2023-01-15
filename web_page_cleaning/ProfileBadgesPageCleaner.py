from datetime import date
from typing import Optional

from lxml import html

from data_models.SteamGames import SteamGames
from data_models.SteamBadges import SteamBadges


class ProfileBadgesPageCleaner:

    def __init__(self, page_string: bytes):
        self.__page: html.HtmlElement = html.fromstring(page_string)
        self.__badges_raw: html.HtmlElement = self.__page.find_class('badge_row')

    def get_number_of_pages(self) -> int:
        if not self.__page.find_class('profile_paging'):
            return 1  # the current one
        divs_with_link_to_next_page: list[html.HtmlElement] = self.__page.find_class('pagelink')
        # there are two paging elements in this webpage
        # so the number of divs with a link to other pages is duplicated
        number_of_pages: int = 1 + int(len(divs_with_link_to_next_page)/2)
        return number_of_pages

    def to_games(self):
        market_ids = []
        game_names = []

        for badge_raw in self.__badges_raw:
            # badges not related to games (pure_badges) have '/badges/' in their url and should be ignored
            badge_details_link = badge_raw.find_class('badge_row_overlay')[0].get('href')
            if '/badges/' in badge_details_link:
                continue

            market_ids.append(badge_details_link.split('/')[-2])
            game_names.append(self.__get_game_name(badge_raw))

        games = SteamGames(name=game_names, market_id=market_ids)
        return games

    def to_badges(self):
        badge_names = []
        levels = []
        xps = []
        foils = []
        game_ids = []
        pure_badge_page_ids = []
        unlocked_datetimes = []

        for badge_raw in self.__badges_raw:

            # not completed badges are ignored
            if badge_raw.find_class('badge_empty'):
                continue

            # some badges have no info whatsoever. It's a bit weird, and they should be ignored as well
            if not badge_raw.find_class('badge_current')[0].getchildren():
                continue

            badge_names.append(badge_raw.find_class('badge_info_title')[0].text)
            level, xp = self.__get_level_and_xp(badge_raw)
            levels.append(level)
            xps.append(xp)
            foils.append(int('Foil Badge' in badge_raw.find_class('badge_title')[0].text))
            game_id, pure_badge_page_id = self.__get_game_id_and_pure_badge_page_id(badge_raw)
            game_ids.append(game_id)
            pure_badge_page_ids.append(pure_badge_page_id)
            unlocked_datetimes.append(self.__get_unlocked_datetime(badge_raw))

        badges = SteamBadges(
            name=badge_names, level=levels, experience=xps, foil=foils, game_id=game_ids,
            pure_badge_page_id=pure_badge_page_ids, unlocked_at=unlocked_datetimes
        )
        return badges

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
