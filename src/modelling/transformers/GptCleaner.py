import re
import numpy as np
from src.context import Context
from src.utils.timing import timing

from src.datacrawl.transformers.TextCleaner import TextCleaner
from omegaconf import DictConfig


class GPTCleaner(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)

        self.period_mapping = self._config.evaluator.cleaning_mapping.period
        self.country_mapping = self._config.evaluator.cleaning_mapping.country
        self.material_mapping = self._config.evaluator.cleaning_mapping.material
        self.color_mapping = self._config.evaluator.cleaning_mapping.color
        self.shape_mapping = self._config.evaluator.cleaning_mapping.shape
        self.style_mapping = self._config.evaluator.cleaning_mapping.style
        self.manufacturer_mapping = self._config.evaluator.cleaning_mapping.manufacturer
        self.condition_mapping = self._config.evaluator.cleaning_mapping.condition
        self.decorations_mapping = self._config.evaluator.cleaning_mapping.decorations

    def map_value_to_key(self, x, mapping_dict):

        ordered_mapping_dict = {}
        for k in sorted(mapping_dict, key=len, reverse=True):
            ordered_mapping_dict[k] = mapping_dict[k]

        for key, values in ordered_mapping_dict.items():
            for sub_value in values:
                if " " + str(sub_value) + " " in " " + str(x) + " ":
                    return key
                
        return np.nan
        

    def handle_cm(self, x):
        for dim in ["", "cm", " cm"]:
            test = re.findall(f"(\\d+.?\\d+){dim}", x)
            if len(test) != 0:
                return test[0]
        return np.nan
    
        
    def replace_periodes(self, x):
        for k, v in self.period_mapping.items():
            if k in x:
                x = v
        return x

    def clean_periode(self, x):

        origin = str(x)
        infos = {}
        x = " " + str(x) + " "

        infos["sign"] = "1"
        if " bc " in x or " b c " in x:
            infos["sign"] = "-1"

        infos["distance_century"] = "0"
        if " early " in x or ' debut ' in x or 'before' in x or "premiere moitie" in x:
            infos["distance_century"] = "-30"
        
        if " late " in x or ' fin ' in x:
            infos["distance_century"] = "30"

        x = self.replace_periodes(x)
        x = handle_romain(x)
        x = handle_th(x)

        if " 1st " in x or " 1er " in x:
            return eval(infos["sign"])*(eval(infos["distance_century"]))
        else:
            numbers = re.findall("\\d+", x)
            numbers = check_numbers(numbers, x)

            if len(numbers) !=0:
                dates = np.mean([eval(a) for a in numbers])
                return eval(infos["sign"])*(dates + eval(infos["distance_century"]))
            else:
                if origin not in ["None", "nan", np.nan]:
                    self._log.error(origin)
                return np.nan


def check_numbers(numbers, x):
    clean_numbers=[]
    for number in numbers:
        if len(number) >= 3:
            clean_numbers.append(number)
        else:
            if len(re.findall("\\b\\d+ century", x.strip()) + re.findall("\\b\\d+ siecle", x) + re.findall("\\b\\d secolo", x))==1:
                clean_numbers.append(number + str('00'))
    return clean_numbers


def handle_romain(x):
    x = x.replace(" veme ", " 5th ")
    x = x.replace("xxv", "25")
    x = x.replace("xxvi", "26")
    x = x.replace("xxii", "22")
    x = x.replace("xxiii", "23")
    x = x.replace("xxiv", "24")
    x = x.replace("xxvii", "27")
    x = x.replace("xxviii", "28")
    x = x.replace("xxi", "21")
    x = x.replace("xx", "20")
    x = x.replace("xix", "19")
    x = x.replace("xviii", "18")
    x = x.replace("xvii", "17")
    x = x.replace("xvi", "16")
    x = x.replace("xv", "15")
    x = x.replace("xiv", "14")
    x = x.replace("xiii", "13")
    x = x.replace("xii", "12")
    x = x.replace("xi", "11")
    x = x.replace("ix", "9")
    x = x.replace("viii", "8")
    x = x.replace("vii", "7")
    x = x.replace("vi", "6")
    x = x.replace("iv", "4")
    x = x.replace("iii", "3")
    return x


def handle_th(x):

    for ith in ["th ", "st ", "rd ", "nd ", "eme ", "e ", " e ", "er ", "nd "]:
        for th in re.findall(f"(\\d+){ith}", x):
            x = x.replace(f"{th}{ith}", str((eval(th) -1)*100 + 50) + " ")

    return x