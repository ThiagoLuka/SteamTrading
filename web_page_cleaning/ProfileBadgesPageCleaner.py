from datetime import date
from typing import Union

from lxml import html


class ProfileBadgesPageCleaner:

    def __init__(self, page_string: bytes):
        self.__page: html.HtmlElement = html.fromstring(page_string)
        self.__raw_badges: html.HtmlElement = self.__page.find_class('badge_row')

    @property
    def raw_badges(self):
        return self.__raw_badges

    def get_number_of_pages(self) -> int:
        if not self.__page.find_class('profile_paging'):
            return 1  # the current one
        divs_with_link_to_next_page: list[html.HtmlElement] = self.__page.find_class('pagelink')
        # there are two paging elements in this webpage
        # so the number of divs with a link to other pages is duplicated
        number_of_pages: int = 1 + int(len(divs_with_link_to_next_page)/2)
        return number_of_pages

    class BadgeCleaner:

        def __init__(self, badge_raw: html.HtmlElement):
            self.badge_raw = badge_raw
            self.badge_details_url = badge_raw.find_class('badge_row_overlay')[0].get('href')

        def is_game_badge(self) -> bool:
            # badges not related to games (pure_badges) have '/badges/' in their url
            return '/badges/' not in self.badge_details_url

        def is_completed(self) -> bool:
            # incomplete badges have a 'badge_emtpy' div
            return not bool(self.badge_raw.find_class('badge_empty'))

        def have_info(self) -> bool:
            # some badges have no info whatsoever. It's a bit weird, and they should be ignored as well
            # those badges have no children under the 'badge_current' div
            return bool(self.badge_raw.find_class('badge_current')[0].getchildren())

        def get_market_id(self) -> Union[str, None]:
            if not self.is_game_badge():
                return None
            return self.badge_details_url.split('/')[-2]

        def get_game_name(self) -> str:
            game_name_raw = self.badge_raw.find_class('badge_title')[0].text
            if 'Foil Badge' in game_name_raw:
                game_name_raw = game_name_raw.replace('- Foil Badge', '')
            game_name = game_name_raw.replace('\r', '').replace('\n', '').replace('\t', '').replace('\xa0', '')
            return game_name

        def get_badge_name(self) -> str:
            return self.badge_raw.find_class('badge_info_title')[0].text

        def get_level_and_xp(self) -> tuple[int, int]:
            level_and_xp_raw = self.badge_raw.find_class('badge_info_description')[0].getchildren()[1].text
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

        def get_foil(self) -> int:
            return int('Foil Badge' in self.badge_raw.find_class('badge_title')[0].text)

        def get_pure_badge_page_id(self) -> Union[int, None]:
            if self.is_game_badge():
                return None
            return int(self.badge_details_url.split('/')[-1])

        def get_unlocked_datetime(self) -> str:
            unlckd_datetime_raw = self.badge_raw.find_class('badge_info_unlocked')[0].text
            unlckd_datetime_raw_list = unlckd_datetime_raw.replace('Unlocked', '').replace('@', '').replace(',',
                                                                                                            '').split()

            unlckd_time_raw = unlckd_datetime_raw_list.pop(-1)
            unlckd_time = unlckd_time_raw.replace('am', ' AM').replace('pm', ' PM')

            unlckd_date_raw_list = unlckd_datetime_raw_list
            if len(unlckd_date_raw_list) == 2:
                unlckd_date_raw_list.append(str(date.today().year))
            unlckd_date_raw = '-'.join(unlckd_date_raw_list)
            unlckd_date = unlckd_date_raw.replace(',', '')

            return f'{unlckd_date} {unlckd_time}'