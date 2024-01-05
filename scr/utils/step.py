import logging 
from abc import abstractmethod
from omegaconf import DictConfig

from src.context import Context 
from src.utils.string import camel_to_snake


class Step:

    def __init__(
            self,
            context : Context, 
            config : DictConfig, 
    ):
        
        self._log : logging.Logger = logging.getLogger(__name__)
        self._config = config 
        self._context = context
        self.name = self.get_name() 

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