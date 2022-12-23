import pandas as pd

from repositories.SteamBadgesRepository import SteamBadgesRepository
from data_models.PandasDataModel import PandasDataModel
from data_models.PandasUtils import PandasUtils


class SteamBadges(PandasDataModel):

    __columns = ['id', 'name', 'level', 'experience', 'foil', 'game_id', 'pure_badge_page_id', 'unlocked_at']
    __columns_game = ['id', 'game_id', 'name', 'level', 'foil']
    __columns_pure = ['id', 'page_id', 'name']
    __columns_user = ['id', 'user_id', 'game_badge_id', 'pure_badge_id', 'experience', 'unlocked_at', 'active']

    def __init__(self, badge_type: str = '', **data):
        cols = self.__get_columns(badge_type)
        class_name = self.__class__.__name__
        super().__init__(class_name, cols, **data)

    @classmethod
    def __get_columns(cls, badge_type: str = ''):
        cols = {
            '': cls.__columns.copy(),
            'game': cls.__columns_game.copy(),
            'pure': cls.__columns_pure.copy(),
            'user': cls.__columns_user.copy(),
        }.get(badge_type, [])
        return cols

    @classmethod
    def __from_db(cls, badge_type: str, db_data: list[tuple]):
        zipped_data = zip(*db_data)
        dict_data = dict(zip(cls.__get_columns(badge_type), zipped_data))
        return cls(badge_type, **dict_data)

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

    @classmethod
    def __save_by_type(cls, badge_type: str, new: pd.DataFrame, check_diff_on_columns: list[str]) -> None:
        saved = cls.get_all(badge_type).df
        if badge_type == 'user':
            saved = PandasUtils.format_only_positive_int_with_nulls(saved, ['game_badge_id', 'pure_badge_id'])
        to_save = PandasUtils.df_set_difference(new, saved, check_diff_on_columns)
        if not to_save.empty:
            cols_to_insert = cls.__get_columns(badge_type)
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
        user_badges = user_badges[self.__get_columns('user')]
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
        cols = SteamBadges.__get_columns(badge_type)
        data = SteamBadgesRepository.get_all(badge_type, cols)
        return SteamBadges.__from_db(badge_type, data)
