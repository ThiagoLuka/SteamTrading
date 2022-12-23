import pandas as pd

from repositories.SteamTradingCardsRepository import SteamTradingCardsRepository
from data_models.PandasDataModel import PandasDataModel
from data_models.PandasUtils import PandasUtils


class SteamTradingCards(PandasDataModel):

    __columns = ['id', 'game_id', 'set_number', 'name', 'url_name']
    __columns_to_description = ['trading_card_id', 'description_id', 'foil']

    def __init__(self, table: str = 'trading_cards', **data):
        cols = self.__get_columns(table)
        class_name = self.__class__.__name__
        super().__init__(class_name, cols, **data)

    @classmethod
    def __get_columns(cls, table: str = 'trading_cards') -> list:
        cols = {
            'trading_cards': cls.__columns.copy(),
            'trading_cards_to_item_descripts': cls.__columns_to_description.copy(),
        }.get(table, [])
        return cols

    @classmethod
    def __from_db(cls, table: str, db_data: list[tuple]):
        zipped_data = zip(*db_data)
        dict_data = dict(zip(cls.__get_columns(table), zipped_data))
        return cls(table, **dict_data)

    def save(self) -> None:
        saved = SteamTradingCards.get_all()
        new_and_update = PandasUtils.df_set_difference(self.df, saved.df, ['game_id', 'set_number'])
        if not new_and_update.empty:
            cols_to_insert = self.__get_columns()
            cols_to_insert.remove('id')
            zipped_data = PandasUtils.zip_df_columns(new_and_update, cols_to_insert)
            SteamTradingCardsRepository.insert_multiple_trading_cards(zipped_data, cols_to_insert)

    @staticmethod
    def get_all(table: str = 'trading_cards') -> 'SteamTradingCards':
        cols = SteamTradingCards.__get_columns(table)
        data = SteamTradingCardsRepository.get_all(table, cols)
        return SteamTradingCards.__from_db(table, data)

    @staticmethod
    def set_relationship_with_item_descripts(item_descripts: pd.DataFrame) -> None:
        trading_cards = SteamTradingCards.get_all().df
        trading_cards.rename(columns={'id': 'trading_card_id'}, inplace=True)
        item_descripts.rename(columns={'id': 'description_id'}, inplace=True)
        item_descripts = item_descripts[item_descripts['type_id'] == 2].copy()

        descripts_foil = item_descripts[item_descripts['url_name'].str.contains('Foil')].copy()
        descripts_foil['foil'] = 1
        descripts_not_foil = item_descripts.drop(labels=list(descripts_foil.index)).copy()
        descripts_not_foil['foil'] = 0

        tcs = trading_cards[['trading_card_id', 'game_id', 'url_name']]

        # foil cards relationship is different
        descripts_not_foil = descripts_not_foil[['description_id', 'foil', 'game_id', 'url_name']]
        not_foil = pd.merge(tcs, descripts_not_foil)

        descripts_foil = descripts_foil[['description_id', 'foil', 'game_id', 'url_name']]
        descripts_foil['original_url_name'] = descripts_foil['url_name']
        descripts_foil['url_name'] = descripts_foil['url_name'].str.replace('%20%28Foil%29', '')
        descripts_foil['url_name'] = descripts_foil['url_name'].str.replace('Foil%20', '')
        foil = pd.merge(tcs, descripts_foil)
        foil.drop(columns='url_name', inplace=True)
        foil.rename(columns={'original_url_name': 'url_name'}, inplace=True)

        full_new_relationship = pd.concat([not_foil, foil], ignore_index=True)
        relevant_cols = SteamTradingCards.__get_columns('trading_cards_to_item_descripts')
        full_new_relationship = full_new_relationship[relevant_cols].copy()

        saved = SteamTradingCards.get_all('trading_cards_to_item_descripts')
        to_save = PandasUtils.df_set_difference(full_new_relationship, saved.df, relevant_cols)
        if not to_save.empty:
            zipped_data = PandasUtils.zip_df_columns(to_save, relevant_cols)
            SteamTradingCardsRepository.insert_trading_cards_to_item_descripts(zipped_data, relevant_cols)
