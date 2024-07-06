import logging 
import pandas as pd
from sqlalchemy import text

from src.context import Context 
from src.utils.timing import timing

class SqlHelper: 

    def __init__(
            self,
            context : Context, 
    ):
        self._context = context
        self._log = context.log
        self.db_tables = pd.read_sql("SELECT table_name FROM information_schema.tables", 
                                  con=self._context.db_con)["table_name"].tolist()

    def read_sql_data(self, table_name):
        try:
            return pd.read_sql(table_name, con=self._context.db_con)
        except Exception as e:
            raise Exception(f"table name does not exist in SQL : {table_name}", e)
        
    def alter_table(self,table_name, column_name, column_type):
        pd.read_sql(f"ALTER TABLE \"{table_name}\" ADD COLUMN \
                                     {column_name} {column_type}")
        
    def get_table_rows_count(self, table_name):
        return pd.read_sql(f"SELECT COUNT(*) FROM \"{table_name}\"", 
                           con=self._context.db_con)["count"].values[0]
    
    def get_table_cols_count(self, table_name):
        return pd.read_sql(f"SELECT * FROM information_schema.columns WHERE table_name = '{table_name}'", 
                           con=self._context.db_con).shape[0]
    
    def drop_table(self, table_name):
        with self._context.db_con.connect() as conn:
            conn.execute(text(f"DROP TABLE \"{table_name}\""))
    
    def write_to_sql(self, dataframe, table_name, if_exists="append"):
        dataframe.to_sql(table_name, con=self._context.db_con, if_exists=if_exists, chunksize = 50000, index=False)
    
    @timing
    def write_sql_data(self, dataframe, table_name, if_exists=None):
        if table_name in self.db_tables:
            col_count = self.get_table_cols_count(table_name)
            row_count = self.get_table_rows_count(table_name)

            if if_exists:
                self._log.info(f"TABLE EXISTS AND WILL BE {if_exists.upper()} INTO SQL : {table_name} ......")
                self.write_to_sql(dataframe, table_name, if_exists=if_exists)
                self._log.info(f"WRITTEN INTO SQL : {table_name}")
            else:
                if dataframe.shape[1] != col_count :
                    self._log.info(f"{table_name} - WILL BE DELETED TO ADD {col_count - dataframe.shape[1]} new columns")
                    self.write_to_sql(dataframe, table_name, if_exists="replace")
                    self._log.info(f"WRITTEN INTO SQL : {table_name}")
                elif dataframe.shape[0] > row_count :
                    self._log.info(f"INSERT {row_count - dataframe.shape[0]} NEW OBSERVATIONS TO {table_name}")
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
            nbr_elements = pd.read_sql(f"SELECT \"{column}\" FROM \"{table_name}\" WHERE \"{column}\" IN {values}", 
                                    con=self._context.db_con)
            with self._context.db_con.begin() as conn:
                conn.execute(text(f"""DELETE FROM \"{table_name}\"
                                WHERE \"{column}\" IN {values}"""))
            self._log.info(f"REMOVED {nbr_elements.shape} OBS FROM TABLE {table_name}")
        else:
            self._log.warning(f"{table_name} does not exist in the Database")
