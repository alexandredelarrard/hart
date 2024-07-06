# import logging
import numpy as np
import pandas as pd
import warnings
import streamlit as st
import matplotlib.pyplot as plt

from src.context import Context
from src.utils.step import Step

from src.modelling.transformers.Embedding import StepEmbedding
from src.modelling.transformers.ChromaCollection import ChromaCollection

from src.constants.variables import CHROMA_TEXT_DB_NAME, CHROMA_PICTURE_DB_NAME
from src.context import get_config_context
from omegaconf import DictConfig
from PIL import Image
import base64

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide")


def extract_info_meta_data(description, feature):
    serie = [x[feature] for x in description if x[feature] != ""]
    return pd.Series(serie)


def get_image_base64(path):
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return "data:image/png;base64," + encoded_string


def resize_images(image_path, width, height):
    img = Image.open(image_path)
    resized_image = img.resize((width, height))
    return resized_image


class WebAPP(Step):

    def __init__(self, context: Context, config: DictConfig):

        super().__init__(context=context, config=config)
        self.carousel_ncols = 4

    def run(self):

        st.title("Topic Extraction")

        self.instatiate_session()
        widget_ui = self.get_sidebar()

        if widget_ui["button"]:
            picture_results = None
            text_results = None

            if widget_ui["query_text"]:
                st.write(widget_ui["query_text"])
                embeddings = st.session_state["text_embedding"].get_text_embedding(
                    widget_ui["query_text"]
                )
                text_results = st.session_state["text_collection"].query_collection(
                    embeddings
                )

            if widget_ui["picture_paths"]:
                self.picture_path = (
                    f"D:/data/drouot/pictures/{widget_ui["picture_paths"].name}"
                )
                embeddings = st.session_state[
                    "picture_embedding"
                ].get_picture_embedding(self.picture_path)
                picture_results = st.session_state[
                    "picture_collection"
                ].query_collection(embeddings)

            # rag with context from results
            # generate summary
            # extract json format from summary
            # Display all to webapp

            self.get_display(text_results, picture_results)

    def instatiate_session(self):

        if "text_embedding" not in st.session_state:
            st.session_state["text_embedding"] = StepEmbedding(
                context=context, config=config, type="text"
            )

        if "picture_embedding" not in st.session_state:
            st.session_state["picture_embedding"] = StepEmbedding(
                context=context, config=config, type="picture"
            )

        if "collection" not in st.session_state:
            st.session_state["text_collection"] = ChromaCollection(
                context=self._context,
                data_name=CHROMA_TEXT_DB_NAME,
                config=self._config,
                n_top_results=48,
            )
            st.session_state["picture_collection"] = ChromaCollection(
                context=self._context,
                data_name=CHROMA_PICTURE_DB_NAME,
                config=self._config,
                n_top_results=48,
            )
        return st

    def get_sidebar(self):

        ui_inputs = {}

        st.sidebar.header("1) Art description to analyse")
        form = st.sidebar.form("my_form")

        form.header("How would you describe the art piece you want to estimate ?")
        ui_inputs["query_text"] = form.text_input("Enter your description")

        form.header("Any picture of the piece of art ?")
        ui_inputs["picture_paths"] = form.file_uploader(
            "Art pictures", accept_multiple_files=False
        )

        ui_inputs["button"] = form.form_submit_button("Run Analysis")

        return ui_inputs

    def get_display(self, text_results, picture_results):

        if picture_results and text_results:
            tab1, tab2 = st.tabs(["Text", "Pictures"])
        elif text_results:
            tab1 = st
        elif picture_results:
            tab2 = st
        else:
            st.write("Please submit either picture or text")

        if text_results:
            self.display_text_results(tab1, text_results)

        if picture_results:
            self.display_text_results(tab2, picture_results)

    def display_text_results(self, tab1, text_results):

        distances = text_results["distances"][0]
        documents = text_results["documents"][0]
        description = text_results["metadatas"][0]

        estim_min = extract_info_meta_data(description, self.name.min_estimate)
        estim_max = extract_info_meta_data(description, self.name.max_estimate)
        result = extract_info_meta_data(description, self.name.item_result)

        tab_col1, tab_col2, tab_col3 = tab1.columns([2, 2, 2])
        with tab_col1.container(height=400, border=False):
            st.image(self.picture_path, use_column_width=True)

        with tab_col2.container(height=400, border=False):
            st.header(
                f"Estimations  : {estim_min.median():.0f} - {estim_max.median():.0f} EUR "
            )
            st.header(f"Resultats : {result.median():.0f} EUR")
            st.write(f"Distance Moyenne : {np.median(distances)*100:.2f}%")

        # Affichez le tracé dans Streamlit
        with tab_col3.container(height=400, border=False):
            fig, ax = plt.subplots()
            ax.hist(result, bins=25)
            st.pyplot(fig)

        grid = self.create_grid(description, ncols=self.carousel_ncols)

        for i, doc in enumerate(description):
            with grid[i].container():
                self.info_in_container(doc, documents[i], distances[i])

    def create_grid(self, description, ncols=3):
        dim_ = len(description)
        nbr_row = dim_ // ncols + 1
        grid = []
        for _ in range(nbr_row):
            row = st.columns(ncols)
            grid = grid + [col.container(height=500) for col in row]
        return grid

    def info_in_container(self, doc, document, distance):
        if "MISSING" not in doc[self.name.id_picture]:
            try:
                st.image(
                    f"D:/data/{doc[self.name.seller]}/pictures/{doc[self.name.id_picture]}.jpg",
                    caption=f"Date: {doc[self.name.date]} / Distance : {distance:0.2f} ",
                )
                st.write(
                    f"Resultat: {doc[self.name.item_result]} / "
                    + f"Estimations: {doc[self.name.min_estimate]}-{doc[self.name.max_estimate]} {doc[self.name.currency]}"
                )
                st.write(document)
                st.write(doc[self.name.url_full_detail])
            except Exception:
                pass


if __name__ == "__main__":
    config, context = get_config_context("./configs", use_cache=False, save=False)
    app = WebAPP(config=config, context=context)
    app.run()
