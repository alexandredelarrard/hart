import pandas as pd 
import os 
import yaml
import logging
from datetime import timedelta
from pathlib import Path as pl
from flask_pymongo import PyMongo
from dotenv import load_dotenv

class Config(object):

    def __init__(self, config_path):

        load_dotenv(pl(config_path) / pl(".env"))
        config_yaml = open(pl(config_path) / pl("configs.yml"))
        self.configs = yaml.load(config_yaml, Loader=yaml.FullLoader)

        self.email_config = self.configs["email"]
        
        self.server = self.configs["server"]
        self.user = os.environ["SERVER_USERNAME"]
        self.pwd = os.environ["SERVER_PWD"]
        self.port = self.server["port"]
        self.host = self.server["host"]
        self.database = self.server["database"]
        self.connexion_string = f"mongodb+srv://{self.user}:{self.pwd}@{self.host}/{self.database}?retryWrites=true&w=majority"

        self.set_loggins()

    def set_loggins(self):

        # loggings 
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

        file_handler = logging.FileHandler('./gunicorn_logs/logs_api.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def init_db(self):
        mongo = PyMongo()
        return mongo, mail

    def set_config_app(self, app, debug=True):
            
        app.secret_key = self.pwd
        os.environ["SECRET_KEY"] = self.pwd
        
        app.config['MONGO_URI'] = self.connexion_string
        self.logger.info(self.connexion_string)
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)
        app.config["JWT_ACCESS_LIFESPAN"] = {'hours': 24}
        app.config["JWT_REFRESH_LIFESPAN"] = {'days': 1}
        app.config["PRAETORIAN_ROLES_DISABLED"] = True
        app.config.update(self.email_config)
    
        if debug:
            app.config["DEBUG"] = True
            app.config["TESTING"] = True
        else:
            app.config["DEBUG"] = False
            app.config["TESTING"] = False

        return app