from src.context import get_config_context
from src.modelling.steps.step_text_clustering import StepTextClustering
# from src.modelling.steps.step_picture_classification import StepPictureClustering
import numpy as np

def get_sidebar(st):

    ui_inputs = {}
    
    st.sidebar.header("1) Art description to analyse")
    form = st.sidebar.form("my_form")

    form.header("How would you describe the art piece you want to estimate ?")
    ui_inputs["query_text"] = form.text_input("Enter your description            ")

    form.header("Any picture of the piece of art ?")
    ui_inputs["picture_paths"] = form.file_uploader("Art pictures", accept_multiple_files=False)

    ui_inputs["button"] = form.form_submit_button("Run Analysis")

    return ui_inputs


def get_display(st, text_results, picture_results):

    if picture_results and text_results:
        tab1, tab2 = st.tabs(["Text", "Pictures"])
    elif text_results:
        tab1 = st
    elif picture_results:
        tab2 = st
    else:
        st.write("Please submit either picture or text")

    if text_results:
        display_text_results(tab1, text_results)
        
    if picture_results:
        display_text_results(tab2, picture_results)


def display_text_results(tab1, text_results):

    distances = text_results["distances"][0]
    documents = text_results["documents"][0]
    description = text_results["metadatas"][0]

    estim_min = np.median([x["MIN_ESTIMATION"] for x in description])
    estim_max = np.median([x["MAX_ESTIMATION"] for x in description])
    result = np.median([x["FINAL_RESULT"] for x in description])

    tab1.header(f"Estimations  : {estim_min:.0f} - {estim_max:.0f} EUR ")
    tab1.header(f"Resultats : {result:.0f} EUR")
    tab1.write(f"Distance Moyenne : {np.mean(distances)*100:.2f}%")

    for i, doc in enumerate(description):
        tab1.divider()
        col1, col2 = tab1.columns([1, 2])

        doc['PICTURE_ID'] += ".jpg" 

        col2.write(f"Estimations : {doc["MIN_ESTIMATION"]} - {doc["MAX_ESTIMATION"]} {doc["CURRENCY"]}")
        col2.write(f"Resultat : {doc['FINAL_RESULT']}")
        col2.write(documents[i])
        col2.write(doc['URL_FULL_DETAILS'])

        if "MISSING" not in doc['PICTURE_ID']:
            col1.image(rf"C:/Users/alarr/Documents/repos/hart/data/drouot/pictures_old/{doc['PICTURE_ID']}", caption=f"Category : {doc['CATEGORY']} Distance : {distances[i]}", width=250)



def display_picture_results(tab2, picture_results):

    distances = picture_results["distances"][0]
    documents = picture_results["documents"][0]
    description = picture_results["metadatas"][0]

    estim_min = np.median([x["MIN_ESTIMATION"] for x in description])
    estim_max = np.median([x["MAX_ESTIMATION"] for x in description])
    result = np.median([x["FINAL_RESULT"] for x in description])

    tab2.header(f"Estimations  : {estim_min:.0f} - {estim_max:.0f} EUR ")
    tab2.header(f"Resultats : {result:.0f} EUR")
    tab2.write(f"Distance Moyenne : {np.mean(distances)*100:.2f}%")

    for i, doc in enumerate(description):
        tab2.divider()
        col1, col2 = tab2.columns([1, 2])

        doc['PICTURE_ID'] += ".jpg" 

        col2.write(f"Estimations : {doc["MIN_ESTIMATION"]} - {doc["MAX_ESTIMATION"]} {doc["CURRENCY"]}")
        col2.write(f"Resultat : {doc['FINAL_RESULT']}")
        col2.write(documents[i])
        col2.write(doc['URL_FULL_DETAILS'])

        if "MISSING" not in doc['PICTURE_ID']:
            col1.image(rf"C:/Users/alarr/Documents/repos/hart/data/drouot/pictures_old/{doc['PICTURE_ID']}", caption=f"Category : {doc['CATEGORY']} Distance : {distances[i]}", width=250)


def instatiate_session(st):

    if 'text_clustering' not in st.session_state:
        config, context = get_config_context('./configs', use_cache = False, save=False)
        st.session_state['text_clustering'] = StepTextClustering(context=context, config=config)

    # if "picture_clustering" not in st.session_state:
    #     config, context = get_config_context('./configs', use_cache = False, save=False)
    #     st.session_state['picture_clustering'] = StepPictureClassification(context=context, config=config)

    if "picture_path" not in st.session_state:
        config, context = get_config_context('./configs', use_cache = False, save=False)
        st.session_state['picture_path'] = r"C:/Users/alarr/Documents/repos/hart/data/drouot/pictures_old"#config.crawling.drouot.save_picture_path
    
    return st
