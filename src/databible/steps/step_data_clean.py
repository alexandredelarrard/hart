import numpy as np
import pandas as pd 
from typing import List
from omegaconf import DictConfig
import pandas as pd

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

pd.options.mode.copy_on_write = True

class StepDataClean(Step):
    
    def __init__(self,
                 config : DictConfig, 
                 context : Context):

        super().__init__(context=context, config=config)

    @timing
    def run(self):

        # communes zone emploi
        df_zone_emploi = self.reconstruct_zone_emploi()
        self.write_sql_data(df_zone_emploi, "CLEAN_ZONE_EMPLOI")

        # communes cleaning and consolidation
        df_communes = self.reconstruct_communes()
        self.write_sql_data(df_communes, "CLEAN_COMMUNES")
    
    @timing
    def reconstruct_zone_emploi(self):
        df = self.read_sql_data("CONSOLIDATE_ZONE_EMPLOI")
        return df

    @timing
    def reconstruct_communes(self):
        df = self.read_sql_data("CONSOLIDATE_COMMUNE")
        df["ID_ZONE_EMPLOI"] = df["ZONE_EMPLOI_2020"].apply(lambda x : str(x)[:4])
        
        # population 
        population = df[["ID_COMMUNE", "POP_2020", "TAUX_POP_MOINS_15_2020", "TAUX_POP_PLUS_65_2020",
                        "TAUX_POP_PLUS_80_2020", "TAUX_POP_25_64_2020", "NBR_FEMME_55_64_2020",
                        "NBR_HOMME_55_64_2020"]].copy()
        population["TAUX_POP_15_24"] = np.where(df["TAUX_POP_MOINS_15_2020"].notnull(), (100 - df[["TAUX_POP_MOINS_15_2020", 
                                                  "TAUX_POP_25_64_2020", 
                                                  "TAUX_POP_PLUS_65_2020"]].sum(axis=1)), np.nan)
        population["TAUX_POP_65_74"] = (df["TAUX_POP_PLUS_65_2020"] - df["TAUX_POP_PLUS_75_2020"])
        population["TAUX_POP_75_79"] = (df["TAUX_POP_PLUS_75_2020"] - df["TAUX_POP_PLUS_80_2020"])
        population["TAUX_POP_55_64"] = df[["NBR_FEMME_55_64_2020", "NBR_HOMME_55_64_2020"]].sum(axis=1) / df["POP_2020"]
        population["TAUX_POP_25_54"] = population["TAUX_POP_25_64_2020"] - population["TAUX_POP_55_64"]
        
        population["AGE_MOYEN"] = (population["TAUX_POP_MOINS_15_2020"]*7.5 + 
                                   population["TAUX_POP_15_24"]*20 + 
                                   population["TAUX_POP_25_54"]*40 + 
                                   population["TAUX_POP_55_64"]*60 +
                                   population["TAUX_POP_65_74"]*70 +
                                   population["TAUX_POP_75_79"]*77.5 +
                                   population["TAUX_POP_PLUS_80_2020"]*92)/100
        
        population = population[["ID_COMMUNE", "TAUX_POP_15_24", "TAUX_POP_25_54",
                                 "TAUX_POP_55_64", "TAUX_POP_65_74", "TAUX_POP_75_79"]]
        df = df.merge(population, on="ID_COMMUNE", how="left", validate="1:1")

        # statut familial
        gender_age = df[["ID_COMMUNE", "POP_2020", "NBR_FEMME_15_24_2020", "NBR_FEMME_25_54_2020", "NBR_FEMME_55_64_2020",
                       "NBR_HOMME_15_24_2020", "NBR_HOMME_25_54_2020", "NBR_HOMME_55_64_2020",
                       "TAUX_POP_65_74", "TAUX_POP_75_79", "TAUX_POP_PLUS_80_2020", "TAUX_POP_MOINS_15_2020"]]
        gender_age["TAUX_HOMME_POP_15_24"] = gender_age["NBR_HOMME_15_24_2020"] / gender_age[["NBR_HOMME_15_24_2020", "NBR_FEMME_15_24_2020"]].sum(axis=1)
        gender_age["TAUX_HOMME_POP_25_54"] = gender_age["NBR_HOMME_25_54_2020"] / gender_age[["NBR_HOMME_55_64_2020", "NBR_FEMME_25_54_2020"]].sum(axis=1)
        gender_age["TAUX_HOMME_POP_55_64"] = gender_age["NBR_HOMME_55_64_2020"] / gender_age[["NBR_HOMME_55_64_2020", "NBR_FEMME_55_64_2020"]].sum(axis=1)
        gender_age["TAUX_HOMME_POP_MOINS_15"] = gender_age["TAUX_HOMME_POP_15_24"]

        # TODO: approximate + 65 
        gender_age = gender_age[["ID_COMMUNE", "TAUX_HOMME_POP_MOINS_15", "TAUX_HOMME_POP_15_24", "TAUX_HOMME_POP_25_54", 
                                 "TAUX_HOMME_POP_55_64"]]
        df = df.merge(gender_age, on="ID_COMMUNE", how="left", validate="1:1")

        # 
    

        return df
    
    
    @timing
    def reconstruct_carreaux_200m(self):
        df_car = self.read_sql_data("CONSOLIDATE_CARREAUX_200M")
        return df

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
    
    

