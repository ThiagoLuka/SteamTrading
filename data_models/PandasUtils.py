import pandas as pd
from typing import Union


class PandasUtils:

    @staticmethod
    def df_set_difference(df: pd.DataFrame, other_df: pd.DataFrame, columns: Union[str, list[str]]) -> pd.DataFrame:
        if isinstance(columns, str):
            return df[~df[columns].isin(other_df[columns])]
        if isinstance(columns, list):
            this_set = set(map(tuple, df[columns].values))
            other_set = set(map(tuple, other_df[columns].values))
            set_diff = this_set.difference(other_set)
            df_diff = pd.DataFrame(data=set_diff, columns=columns)
            return df.merge(df_diff)

    @staticmethod
    def zip_df_columns(df: pd.DataFrame, columns: list[str] = None) -> zip:
        columns_values = []
        for column in columns:
            columns_values.append(tuple(df[column]))
        return zip(*columns_values)

    @staticmethod
    def format_only_positive_int_with_nulls(df: pd.DataFrame, columns: Union[str, list[str]]) -> pd.DataFrame:
        if isinstance(columns, str):
            df[[columns]] = df[[columns]].fillna(-1)
            df[[columns]] = df[[columns]].astype(int)
            df[[columns]] = df[[columns]].astype(str)
            df[[columns]] = df[[columns]].replace('-1', None)
            return df
        if isinstance(columns, list):
            for column in columns:
                df[[column]] = df[[column]].fillna(-1)
                df[[column]] = df[[column]].astype(int)
                df[[column]] = df[[column]].astype(str)
                df[[column]] = df[[column]].replace('-1', None)
            return df
