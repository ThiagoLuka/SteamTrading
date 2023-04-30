

class QueryBuilderPG:

    @staticmethod
    def unzip_to_query_values_str(zipped_data: zip) -> str:
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
    def __check_null(string: str) -> bool:
        return string == 'None' or string == 'nan'
