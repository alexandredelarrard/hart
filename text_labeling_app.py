import warnings
import pandas as pd
import streamlit as st
import numpy as np

from src.context import Context
from src.utils.step import Step

from src.constants.class_map import class_mapping
from src.context import get_config_context
from omegaconf import DictConfig
from time import time 

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide")

class WebAPP(Step):
   
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)
        self.save_label_to = r'D:\data\text_training\labeled_text.txt'
        self.read_data_to_label_path = r"D:\data\text_training\training_classes.csv"
        self.class_options = list(class_mapping.values())

    def run(self):

        st.title("Text labelling")
        self.instatiate_session(st)
        col1, col2, col3 = st.columns([2, 3, 1])

        if st.session_state['index'] < len(st.session_state['data']):
            self.get_display(st, col1, col2, col3)
            if col3.button('Save Label'):
                if self.user_input:
                    user_input = self.user_input
                if self.user_input_new:
                    user_input = self.user_input_new
                self.save_labelling(self.id_item, user_input)
                st.session_state['index'] +=1
                st.experimental_rerun()
                
    def instatiate_session(self, st):

        if "data" not in st.session_state:
            df = pd.read_csv(self.read_data_to_label_path, sep=";")
            df = df.loc[0.98>df["PROBA_0"]]

            df_done= pd.read_csv(self.save_label_to, header=None)
            df = df.loc[~df["ID_ITEM"].isin(df_done[0].tolist())]

            df = df.sort_values(["TOP_0", "PROBA_0"], ascending=True)
                
            st.session_state['data'] = df.to_dict(orient="records")
        
        if "index" not in st.session_state:
            st.session_state['index'] = 0

        if "options" not in st.session_state:
            st.session_state['options'] = list(np.sort(list(df_done[1].unique()))) # self.class_options + 

        return st
    
    def get_display(self, st, col1, col2, col3):
        
        row = st.session_state['data'][st.session_state['index']]

        try:
            col1.image(f"D:/data/{row["SELLER"]}/pictures/{row["ID_PICTURE"]}.jpg", 
                        width=350)
        except Exception:
            pass
        
        col2.write(f"Description: {row["text"]}")
        col2.write(f"URL: {row["URL_FULL_DETAILS"]}")
        self.user_input = col3.selectbox(f'Proba: {row["PROBA_0"]}/ Options', 
                                       options=st.session_state['options'],
                                       index=None,
                                       placeholder=f"Predicted : {row["TOP_0"]}")

        # Create text input for user entry
        self.user_input_new = col3.text_input("Nouvelle categorie", None)
        if self.user_input_new:
            st.session_state['options'] = list(np.sort(st.session_state['options'] + [self.user_input_new]))

        self.id_item = row["ID_ITEM"]
        col3.write(f"ROW ID: {st.session_state['index']}/{len(st.session_state['data'])}")

    def save_labelling(self, id_item, user_input):
        with open(self.save_label_to, 'a') as file:
            file.write(f"{id_item}, {user_input}\n")
        
if __name__ == "__main__":
    config, context = get_config_context('./configs', use_cache = False, save=False)
    app = WebAPP(config=config, context=context)
    app.run()