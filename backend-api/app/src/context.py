import logging 
import os 
from chromadb import Settings, HttpClient
from io import StringIO
import sys 
from logging.config import dictConfig 
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from dotenv import load_dotenv, find_dotenv
from omegaconf import DictConfig, OmegaConf

from src.utils.config import read_config

class DBeaver: 

    def __init__(self, config):

        self.config=config

        self.server = self.config["server"]
        self.user = os.environ["DATABASE_USERNAME"]
        self.pwd = os.environ["DATABASE_PWD"]
        self.port = self.server["port"]
        self.host = self.server["host"]
        self.database = self.server["database"]
        self.connexion_string = f"postgresql+psycopg2://{self.user}:{self.pwd}@{self.host}:{self.port}/{self.database}"

    def init_db(self):
        connection = create_engine(self.connexion_string)
        return connection
    
    def flask_connect(self, connection):
        db = SQLAlchemy()
        db.Model.metadata.reflect(connection.engine)
        return db
    
class Context:

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

        # connection 
        db = DBeaver(config)
        self.connexion_string = db.connexion_string
        self.db_con = db.init_db()
        self.flask_db = db.flask_connect(self.db_con)

        # Cors policy
        self.cors = CORS(resources={r"/*": {"origins": self._config.front_end.server}})

        # chromadb 
        self.chroma_client = HttpClient(
                host=self._config.chroma_db.host,
                port=self._config.chroma_db.port,
                settings=Settings(
                    allow_reset=True,
                    anonymized_telemetry=False
                )
            )

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
        config = read_config(path="./configs")
        dictConfig(OmegaConf.to_container(config.logging))
    except FileNotFoundError:
        print(f"configuration file {config_path} not found ", file=sys.stderr)
        sys.exit(1)

    context = Context(config=config, use_cache=use_cache, save=save)

    return config, context 