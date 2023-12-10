import psycopg2

from utils.Singleton import Singleton


class DBController(metaclass=Singleton):

    def __init__(self):
        self.__check_db_access()

    @staticmethod
    def execute(query: str, get_result: bool = False):
        with DBController.__get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            if get_result:
                return cursor.fetchall()

    @staticmethod
    def __check_db_access():
        try:
            DBController.__get_connection()
        except Exception as e:
            print(e)

    @staticmethod
    def __get_connection():
        return psycopg2.connect(DBController.__get_standard_postgres_conn_str())

    @staticmethod
    def __get_standard_postgres_conn_str() -> str:
        conn_str: str = ''
        with open('db_user.txt', 'r') as file:
            for line in file.readlines():
                conn_str += line.replace('\n', ' ')
        return conn_str
