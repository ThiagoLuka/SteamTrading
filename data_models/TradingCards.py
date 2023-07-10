from data_models.PandasDataModel import PandasDataModel
from data_models.PandasUtils import PandasUtils
from repositories.TradingCardsRepository import TradingCardsRepository


class TradingCards(
    PandasDataModel,
    tables={
        'item_booster_packs',
        'item_trading_cards'
    },
    columns={
        'default': ('id', 'item_steam_id', 'game_id', 'set_number', 'foil'),
        'item_booster_packs': ('id', 'item_steam_id', 'game_id', 'times_opened', 'foil_quantity'),
        'item_trading_cards': ('id', 'item_steam_id', 'game_id', 'set_number', 'foil'),
    },
    repository=TradingCardsRepository
):

    def __init__(self, table: str = 'default', **data):
        super().__init__(table, **data)

    def save(self):
        if self.columns == TradingCards._get_class_columns('item_booster_packs'):
            self.__save_boosters()
        elif self.columns == TradingCards._get_class_columns('item_trading_cards'):
            self.__save_cards()

    def __save_boosters(self):
        saved = TradingCards.get_all('item_booster_packs')
        new = PandasUtils.df_set_difference(self.df, saved.df, 'game_id')
        if new.empty:
            return
        cols_to_insert = ['item_steam_id', 'game_id']
        zipped_data = PandasUtils.zip_df_columns(new, cols_to_insert)
        TradingCardsRepository.insert_multiples('item_booster_packs', cols_to_insert, zipped_data)

    def __save_cards(self):
        saved = TradingCards.get_all('item_trading_cards')
        new = PandasUtils.df_set_difference(self.df, saved.df, ['game_id', 'set_number', 'foil'])
        if new.empty:
            return
        cols_to_insert = TradingCards._get_class_columns('item_trading_cards')
        cols_to_insert.remove('id')
        zipped_data = PandasUtils.zip_df_columns(new, cols_to_insert)
        TradingCardsRepository.insert_multiples('item_trading_cards', cols_to_insert, zipped_data)

    @staticmethod
    def get_all(table: str = 'item_trading_cards', columns: list = None):
        if not columns:
            columns = TradingCards._get_class_columns(table)
        data = TradingCardsRepository.get_all(table, columns)
        return TradingCards._from_db(table, data)

    @staticmethod
    def update_booster_packs_opened(game_id: int, times_opened: int,foil_quantity: int) -> None:
        TradingCardsRepository.update_booster_packs_opened(
            game_id=game_id, times_opened=times_opened,foil_quantity=foil_quantity
        )
