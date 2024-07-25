import json
import pandas as pd
from sqlalchemy import text

from src.context import Context
from src.utils.timing import timing


class SqlHelper:

    def __init__(
        self,
        context: Context,
    ):
        self._context = context
        self._log = context.log

        with self._context.db_con.connect() as conn:
            self.db_tables = pd.read_sql(
                "SELECT table_name FROM information_schema.tables", con=conn.connection
            )
        self.db_tables = self.db_tables["table_name"].tolist()

    def read_sql_data(self, table_name, params=None):
        try:
            return pd.read_sql(table_name, con=self._context.db_con, params=params)
        except Exception as e:
            raise Exception(f"table name does not exist in SQL : {table_name}", e)

    def alter_table(self, table_name, column_name, column_type):
        pd.read_sql(
            f'ALTER TABLE "{table_name}" ADD COLUMN \
                                     {column_name} {column_type}'
        )

    def get_table_rows_count(self, table_name):
        return pd.read_sql(
            f'SELECT COUNT(*) FROM "{table_name}"', con=self._context.db_con
        )["count"].values[0]

    def get_table_cols_count(self, table_name):
        return pd.read_sql(
            f"SELECT * FROM information_schema.columns WHERE table_name = '{table_name}'",
            con=self._context.db_con,
        ).shape[0]

    def drop_table(self, table_name):
        with self._context.db_con.connect() as conn:
            conn.execute(text(f'DROP TABLE "{table_name}"'))

    def write_to_sql(self, dataframe, table_name, if_exists="append"):
        dataframe.to_sql(
            table_name,
            con=self._context.db_con,
            if_exists=if_exists,
            chunksize=50000,
            index=False,
        )

    @timing
    def write_sql_data(self, dataframe, table_name, if_exists=None):
        if table_name in self.db_tables:
            col_count = self.get_table_cols_count(table_name)
            row_count = self.get_table_rows_count(table_name)

            if if_exists:
                self._log.info(
                    f"TABLE EXISTS AND WILL BE {if_exists.upper()} INTO SQL : {table_name} ......"
                )
                self.write_to_sql(dataframe, table_name, if_exists=if_exists)
                self._log.info(f"WRITTEN INTO SQL : {table_name}")
            else:
                if dataframe.shape[1] != col_count:
                    self._log.info(
                        f"{table_name} - WILL BE DELETED TO ADD {col_count - dataframe.shape[1]} new columns"
                    )
                    self.write_to_sql(dataframe, table_name, if_exists="replace")
                    self._log.info(f"WRITTEN INTO SQL : {table_name}")
                elif dataframe.shape[0] > row_count:
                    self._log.info(
                        f"INSERT {row_count - dataframe.shape[0]} NEW OBSERVATIONS TO {table_name}"
                    )
                    self.write_to_sql(dataframe, table_name)
                    self._log.info(f"WRITTEN INTO SQL : {table_name}")
                else:
                    self._log.info(f"DATA {table_name} IS ALREADY UP TO DATE")
        else:
            self._log.info(f"WRITTING INTO SQL : {table_name} ......")
            self.write_to_sql(dataframe, table_name)
            self._log.info(f"WRITTEN INTO SQL : {table_name}")

    @timing
    def remove_rows_sql_data(self, values, column, table_name):
        if table_name in self.db_tables:
            values = str(tuple(values))
            nbr_elements = pd.read_sql(
                f"""SELECT {column} FROM {table_name} WHERE {column} IN {values} """,
                con=self._context.db_con,
            )
            with self._context.db_con.begin() as conn:
                conn.execute(
                    f"""DELETE FROM {table_name}
                            WHERE {column} IN {values}"""
                )
            self._log.info(f"REMOVED {nbr_elements.shape} OBS FROM TABLE {table_name}")
        else:
            self._log.warning(f"{table_name} does not exist in the Database")

    def insert_raw_to_table(self, unique_id_col: str, row_dict: dict, table_name: str):

        if table_name in self.db_tables:

            keys_to_string = ", ".join([f'"{x}"' for x in row_dict.keys()])
            values = tuple(
                json.dumps(value) if isinstance(value, dict) else value
                for value in row_dict.values()
            )
            placeholders = ", ".join(["%s"] * len(values))
            update_columns = ", ".join(
                [
                    (
                        f'"{k}" = \'{json.dumps(v).replace("\'", "\'\'")}\''
                        if isinstance(v, (list, dict))
                        else f'"{k}" = \'{str(v).replace("\'", "\'\'")}\''
                    )
                    for k, v in list(row_dict.items())
                    if k != unique_id_col
                ]
            )

            query = f"""INSERT INTO {table_name} ({keys_to_string})
                        VALUES ({placeholders})
                        ON CONFLICT ({unique_id_col})
                        DO UPDATE SET {update_columns}"""

            with self._context.db_con.begin() as conn:
                try:
                    conn.execute(query, values)

                except Exception as e:
                    if "value violates unique constraint" in str(e):
                        self._log.warning(f"Row already saved in db {table_name}")
                    else:
                        self._log.error(f"Something wrong happened {e}")
                finally:
                    pass

    @timing
    def create_table_if_not_exist(self, table_schema):
        # TODO

        col_tuple = ""
        features = table_schema.schema()["properties"]

        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_schema.__tablename__} (
                id_item TEXT,
                methode TEXT,
                input TEXT,
                answer TEXT,
                date TEXT,
                french_title TEXT,
                french_description TEXT,
                english_title TEXT,
                english_description TEXT,
                object_category TEXT,
                number_objects_described TEXT
            )
            """

        with self._context.db_con.begin() as conn:
            conn.execute(create_table_query)
