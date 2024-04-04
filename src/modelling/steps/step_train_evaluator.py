import glob
import time
import pandas as pd 

from tqdm import tqdm 
from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from omegaconf import DictConfig
from src.utils.utils_crawler import (encode_file_name,
                                     read_crawled_pickles,
                                     save_queue_to_file)


class StepTrainEvaluator(Step):

    def __init__(self, 
                context : Context,
                config : DictConfig):

        super().__init__(context=context, config=config)

        self.save_queue_path= self._config.gpt.save_path

    @timing
    def run(self):

        df_done = read_crawled_pickles(path=self.save_queue_path)
