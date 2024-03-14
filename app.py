# import logging
import warnings
import pandas as pd
import streamlit as st
import app.web_app as ui

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide")


def main():

    st.title("Topic Extraction")

    ui.instatiate_session(st)
    widget_ui = ui.get_sidebar(st)
    displays = st.empty()

    if widget_ui["button"]:
        text_results = st.session_state["clustering"].query_collection(widget_ui["query_text"])
        # picture_results = step_picture_cluster.query_collection(widget_ui["picture_paths"])

        ui.get_display(st, text_results)

if __name__ == "__main__":
    main()