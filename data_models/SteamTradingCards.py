from repositories.SteamTradingCardsRepository import SteamTradingCardsRepository
from data_models.PandasDataModel import PandasDataModel
from data_models.PandasUtils import PandasUtils


class SteamTradingCards(PandasDataModel):

    __columns = ['id', 'game_id', 'set_number', 'name', 'url_name']

    def __init__(self, **data):
        cols = self.__get_columns()
        class_name = self.__class__.__name__
        super().__init__(class_name, cols, **data)

    @classmethod
    def __get_columns(cls) -> list:
        return cls.__columns.copy()

    @classmethod
    def __from_db(cls, data: list[tuple]):
        zipped_data = zip(*data)
        dict_data = dict(zip(cls.__columns, zipped_data))
        return cls(**dict_data)

    def save(self) -> None:
        saved = SteamTradingCards.get_all()
        new_and_update = PandasUtils.df_set_difference(self.df, saved.df, ['game_id', 'set_number'])
        if not new_and_update.empty:
            cols_to_insert = self.__get_columns()
            cols_to_insert.remove('id')
            zipped_data = PandasUtils.zip_df_columns(new_and_update, cols_to_insert)
            SteamTradingCardsRepository.insert_multiple_tcgs(zipped_data)

    @staticmethod
    def get_all() -> 'SteamTradingCards':
        data = SteamTradingCardsRepository.get_all()
        return SteamTradingCards.__from_db(data)
