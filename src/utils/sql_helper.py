import logging 
import pandas as pd

from src.context import Context 
from src.utils.timing import timing

class SqlHelper: 

    def __init__(
            self,
            context : Context, 
    ):
        self._context = context
        self._sql_table_names = self.get_table_names()
        self._tables_in_sql = self.get_sql_loaded_tables()
        self.db_tables = pd.read_sql("SELECT table_name FROM information_schema.tables", 
                                  con=self._context.db_con)["table_name"].tolist()

    def get_table_names(self):
        
        sql_table_names = []
        for granularity in self._config.flat_file.insee.keys():
            for data_name, values in self._config.flat_file.insee[granularity].items():

                try:
                    sql_table_names.append(values.table_name)
                except Exception as e:
                    self._log.warning(f"{data_name} does not have any table name, \
                                    careful since the table will be loaded in SQL DATABASE")
        
        return sql_table_names
    
    def get_sql_loaded_tables(self):
        return list(set(self.db_tables).intersection(set(self._sql_table_names)))

    def read_sql_data(self, table_name):
        try:
            return pd.read_sql(table_name, con=self._context.db_con)
        except Exception as e:
            raise Exception(f"table name does not exist in SQL : {table_name}", "")
        
    def alter_table(self,table_name, column_name, column_type):
        self._context.db_con.execute(f"ALTER TABLE {table_name} ADD COLUMN 
                                     {column_name} {column_type}")
        
    def get_table_rows_count(self, table_name):
        return self._context.db_con.execute(f"SELECT COUNT(*) FROM {table_name}")
    
    def get_table_cols_count(self, table_name):
        return self._context.db_con.execute(f"SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = {table_name}")
    
    @timing
    def write_sql_data(self, dataframe, table_name):
        if table_name in self.db_tables:
            col_count = self.get_table_cols_count(table_name)
            row_count = self.get_table_rows_count(table_name)
            if col_count > dataframe.shape[1] :
                self._log.info(f"{table_name} - WILL BE DELETED TO ADD {col_count - dataframe.shape[1]} new columns")
                self._context.db_con.execute(f"DROP TABLE {table_name}")
                dataframe.to_sql(table_name, con=self._context.db_con, chunksize = 50000, index=False)
            elif row_count > dataframe.shape[0] :
                self._log.info(f"INSERT {row_count - dataframe.shape[0]} NEW OBSERVATIONS TO {table_name}")
        else:
            self._log.info(f"WRITTING INTO SQL : {table_name} ......")
            dataframe.to_sql(table_name, con=self._context.db_con, if_exists="append", chunksize = 50000, index=False)
        self._log.info(f"WRITTEN INTO SQL : {table_name}")