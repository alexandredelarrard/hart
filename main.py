import pandas as pd 
import yaml
from pathlib import Path as pl

def load_configs(config_path):
    config_yaml = open(pl(config_path) / pl("configs.yml"))
    configs = yaml.load(config_yaml, Loader=yaml.FullLoader)
    return configs

if __name__ == "__main__" : 
    configs = load_configs('configs')
    datas = {}
    