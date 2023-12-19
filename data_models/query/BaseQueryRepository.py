from typing import Union

from data_models.db.DBController import DBController


class BaseQueryRepository:

    @staticmethod
    def query_tables(table_type: str) -> str:
        return {
            # 'inventory':
        }.get(table_type)

    @staticmethod
    def _db_execute(query: str) -> Union[list[tuple], int]:
        return DBController.execute(query=query, get_result=True)
