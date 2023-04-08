import pandas as pd


class PandasDataModel:

    _models_info: dict = {}

    def __init_subclass__(cls, **kwargs):
        cls._models_info.update({
            cls.__name__: {**kwargs}
        })

    def __init__(self, table: str, **data):
        model_columns = self._get_class_columns(table)

        if not data:
            self.__df = pd.DataFrame(columns=model_columns)
            return

        self.__check_data_for_invalid_columns(model_columns, data)

        self.__df = pd.DataFrame(data.values(), index=list(data.keys())).T
        self.__df = self.__df.reindex(columns=model_columns)

    def __add__(self, other):
        if not other.__class__.__name__ == self.__class__.__name__:
            raise TypeError(f"Invalid sum: {self.__class__.__name__} doesn't sum up with {other.__class__.__name__}")
        if not self.columns == other.columns:
            raise TypeError(f"Invalid sum: Columns don't match, same class but different tables.")
        self.__df = pd.concat([self.df, other.df], ignore_index=True)
        self.__df.drop_duplicates(inplace=True)
        return self

    def __radd__(self, other):
        return self if other == 0 else self.__add__(other)

    def __iter__(self):
        for index, row in self.__df.iterrows():
            yield dict(row)

    @property
    def df(self) -> pd.DataFrame:
        return self.__df.copy()

    @property
    def empty(self) -> bool:
        return self.__df.empty

    @property
    def columns(self) -> list:
        return list(self.df.columns)

    @classmethod
    def _get_class_columns(cls, table: str = 'default') -> list:
        return list(cls._models_info[cls.__name__]['columns'][table])

    @classmethod
    def _from_db(cls, table: str, db_data: list[tuple]) -> 'PandasDataModel':
        data_zipped = zip(*db_data)
        data_dict = dict(zip(cls._get_class_columns(table), data_zipped))
        return cls(table, **data_dict)

    def save(self, *external_data) -> None:
        pass

    def __check_data_for_invalid_columns(self, model_columns: list, data: dict) -> None:
        for column in data.keys():
            if column not in model_columns:
                raise IndexError(f'{self.__class__.__name__} does not accept {column} as data')
