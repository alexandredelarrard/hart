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
    def commune_elections_cleaning(self, df):
        df = self.replace_nans(df, ["TAUX_DE_PROCURATIONS_EN_2022", 
                                    "NOMBRE_DE_MANDANTS_EN_2022", 
                                    "ELECTEURS_INSCRITS_SUR_LISTE_PRINCIPALE_2022"])
        return df
    

    @timing
    def commune_emploi_cleaning(self, df):

        # to float
        df = self.replace_nans(df, ["PART_DES_EMPLOYES_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                    "PART_DES_OUVRIERS_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                    "PART_DES_EMPLOIS_SAL_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                    "PART_DES_EMPLOIS_NON_SAL_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                    'NB_DE_FEMMES_DE_15_A_64_ANS_PAR_TRANCHE_D_AGE_2020',
                                    'NB_DE_FEMMES_DE_15_A_64_ANS_PAR_TRANCHE_D_AGE_20201',
                                    'NB_DE_FEMMES_DE_15_A_64_ANS_PAR_TRANCHE_D_AGE_20202',
                                    'NB_DE_FEMMES_DE_15_A_64_ANS_PAR_TRANCHE_D_AGE_20203',
                                    'NB_D_EMPLOIS_AU_LIEU_DE_TRAVAIL_LT_2020',
                                    "PART_DES_AGRICULTEURS_EXPL_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                    "PART_DES_ARTISANS_COMMERCANTS_CHEFS_D'ENT_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                    "PART_DES_CADRES_ET_PROF_INTELLECTUELLES_SUP_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                    "PART_DES_PROF_INTERMEDIAIRES_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                    'TAUX_D_ACTIVITE_PAR_TRANCHE_D_AGE_2020',
                                    'TAUX_D_ACTIVITE_PAR_TRANCHE_D_AGE_20201',
                                    'TAUX_D_ACTIVITE_PAR_TRANCHE_D_AGE_20202',
                                    'TAUX_D_ACTIVITE_DES_FEMMES_PAR_TRANCHE_D_AGE_2020',
                                    'TAUX_D_ACTIVITE_DES_FEMMES_PAR_TRANCHE_D_AGE_20201',
                                    'TAUX_D_ACTIVITE_DES_FEMMES_PAR_TRANCHE_D_AGE_20202',
                                    'TAUX_ACTIVITE_DES_HOMMES_PAR_TRANCHE_D_AGE_2020',
                                    'TAUX_ACTIVITE_DES_HOMMES_PAR_TRANCHE_D_AGE_20201',
                                    'TAUX_ACTIVITE_DES_HOMMES_PAR_TRANCHE_D_AGE_20202'])
        
        df.rename(columns= {}, inplace=True)
        
        # split dataframe
        df_zipcode_activity  = df[['CODE', 'LIBELLE',
                                   "NB_D_EMPLOIS_AU_LIEU_DE_TRAVAIL_LT_2020",
                                   "PART_DES_EMPLOIS_SAL_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                   "PART_DES_OUVRIERS_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                   "PART_DES_AGRICULTEURS_EXPL_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                   "PART_DES_ARTISANS_COMMERCANTS_CHEFS_D'ENT_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                   "PART_DES_EMPLOYES_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                   "PART_DES_PROF_INTERMEDIAIRES_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                   "PART_DES_CADRES_ET_PROF_INTELLECTUELLES_SUP_DANS_LE_NB_D'EMPLOIS_AU_LT_2020"]]
        
        df_zipcode_activity["CSP"] = df_zipcode_activity[["PART_DES_OUVRIERS_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                                        "PART_DES_AGRICULTEURS_EXPL_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                                        "PART_DES_ARTISANS_COMMERCANTS_CHEFS_D'ENT_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                                        "PART_DES_EMPLOYES_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                                        "PART_DES_PROF_INTERMEDIAIRES_DANS_LE_NB_D'EMPLOIS_AU_LT_2020",
                                                        "PART_DES_CADRES_ET_PROF_INTELLECTUELLES_SUP_DANS_LE_NB_D'EMPLOIS_AU_LT_2020"]].idxmax(axis=1)

        # activity per age, zipcode gender
        df_activity = df[['CODE', 'LIBELLE',
                        'NB_D_EMPLOIS_AU_LIEU_DE_TRAVAIL_LT_2020',
                        'NB_DE_FEMMES_DE_15_A_64_ANS_PAR_TRANCHE_D_AGE_20201',
                        'NB_DE_FEMMES_DE_15_A_64_ANS_PAR_TRANCHE_D_AGE_20202',
                        'NB_DE_FEMMES_DE_15_A_64_ANS_PAR_TRANCHE_D_AGE_20203',
                        'TAUX_D_ACTIVITE_PAR_TRANCHE_D_AGE_2020',
                        'TAUX_D_ACTIVITE_PAR_TRANCHE_D_AGE_20201',
                        'TAUX_D_ACTIVITE_PAR_TRANCHE_D_AGE_20202',
                        'TAUX_D_ACTIVITE_DES_FEMMES_PAR_TRANCHE_D_AGE_2020',
                        'TAUX_D_ACTIVITE_DES_FEMMES_PAR_TRANCHE_D_AGE_20201',
                        'TAUX_D_ACTIVITE_DES_FEMMES_PAR_TRANCHE_D_AGE_20202',
                        'TAUX_ACTIVITE_DES_HOMMES_PAR_TRANCHE_D_AGE_2020',
                        'TAUX_ACTIVITE_DES_HOMMES_PAR_TRANCHE_D_AGE_20201',
                        'TAUX_ACTIVITE_DES_HOMMES_PAR_TRANCHE_D_AGE_20202']]
            
        return df
    

    def replace_nans(self, df, liste_cols):
        for col in liste_cols:
            df[col] = df[col].replace('N/A - résultat non disponible', np.nan)
            df[col] = df[col].replace('N/A - division par 0', np.nan)
            df[col] = df[col].astype(float)
        return df


