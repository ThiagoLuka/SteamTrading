import pandas as pd

from repositories.SteamBadgesRepository import SteamBadgesRepository
from data_models.PandasDataModel import PandasDataModel
from data_models.PandasUtils import PandasUtils
from data_models.MathUtils import MathUtils


class SteamBadges(
    PandasDataModel,
    tables={
        'game_badges',
        'pure_badges',
        'user_badges',
    },
    columns={
        'default': ('id', 'name', 'level', 'experience', 'foil', 'game_id', 'pure_badge_page_id', 'unlocked_at'),
        'game_badges': ('id', 'game_id', 'name', 'level', 'foil'),
        'pure_badges': ('id', 'page_id', 'name'),
        'user_badges': ('id', 'user_id', 'game_badge_id', 'pure_badge_id', 'experience', 'unlocked_at', 'active'),
    },
    repository=SteamBadgesRepository
):

    def __init__(self, table: str = 'default', **data):
        super().__init__(table, **data)

    def save(self, user_id: int) -> None:
        game_badges = self.df[self.df['pure_badge_page_id'].isna()]
        self.__save_by_type(
            'game', game_badges, check_diff_on_columns=['game_id', 'level', 'foil']
        )

        pure_badges = self.df[~self.df['pure_badge_page_id'].isna()]
        pure_badges.rename(columns={'pure_badge_page_id': 'page_id'}, inplace=True)
        self.__save_by_type(
            'pure', pure_badges, check_diff_on_columns=['page_id', 'name']
        )

        user_badges = self.__user_badges_with_other_tables_references(user_id)
        self.__save_by_type(
            'user', user_badges, check_diff_on_columns=['user_id', 'game_badge_id', 'pure_badge_id']
        )

        self.__update_inactive_badges(user_id)

    @staticmethod
    def __save_by_type(badge_type: str, new: pd.DataFrame, check_diff_on_columns: list[str]) -> None:
        saved = SteamBadges.get_all(badge_type).df
        if badge_type == 'user':
            saved = PandasUtils.format_only_positive_int_with_nulls(saved, ['game_badge_id', 'pure_badge_id'])
        to_save = PandasUtils.df_set_difference(new, saved, check_diff_on_columns)
        if to_save.empty:
            return
        cols_to_insert = SteamBadges._get_class_columns(f'{badge_type}_badges')
        cols_to_insert.remove('id')
        zipped_data = PandasUtils.zip_df_columns(to_save, cols_to_insert)
        if badge_type == 'game':
            SteamBadgesRepository.upsert_multiple_game_badges(zipped_data, cols_to_insert)
        if badge_type == 'pure' or badge_type == 'user':
            SteamBadgesRepository.insert_multiple_badges(badge_type, zipped_data, cols_to_insert)

    def __user_badges_with_other_tables_references(self, user_id: int) -> pd.DataFrame:
        saved_game_badges = self.get_all('game').df
        saved_game_badges.rename(columns={'id': 'game_badge_id'}, inplace=True)
        user_game_badges = pd.merge(self.df, saved_game_badges)

        saved_pure_badges = self.get_all('pure').df
        saved_pure_badges.rename(columns={'id': 'pure_badge_id'}, inplace=True)
        user_pure_badges = pd.merge(self.df, saved_pure_badges)

        user_badges = pd.concat([user_game_badges, user_pure_badges], ignore_index=True)
        user_badges['user_id'] = user_id
        user_badges['active'] = 1
        user_badges = user_badges[SteamBadges._get_class_columns('user_badges')]
        user_badges = PandasUtils.format_only_positive_int_with_nulls(user_badges, ['game_badge_id', 'pure_badge_id'])
        return user_badges

    def __update_inactive_badges(self, user_id):
        badges_id_to_deactivate: list = []

        game_badges_to_inactivate = self.__user_game_badges_id_to_deactivate(user_id)
        badges_id_to_deactivate.extend(game_badges_to_inactivate)

        pure_badges_to_inactivate = self.__user_pure_badges_id_to_deactivate(user_id)
        badges_id_to_deactivate.extend(pure_badges_to_inactivate)

        SteamBadgesRepository.set_user_badges_to_inactive(badges_id_to_deactivate)

    @staticmethod
    def __user_game_badges_id_to_deactivate(user_id: int) -> list:
        cols_to_get_game = ['user_badges.id', 'game_id', 'level', 'foil']
        user_game_badges = SteamBadgesRepository.get_user_badges_with_type_details(user_id, 'game', cols_to_get_game)
        df_game = pd.DataFrame(data=user_game_badges, columns=cols_to_get_game)
        df_game.drop(df_game[df_game['foil']].index, inplace=True)
        sorted_by_higher_level = df_game.sort_values(by='level', ascending=False)
        only_lower_lvls = sorted_by_higher_level[sorted_by_higher_level['game_id'].duplicated(keep='first')]
        return list(only_lower_lvls['user_badges.id'])

    @staticmethod
    def __user_pure_badges_id_to_deactivate(user_id: int) -> list:
        cols_to_get_pure = ['user_badges.id', 'page_id', 'unlocked_at']
        user_pure_badges = SteamBadgesRepository.get_user_badges_with_type_details(user_id, 'pure', cols_to_get_pure)
        df_pure = pd.DataFrame(data=user_pure_badges, columns=cols_to_get_pure)
        pure_sorted_by_most_recent = df_pure.sort_values(by='unlocked_at', ascending=False)
        only_least_recent = pure_sorted_by_most_recent[pure_sorted_by_most_recent['page_id'].duplicated(keep='first')]
        return list(only_least_recent['user_badges.id'])

    @staticmethod
    def get_all(badge_type: str = 'user') -> 'SteamBadges':
        cols = SteamBadges._get_class_columns(f'{badge_type}_badges')
        data = SteamBadgesRepository.get_all(badge_type, cols)
        return SteamBadges._from_db(f'{badge_type}_badges', data)

    @staticmethod
    def get_current_by_user(user_id: int) -> 'SteamBadges':
        cols = SteamBadges._get_class_columns('user_badges')
        data = SteamBadgesRepository.get_all_active_by_user_id(user_id, cols)
        return SteamBadges._from_db('user_badges', data)

    @staticmethod
    def get_user_level(user_id: int) -> int:
        # Steam levels are earned by raising experience. The first 10 levels are earned with 100xp each
        # From level 10-20 one needs 200xp for each, between 20-30 300xp each, and so it goes on
        # Following this rule and using a little math, one could know the steam level given a certain experience
        # by figuring out that the level could be split into the tens, which follow a triangular sequence times 1000,
        # and the units, which follow a linear progression of the nth element of the triangular sequence time 100
        # That's why this weird calculation that comes after works
        user_xp: int = SteamBadgesRepository.get_user_total_experience(user_id)
        thousand_xp_to_this_ten, level_tens = MathUtils.highest_triangular_number_and_nth_term_below(user_xp // 1000)
        user_xp_units = user_xp - (thousand_xp_to_this_ten * 1000)
        level_units = user_xp_units // ((level_tens + 1) * 100)
        level = 10 * level_tens + level_units
        return level
