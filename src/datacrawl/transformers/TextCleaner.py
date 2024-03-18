from typing import List
import pandas as pd 

import re
from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from src.constants.variables import currencies
from omegaconf import DictConfig


class TextCleaner(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)

    def get_currency_from_text(self, variable):
        return variable.apply(lambda x : re.findall(currencies, str(x))[0] if 
                                             len(re.findall(currencies, str(x))) > 0 else x)

    def get_estimate(self, variable, min_max : str = "min"):
        if min_max.lower() == "min":
            return variable.apply(lambda x : re.findall(r"\d+", str(x).replace(" ","").replace(",",""))[0] 
                                           if len(re.findall(r"\d+", str(x))) > 0 else x)
        elif min_max.lower() == "max":
            return variable.apply(lambda x : re.findall(r"\d+", str(x).replace(" ","").replace(",",""))[1] 
                                           if len(re.findall(r"\d+", str(x))) > 0 else x)
        else: 
            raise Exception("EITHER MIN OR MAX value for min_max")

    def get_splitted_infos(self, variable, index, sep='\n'):
        return  pd.DataFrame(variable.str.split(sep).tolist(), index=index)