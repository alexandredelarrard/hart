import logging 
import os 
from io import StringIO
import sys 
from logging.config import dictConfig 
from pathlib import Path 

from dotenv import load_dotenv, find_dotenv
from omegaconf import DictConfig, OmegaConf

from src.utils.config import read_config
from src.utils.seed import set_seed

class Context(Object):

    def __init__(self, config : DictConfig, use_cache : bool, save : bool):

        self._config = config

        # creqte logging buffer 
        buffer =StringIO()
        handler = logging.StreamHandler(buffer)
        formatter = logging.Formatter(self._config.logging.formatters.file.format)
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)
        self.log_buffer = buffer 

        # logging 
        self.log = logging.getLogger(__name__)

        # env variables 
        dot_env_file = find_dotenv(usecwd=True)
        load_dotenv(dot_env_file)
        self.log.info(f"Dot env file has been loaded {dot_env_file}")

        self._use_cache = use_cache
        self._save = save

    @property
    def config(self) -> DictConfig:
        return self._config
    
    @property
    def use_cache(self) -> bool: 
        return self._use_cache
    
    @property
    def save(self) -> bool: 
        return self._save
    
    @property
    def random_state(self) -> int:
        return self._config.seed
    

def get_config_context(config_path : str, use_cache : bool, save : bool):

    try:
        config = read_config(path=config_path)
        dictConfig(OmegaConf.to_container(config.logging))
        set_seed(config)
    except FileNotFoundError:
        print(f"configuration file {config_path} not found ", file=sys.stderr)
        sys.exit(1)

    context = Context(config=config, use_cache=use_cache, save=save)

    return config, context 