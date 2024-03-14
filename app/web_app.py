from src.context import get_config_context
from src.datacrawl.steps.step_text_clustering import StepTextClustering
import numpy as np

def get_sidebar(st):

    ui_inputs = {}
    
    st.sidebar.header("1) Art description to analyse")
    form = st.sidebar.form("my_form")

    form.header("How would you describe the art piece you want to estimate ?")
    ui_inputs["query_text"] = form.text_input("Enter your description            ")

    form.header("Any picture of the piece of art ?")
    ui_inputs["picture_paths"] = form.file_uploader("Art pictures", accept_multiple_files=True)

    ui_inputs["button"] = form.form_submit_button("Run Analysis")

    return ui_inputs


def get_display(st, text_results):
    display = {}

    distances = text_results["distances"][0]
    documents = text_results["documents"][0]
    description = text_results["metadatas"][0]

    estim_min = np.median([x["MIN_ESTIMATION"] for x in description])
    estim_max = np.median([x["MAX_ESTIMATION"] for x in description])
    result = np.median([x["FINAL_RESULT"] for x in description])

    st.header(f"Estimations  : {estim_min:.0f} - {estim_max:.0f} EUR ")
    st.header(f"Resultats : {result:.0f} EUR")
    st.write(f"Distance Moyenne : {np.mean(distances)*100:.2f}%")

    for i, doc in enumerate(description):
        st.divider()
        col1, col2 = st.columns([1, 2])

        doc['PICTURE_ID'] += ".jpg" 

        col2.write(f"Estimations : {doc["MIN_ESTIMATION"]} - {doc["MAX_ESTIMATION"]} {doc["CURRENCY"]}")
        col2.write(f"Resultat : {doc['FINAL_RESULT']}")
        col2.write(documents[i])
        col2.write(doc['URL_FULL_DETAILS'])

        if "MISSING" not in doc['PICTURE_ID']:
            col1.image(rf"C:/Users/alarr/Documents/repos/hart/data/drouot/pictures/{doc['PICTURE_ID']}", caption=f"Category : {doc['CATEGORY']} Distance : {distances[i]}", width=250)
        
    return display


def instatiate_session(st):

    if 'clustering' not in st.session_state:
        config, context = get_config_context('./configs', use_cache = False, save=False)
        st.session_state['clustering'] = StepTextClustering(context=context, config=config)
    
    return st

# Montre a gousset du 19eme plaqué or, en bon état de marche