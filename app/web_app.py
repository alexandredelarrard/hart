import numpy as np
import pandas as pd 

def extract_info_meta_data(description, feature):
    serie = [x[feature] for x in description if x[feature] != ""]
    return pd.Series(serie)

def get_sidebar(st):

    ui_inputs = {}
    
    st.sidebar.header("1) Art description to analyse")
    form = st.sidebar.form("my_form")

    form.header("How would you describe the art piece you want to estimate ?")
    ui_inputs["query_text"] = form.text_input("Enter your description")

    form.header("Any picture of the piece of art ?")
    ui_inputs["picture_paths"] = form.file_uploader("Art pictures", accept_multiple_files=False)

    ui_inputs["button"] = form.form_submit_button("Run Analysis")

    return ui_inputs


def get_display(st, text_results, picture_results, naming):

    if picture_results and text_results:
        tab1, tab2 = st.tabs(["Text", "Pictures"])
    elif text_results:
        tab1 = st
    elif picture_results:
        tab2 = st
    else:
        st.write("Please submit either picture or text")

    if text_results:
        display_text_results(tab1, text_results, naming)
        
    if picture_results:
        display_text_results(tab2, picture_results, naming)
        

def display_text_results(tab1, text_results, naming):

    distances = text_results["distances"][0]
    documents = text_results["documents"][0]
    description = text_results["metadatas"][0]

    estim_min = extract_info_meta_data(description, naming.eur_min_estimate).median()
    estim_max = extract_info_meta_data(description, naming.eur_max_estimate).median()
    result = extract_info_meta_data(description, naming.eur_item_result).median()

    tab1.header(f"Estimations  : {estim_min:.0f} - {estim_max:.0f} EUR ")
    tab1.header(f"Resultats : {result:.0f} EUR")
    tab1.write(f"Distance Moyenne : {np.median(distances)*100:.2f}%")

    for i, doc in enumerate(description):
        tab1.divider()
        col1, col2 = tab1.columns([1, 2])

        col2.write(f"Estimations : {doc[naming.eur_min_estimate]} - {doc[naming.eur_max_estimate]} {doc[naming.currency]}")
        col2.write(f"Resultat : {doc[naming.eur_item_result]}")
        col2.write(documents[i])

        try:
            col2.write(doc[naming.url_full_detail])
        except Exception:
            pass

        if "MISSING" not in doc[naming.id_picture]:
            try:
                col1.image(f"D:/data/{doc[naming.seller]}/pictures/{doc[naming.id_picture]}.jpg", 
                           caption=f"Distance : {distances[i]}", 
                           width=250)
            except Exception:
                pass