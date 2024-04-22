import os
import time
import random
from typing import List
from omegaconf import DictConfig
import pandas as pd

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

class StepDataConsolidate(Step):
    
    def __init__(self,
                 config : DictConfig, 
                 context : Context):

        super().__init__(context=context, config=config)

    @timing
    def run(self):

        # consolidate granularities 
        df_communes = self.consolidate_communes()
        self.write_sql_data(df_communes, table_name="CONSOLIDATE_COMMUNE")

        df_departements = self.consolidate_departements()
        self.write_sql_data(df_departements, table_name="CONSOLIDATE_DEPARTEMENTS")

        df_zone_emploi = self.consolidate_zone_emploi()
        self.write_sql_data(df_zone_emploi, table_name="CONSOLIDATE_ZONE_EMPLOI")

        df_carreaux_200m = self.consolidate_carreaux_200m()
        self.write_sql_data(df_carreaux_200m, table_name="CONSOLIDATE_CARREAUX_200M")

        df_carreaux_1km = self.consolidate_carreaux_1km()
        self.write_sql_data(df_carreaux_1km, table_name="CONSOLIDATE_CARREAUX_1KM")

    @timing
    def consolidate_communes(self):
        # TODO: check les communes entre 2020 et 2023 qui changent. 
        # Gérer les MVs de région & co

        df_root = self.read_sql_data("COMMUNE_ENCODAGE_2020")
        df_root = df_root[["ID_COMMUNE", "ID_REGION", "ID_DEPARTEMENT", "ID_ARRONDISSEMENT",
                           "ID_CANTON", "ID_COMMUNE_PARENTE", "NOM_COMMUNE"]].drop_duplicates("ID_COMMUNE")
        
        commune_tables = [x for x in self._tables_in_sql if "CLEAN" not in x \
                          and "CONSOLIDATE" not in x and "COMMUNE" in x and \
                          "ENCODAGE" not in x]

        assert(len(commune_tables) == 14)

        for table_name in commune_tables:
            df_table = self.read_sql_data(table_name)
            df_root = df_root.merge(df_table.drop(["NOM_COMMUNE_ORIGINE"], axis=1), on="ID_COMMUNE",
                                how="left", validate="1:1")

        df_root = df_root.loc[df_root["NBR_DECES_2022"].notnull()]

        return df_root
    
    @timing
    def consolidate_departements(self):
        # TODO: more data at dep level
        df_dep = self.read_sql_data("DEPARTEMENT_CHOMAGE")
        return df_dep
    
    @timing
    def consolidate_zone_emploi(self):
        # TODO: more data at zone emploi level

        df_ze = self.read_sql_data("ZONE_EMPLOI_CHOMAGE")

        zone_emploi_tables = [x for x in self._tables_in_sql if "CLEAN" not in x \
                          and "CONSOLIDATE" not in x and "ZONE_EMPLOI" in x and
                          "CHOMAGE" not in x and "COMMUNE_" not in x]

        assert(len(zone_emploi_tables) == 3)

        for table_name in zone_emploi_tables:
            df_table = self.read_sql_data(table_name)
            df_ze = df_ze.merge(df_table.drop(["NOM_ZONE_EMPLOI"], axis=1), on="ID_ZONE_EMPLOI",
                                how="left", validate="1:1")

        return df_ze
    
    @timing
    def consolidate_carreaux_200m(self):

        df_met = self.read_sql_data("CARREAUX_200M_METROPOLE")
        df_reun = self.read_sql_data("CARREAUX_200M_REUNION")
        df_mart = self.read_sql_data("CARREAUX_200M_MARTINIQUE")

        df = pd.concat([df_met, df_mart, df_reun], axis=0)

        return df
    
    @timing
    def consolidate_carreaux_1km(self):

        df_met = self.read_sql_data("CARREAUX_1KM_METROPOLE")
        df_reun = self.read_sql_data("CARREAUX_1KM_REUNION")
        df_mart = self.read_sql_data("CARREAUX_1KM_MARTINIQUE")

        df = pd.concat([df_met, df_mart, df_reun], axis=0)

        return df