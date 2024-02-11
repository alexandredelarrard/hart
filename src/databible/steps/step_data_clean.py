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

                self.write_sql_data(df, table_name="CLEAN_" + data_name)
    
    # dict_keys(['communes_encodage_2020', 'communes_encodage_2023', 'deces', 'elections', 'emploi', 'entreprise_creation', 'entreprise_caracteristiques', 'logements', 'menages', 'naissance', 'populations_csp', 'scolarisation', 'securite', 'tourisme'])

    @timing
    def commune_emplois_cleaning(self, df):

        # split dataframe
        df_zipcode_activity  = df[['CODE', 'LIBELLE',
                                   "NBR_EMPLOIS_2020",
                                   "TAUX_SALARIES_DS_EMPLOI_2020",
                                   "TAUX_OURVIERS_DS_EMPLOI_2020",
                                   "TAUX_EMPOYES_DS_EMPLOI_2020",
                                   "TAUX_AGRICULTEURS_DS_EMPLOI_2020",
                                   "TAUX_ARTISANS_COMMERCANTS_DS_EMPLOI_2020",
                                   "TAUX_PROF_INTERMEDIAIRE_DS_EMPLOI_2020",
                                   "TAUX_CADRES_INTEL_SUP_DS_EMPLOI_2020"]]
        
        df_zipcode_activity["CSP"] = df_zipcode_activity[["TAUX_OURVIERS_DS_EMPLOI_2020",
                                                        "TAUX_EMPOYES_DS_EMPLOI_2020",
                                                        "TAUX_AGRICULTEURS_DS_EMPLOI_2020",
                                                        "TAUX_ARTISANS_COMMERCANTS_DS_EMPLOI_2020",
                                                        "TAUX_PROF_INTERMEDIAIRE_DS_EMPLOI_2020",
                                                        "TAUX_CADRES_INTEL_SUP_DS_EMPLOI_2020"]].idxmax(axis=1)
        df_zipcode_activity["CSP"] =  df_zipcode_activity["CSP"].map({"TAUX_OURVIERS_DS_EMPLOI_2020" : "ouvrier",
                                                                      "TAUX_EMPOYES_DS_EMPLOI_2020" : "employe",
                                                                    "TAUX_AGRICULTEURS_DS_EMPLOI_2020": "agriculteur",
                                                                    "TAUX_ARTISANS_COMMERCANTS_DS_EMPLOI_2020":"artisan_commercant",
                                                                    "TAUX_PROF_INTERMEDIAIRE_DS_EMPLOI_2020":"prof_intermediaire",
                                                                    "TAUX_CADRES_INTEL_SUP_DS_EMPLOI_2020":"cadre"})

        # activity per age, zipcode gender
        df_activity = df[['CODE', 'LIBELLE',
                        'NBR_EMPLOIS_2020',
                        'NBR_FEMMES_15_24_2020',
                        'NBR_FEMMES_25_54_2020',
                        'NBR_FEMMES_55_64_2020',
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
    

