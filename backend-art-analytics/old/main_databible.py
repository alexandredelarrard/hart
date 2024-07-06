from src.context import get_config_context

from src.databible.steps.step_data_load import StepDataLoad
from src.databible.steps.step_data_clean import StepDataClean
from src.databible.steps.step_data_consolidate import StepDataConsolidate

if __name__ == "__main__":
    """
    TODO:
        - extraire les carreaux et donnees carroyées
        - extraire les data au zipcode de l'insee
        - extraire dvf
        - extraire données de vote
        - extraire données fiscales
        - extraire données meteo zipcode ?
        - extraire données POI / google maps
        - extraire données de surface (arbre , eau, altitude, etc.)
        - extraire données location / se loger
        - extraire données airbnb
        - extraire données flux : gaz / routier / internet / rte elec
        - automatiser la maj des flux
    """

    config, context = get_config_context("./configs", use_cache=False, save=False)

    # load data
    dataload = StepDataLoad(config, context)
    dataload.run()

    consolidate = StepDataConsolidate(config, context)
    consolidate.run()

    self = StepDataClean(config, context)
    # self.run()
