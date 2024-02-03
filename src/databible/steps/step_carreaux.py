import os
import time
import random
from typing import List
from omegaconf import DictConfig
import pandas as pd

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

class StepConsolidateInsee(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 granularite : str):

        super().__init__(context=context, config=config)
        self.granularite = self.check_granularite(granularite)

    @timing
    def run(self):

        # initialize the drivers 
        df = self.load_data()

    @timing
    def load_data(self):

        data_dict= {}
        data_dict["carreau"] = pd.read_csv(self._config.flat_file.insee[f"carreaux_{granularite}"]["met"])
        data_dict["code_geo"] = pd.read_csv(self._config.flat_file.insee.communes_encodage)

        return data_dict


    def check_granularite(self, granularite):
        granularite = granularite.lower().strip().replace(" ", "_")
        if granularite not in ["200m", "1km"]:
            raise Exception("Granularite should be either '200m' or '1km'")
        return granularite

        



       