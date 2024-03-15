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

    if widget_ui["button"]:
        picture_results= None
        text_results=None

        if widget_ui["query_text"]:
            st.write(widget_ui["query_text"])
            text_results = st.session_state["text_clustering"].query_collection(widget_ui["query_text"])

        if widget_ui["picture_paths"]:
            st.write(widget_ui["picture_paths"])
            picture_results = st.session_state["picture_clustering"].query_collection("/".join([st.session_state['picture_path'], widget_ui['picture_paths'].name]))

        ui.get_display(st, text_results, picture_results)

if __name__ == "__main__":
    main()