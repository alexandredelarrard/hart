import numpy as np
from typing import List
from omegaconf import DictConfig
import pandas as pd

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

class StepDataClean(Step):
    
    def __init__(self,
                 config : DictConfig, 
                 context : Context):

        super().__init__(context=context, config=config)

    @timing
    def run(self):

        # clean data 
        self.clean_datasets()

    
    @timing
    def clean_datasets(self):

        cleaning_methods = [method for method in dir(StepDataClean) if "_cleaning"  in method]

        for data_name in self._sql_table_names:
            methode = data_name.lower() + "_cleaning"

            if methode in cleaning_methods:
                df = self.read_sql_data(data_name)
                df = eval(f"self.{methode}")(df)
                self.write_sql_data(df, table_name=data_name)
    
    @timing
    def commune_emplois_cleaning(self, df):

        # split dataframe
        df["CSP"] = df[["TAUX_OUVRIERS_2020",
                        "TAUX_EMPLOYES_2020",
                        "TAUX_AGRICULTEURS_2020",
                        "TAUX_ARTISAN_COMMERCE_2020",
                        "TAUX_PROF_INTER_2020",
                        "TAUX_CADRE_INTELLECT_2020"]].idxmax(axis=1).map({
                            "TAUX_OUVRIERS_2020" : "ouvrier",
                            "TAUX_EMPLOYES_2020" : "employe",
                            "TAUX_AGRICULTEURS_2020": "agriculteur",
                            "TAUX_ARTISAN_COMMERCE_2020":"artisan_commercant",
                            "TAUX_PROF_INTER_2020":"prof_intermediaire",
                            "TAUX_CADRE_INTELLECT_2020":"cadre"})

        # activity per age, zipcode gender
        df_activity = df[['ID_COMMUNE', 
                        'NOM_COMMUNE_ORIGINE',
                        'NBR_EMPLOI',
                        'NBR_FEMME_15_24_2020',
                        'NBR_FEMME_25_54_2020',
                        'NBR_FEMME_55_64_2020',
                        'TAUX_ACTIVITE_15_24',
                        'TAUX_ACTIVITE_25_54',
                        'TAUX_ACTIVITE_55_64',
                        'TAUX_ACTIVITE_FEMME_15_24',
                        'TAUX_ACTIVITE_FEMME_25_54',
                        'TAUX_ACTIVITE_FEMME_55_64',
                        'TAUX_ACTIVITE_HOMME_15_24',
                        'TAUX_ACTIVITE_HOMME_25_54',
                        'TAUX_ACTIVITE_HOMME_55_64']]
            
        return df
    
    

