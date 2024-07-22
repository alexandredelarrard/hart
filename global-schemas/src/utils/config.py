from omegaconf import DictConfig, OmegaConf
import glob
from pathlib import Path


def read_config(path: str) -> DictConfig:

    if not Path(path):
        raise Exception(f"{path} does not exist")

    config_paths = sorted(glob.glob(path + "/**/*.yml", recursive=True))

    # get all configs
    config_base = [OmegaConf.load(config) for config in config_paths]

    config = OmegaConf.merge(*config_base)

    return config
