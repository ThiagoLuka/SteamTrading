import pandas as pd

from data_models.PandasUtils import PandasUtils
from repositories.QueryBuilderPG import QueryBuilderPG
from db.DBController import DBController


class BasePersistenceModel:

    model_names: dict = {}

    def __init_subclass__(cls, **kwargs):
        BasePersistenceModel.model_names.update({kwargs['name']: cls})

    def __init__(self, data: list[dict]):
        self._df = pd.DataFrame(data)

    @property
    def df(self) -> pd.DataFrame:
        return self._df.copy()

    def save(self, *args, **kwargs) -> None:
        pass

    @staticmethod
    def _db_execute(query: str) -> None:
        return DBController.execute(query=query)

    @staticmethod
    def _insert_into_staging_query(df, staging_table_name) -> str:
        cols_to_insert = list(df.columns)
        zipped_data = PandasUtils.zip_df_columns(df, cols_to_insert)
        values = QueryBuilderPG.unzip_to_query_values_str(zipped_data)
        return f"""
            INSERT INTO {staging_table_name}
            ({', '.join(cols_to_insert)})
            VALUES {values};
        """
