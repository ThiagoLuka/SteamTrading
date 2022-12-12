import pandas as pd


class PandasDataModel:

    def __init__(self, child_name: str, model_columns, **data):
        self.__child_class_name = child_name

        if not data:
            self.__df = pd.DataFrame(columns=model_columns)
            return

        for column in data.keys():
            if column not in model_columns:
                raise IndexError(f'Trying to set {child_name} with invalid data')

        self.__df = pd.DataFrame(data.values(), index=list(data.keys())).T
        self.__df = self.__df.reindex(columns=model_columns)

    def __add__(self, other):
        if other.__class__.__name__ == self.__child_class_name:
            self.__df = pd.concat([self.df, other.df], ignore_index=True)
            self.__df.drop_duplicates(inplace=True)
            return self
        raise TypeError(f'Trying to sum data model with unknown type')

    def __iter__(self):
        for index, row in self.__df.iterrows():
            yield dict(row)

    @property
    def df(self) -> pd.DataFrame:
        return self.__df.copy()

    @property
    def empty(self) -> bool:
        return self.__df.empty

    @classmethod
    def __get_columns(cls) -> list:
        pass

    def save(self, *external_data) -> None:
        pass
