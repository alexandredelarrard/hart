import logging 
import pandas as pd
from abc import abstractmethod
from src.utils.timing import timing
from omegaconf import DictConfig

from src.context import Context 
from src.utils.string import camel_to_snake


class Step:

    def __init__(
            self,
            config : DictConfig,
            context : Context, 
    ):
        
        self._log : logging.Logger = logging.getLogger(__name__)
        self._config = config 
        self._context = context
        self._name = self.get_name() 
        self._sql_table_names = self.get_table_names()
        self._tables_in_sql = self.get_sql_loaded_tables()

        self._log.info(f"starting step {self}")

    @property
    def name(self):
        return self._name

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def get_name(cls):
        return camel_to_snake(cls.__name__)
    
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

        tables = pd.read_sql("SELECT table_name FROM information_schema.tables", con=self._context.db_con)
        tables = tables["table_name"].tolist()
        tables = list(set(tables).intersection(set(self._sql_table_names)))
        return tables

    def read_sql_data(self, table_name):
        return pd.read_sql(table_name, con=self._context.db_con)
    
    @timing
    def write_sql_data(self, dataframe, table_name):
        self._log.info(f"WRITTING INTO SQL : {table_name} ......")
        dataframe.to_sql(table_name, con=self._context.db_con, chunksize = 50000)
        self._log.info(f"WRITTEN INTO SQL : {table_name}")
        