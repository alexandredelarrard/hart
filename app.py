# import logging

import warnings
import pandas as pd
import streamlit as st
import app.web_app as ui

from src.context import Context
from src.utils.step import Step

from src.modelling.steps.step_text_clustering import StepTextClustering
from src.modelling.steps.step_picture_clustering import StepPictureClustering
from src.modelling.transformers.ChromaCollection import ChromaCollection

from src.constants.variables import CHROMA_TEXT_DB_NAME
from src.context import get_config_context
from omegaconf import DictConfig

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide")


class WebAPP(Step):
   
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)

    def run(self):

        st.title("Topic Extraction")

        self.instatiate_session(st)
        widget_ui = ui.get_sidebar(st)

        if widget_ui["button"]:
            picture_results= None
            text_results=None

            if widget_ui["query_text"]:
                st.write(widget_ui["query_text"])
                embeddings = st.session_state["text_clustering"].text_to_embedding(widget_ui["query_text"])
                text_results = st.session_state["collection"].query_collection(embeddings)

            if widget_ui["picture_paths"]:
                st.write(widget_ui["picture_paths"])
                picture_results = st.session_state["picture_clustering"].query_collection("/".join([st.session_state['picture_path'], widget_ui['picture_paths'].name]))

            ui.get_display(st, text_results, picture_results, self.name)


    def instatiate_session(self, st):

        if 'text_clustering' not in st.session_state:
            st.session_state['text_clustering'] = StepTextClustering(context=self._context, 
                                                                     config=self._config)

        # if "picture_clustering" not in st.session_state:
        #     st.session_state['picture_clustering'] = StepPictureClustering(context=context, config=config)

        if "collection" not in st.session_state:
            st.session_state["collection"] = ChromaCollection(context=self._context,
                                                              data_name=CHROMA_TEXT_DB_NAME, 
                                                              config=self._config)

        if "picture_path" not in st.session_state:
            st.session_state['picture_path'] = r"D:/data/drouot/pictures_old" #config.crawling.drouot.save_picture_path
        
        return st


if __name__ == "__main__":
    config, context = get_config_context('./configs', use_cache = False, save=False)
    app = WebAPP(config=config, context=context)
    app.run()