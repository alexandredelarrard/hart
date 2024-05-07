import re
import numpy as np
import logging 

from src.context import Context
from nltk.tokenize import word_tokenize
from src.utils.utils_dataframe import remove_punctuation

from src.datacrawl.transformers.TextCleaner import TextCleaner
from omegaconf import DictConfig


def check_numbers(numbers, x):
    clean_numbers=[]
    for number in numbers:
        if len(number) >= 3:
            clean_numbers.append(number)
        else:
            if len(re.findall("\\b\\d+\s?century", x.strip()) + 
                   re.findall("c.\s?\\d+", x.strip()) + 
                   re.findall("s.\s?\\d+", x) + 
                   re.findall("\\d+\s?jh", x) + 
                   re.findall("\\b\\d+\s?siecle", x) + 
                   re.findall("sec.\s?\\b\\d+", x.strip()) + 
                   re.findall("\\b\\d+\s?sec", x.strip()) + 
                   re.findall("\\b\\d+\s?secolo", x)) != 0:
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

    for ith in ["th ", "st ", "rd ", "nd ", "eme ", "e ", "er ", "nd "]:
        for th in re.findall(f"(\\d+\s?){ith}", x):
            x = x.replace(f"{th}{ith}", str((int(th) -1)*100 + 50) + " ")

    return x

def handle_years_pair(numbers):
    if numbers == ["19", "20"]:
        return ["1850"]
    elif numbers == ["20", "21"]:
        return ["1950"]
    elif numbers == ["18", "19"]:
        return ["1750"]
    elif numbers == ["17", "18"]:
        return ["1650"]
    elif numbers == ["16", "17"]:
        return ["1550"]
    elif numbers == ["15", "16"]:
        return ["1450"]
    else:
        return numbers
    
def handle_short_century(x):
    if x == "19":
        return "1850"
    elif x == "20":
        return "1950"
    elif x == "18":
        return "1750"
    elif x == "17":
        return "1650"
    else:
        return x 
    
class GPTCleaner(TextCleaner):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)

        self.period_mapping = self._config.evaluator.cleaning_mapping.period_mapping
       
    def map_value_to_key(self, x, mapping_dict):
        tok_x = word_tokenize(remove_punctuation(str(x)))
        for key, values in mapping_dict.items():
            for sub_value in values:
                if str(sub_value) in tok_x:
                    return key.strip()
        return np.nan
        
    def handle_cm(self, x):

        x = " " + x.replace("-", " ") + " "
        x = x.replace(",", ".")

        # handle inches 
        x = x.replace(" 3/4 ", ".75 ")
        x = x.replace(" 1/2 ", ".5 ")
        x = x.replace(" 1/4 ", ".25 ")
        x = x.replace(" 1/8 ", ".125 ")
        x = x.replace(" 7/8 ", ".875 ")
        x = x.replace(" 5/8 ", ".625 ")
        x = x.replace(" 3/8 ", ".375 ")

        x = x.replace(" 3/4in", ".75 in")
        x = x.replace(" 1/2in", ".5 in")
        x = x.replace(" 1/4in", ".25 in")
        x = x.replace(" 1/8in", ".125 in")
        x = x.replace(" 7/8in", ".875 in")
        x = x.replace(" 5/8in", ".625 in")
        x = x.replace(" 3/8in", ".375 in")

        # TODO: handle picture frames with x 

        dimensions = {}
        for dim in ["cm", "mm", "in", ""]:
            extract =  re.findall(f"(\\d+.?\\d+\s?){dim}", x)
            if len(extract) == 1:
                if dim != "":
                    if dim == "in":
                        dimensions[dim] = extract[0].strip() + "*2.54"
                    elif dim == "mm":
                        dimensions[dim] = extract[0].strip() + "*0.1"
                    else:
                        dimensions[dim] = extract[0].strip()
                else:
                    dimensions["no_dim"] = extract[0].strip()

        try:
            answer = np.mean([eval(a) for a in dimensions.values()])
        except Exception:
            answer = np.nan
            # logging.error(x)
        return answer
        
    def replace_periodes(self, x):
        for k, v in self.period_mapping.items():
            if k in x:
                x = v
        return x
    
    def eval_number(self, x):
        try: 
            return eval(x)
        except Exception:
            return np.nan
        
    def clean_periode(self, x):

        infos = {}
        x = " " + str(x) + " "
        x = x.replace("era", "")
        x = x.replace("period", "")
        x = x.replace("thirty", "30")
        x = re.sub(" +", " ", x)
        x = x.replace(",", " ").replace("/", " ").replace("-", " ")
        x = x.replace("oo", "00")
        x = x.replace("??", "00")
        x = x.replace("**", "00")

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
        x = handle_short_century(x.strip())

        if " 1st " in x or " 1er " in x:
            return eval(infos["sign"])*(eval(infos["distance_century"]))
        else:
            numbers = re.findall("\\d+", x)
            numbers = handle_years_pair(numbers)
            numbers = check_numbers(numbers, x)

            if len(numbers) !=0:
                dates = np.mean([int(a) for a in numbers if a.isdigit()])
                return eval(infos["sign"])*(dates + eval(infos["distance_century"]))
            else:
                # if x!= "nan":
                #     logging.error(x)
                return np.nan