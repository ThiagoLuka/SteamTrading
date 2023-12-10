import pandas as pd

from data_models.PandasUtils import PandasUtils
from data_models.QueryBuilderPG import QueryBuilderPG
from data_models.db.DBController import DBController


class BasePersistenceModel:

    models: dict = {}

    def __init_subclass__(cls, **kwargs):
        BasePersistenceModel.models.update({kwargs['name']: cls})

    def __init__(self, data: list[dict] = None):
        self._df = pd.DataFrame(data)

    @property
    def df(self) -> pd.DataFrame:
        return self._df.copy()

    def save(self, *args, **kwargs) -> None:
        pass

    @staticmethod
    def table_name(table_type: str) -> str:
        pass

    @staticmethod
    def table_columns(table_type: str) -> list:
        pass

    @staticmethod
    def _db_execute(query: str) -> None:
        return DBController.execute(query=query)

    def _insert_into_staging(self, df, staging_table_name) -> None:
        cols_to_insert = list(df.columns)
        zipped_data = PandasUtils.zip_df_columns(df, cols_to_insert)
        values = QueryBuilderPG.unzip_to_query_values_str(zipped_data)
        self._db_execute(f"""
            INSERT INTO {staging_table_name}
            ({', '.join(cols_to_insert)})
            VALUES {values};
        """)
