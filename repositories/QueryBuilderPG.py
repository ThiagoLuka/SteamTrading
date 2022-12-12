

class QueryBuilderPG:

    @staticmethod
    def unzip_to_values_query_str(zipped_data: zip) -> str:
        rows = []
        for row in zipped_data:
            values = []
            for value in row:
                if QueryBuilderPG.__check_null(str(value)):
                    values.append('NULL')
                else:
                    value = QueryBuilderPG.sanitize_string(str(value))
                    values.append(f"'{value}'")
            rows.append(f"({', '.join(values)})")
        values_query_str = ', '.join(rows)
        return values_query_str

    @staticmethod
    def sanitize_string(string: str) -> str:
        if "'" in string:
            string = string.replace("'", "''")
        return string

    @staticmethod
    def cols_to_insert_list_to_str(cols_list: list[str]) -> str:
        return f"({', '.join(cols_list)})"

    @staticmethod
    def cols_to_get_list_to_str(cols_list: list[str]) -> str:
        return f"{', '.join(cols_list)}"

    @staticmethod
    def __check_null(string: str) -> bool:
        return string == 'None'
