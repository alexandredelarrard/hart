import logging 
import pandas as pd
from abc import abstractmethod
from omegaconf import DictConfig

from src.context import Context 
from src.utils.string import camel_to_snake
from src.utils.sql_helper import SqlHelper


class Step(SqlHelper):

    def __init__(
            self,
            config : DictConfig,
            context : Context, 
    ):
        super().__init__(context=context)

        self._log : logging.Logger = logging.getLogger(__name__)
        self._config = config 
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
        return list(set(self.db_tables).intersection(set(self._sql_table_names)))
    
    
