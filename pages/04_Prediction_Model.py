import os
import pickle

import pandas as pd
import streamlit as st
import streamlit_nested_layout

from SPARQLWrapper import SPARQLWrapper
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from streamlit_extras.switch_page_button import switch_page

from functions.functions import add_parameter_ui, get_classifier
from functions.fuseki_connection import login_analyst, get_dataset, getUniqueValuesSeq

login_analyst()

host, host_upload = get_dataset()

try:
    getUniqueValuesSeq(host)

except Exception as e:
    st.error("Please upload feature values in Data Understanding step")
    if st.button("Data Understanding"):
        switch_page("Data Understanding")
    st.stop()




tab1, tab2 = st.tabs(["Data", "Model"])

with tab1:
    option=st.radio(label="Select",options=["Select", "Upload"])
    if option=="Select":
        models = os.listdir("/Users/pascal/Studium/Masterthesis/model")
        st.write(models)
        loaded_model2 = st.selectbox(label="Select model", options = models)

    else:
        st.markdown("Upload Model")
        if "model" in st.session_state:
            st.write(st.session_state['model'].feature_names_in_)
        loaded_model2 = st.file_uploader("Upload Model")
        model_name = st.session_state.fuseki_database
        if model_name != "":
            with open(os.path.join("/Users/pascal/Studium/Masterthesis/model", ""), 'wb') as f:
                pickle.dump(f, loaded_model2)


    if loaded_model2 is not None:
        with open(os.path.join("/Users/pascal/Studium/Masterthesis/model", loaded_model2), 'rb') as f:
            loaded_model = pickle.load(f)
        st.success("Model uploaded")
        st.session_state.model = loaded_model
        with st.expander("Show model information:"):
            st.write(type(loaded_model))
            st.write(loaded_model.feature_names_in_)





with tab2:
    from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
    from sklearn.impute import SimpleImputer
    from sklearn.compose import ColumnTransformer

    try:
        # divide df based on level of measurement
        nominal = [key for key, value in st.session_state.level_of_measurement_dic.items() if value == 'Nominal']
        ordinal = [key for key, value in st.session_state.level_of_measurement_dic.items() if value == 'Ordinal']
        cardinal = [key for key, value in st.session_state.level_of_measurement_dic.items() if value == 'Cardinal']

        # pipeline for transforming ordinal, cardinal and nominal values
        ct = ColumnTransformer(transformers=[("OneHot", OneHotEncoder(handle_unknown='ignore'), nominal),
                                             ("Ordinal", OrdinalEncoder(handle_unknown='error'), ordinal),
                                             ("Cardinal", SimpleImputer(strategy='median'), cardinal)],
                               remainder='drop', verbose_feature_names_out=False)


        try:
            x_trans_df = pd.DataFrame(ct.fit_transform(st.session_state['X']).toarray(), columns=ct.get_feature_names_out())
        except Exception as e:
            x_trans_df = pd.DataFrame(ct.fit_transform(st.session_state['X']), columns=ct.get_feature_names_out())



        X_train, X_test, y_train, y_test = train_test_split(x_trans_df, st.session_state['y'], test_size=0.2,
                                                            random_state=1234)

        st.markdown("Define Model")
        # Select classifier
        classifier_name = st.sidebar.selectbox(
            'Select classifier',
            ('KNN', 'SVM', 'Random Forest')
        )
        if classifier_name is not None:
            st.session_state['classifier_name'] = classifier_name


        params = add_parameter_ui(st.session_state['classifier_name'])
        #
        clf = get_classifier(st.session_state['classifier_name'], params)
        # #### CLASSIFICATION ####

        clf.fit(X_train, y_train)
        st.session_state['model']  = clf
        y_pred = pd.DataFrame(clf.predict(X_test))

        df_result = pd.DataFrame(X_test.reset_index(), columns=ct.get_feature_names_out())

        df_result["Prediction"] = y_pred
        st.write(df_result)

        acc = accuracy_score(y_test, y_pred)

        st.write(f'Classifier = {st.session_state["classifier_name"]}')
        st.write(f'Accuracy =', acc)

        st.download_button("Download Model", data=pickle.dumps(clf), file_name=str(st.session_state.fuseki_database+".pkl"))
    except:
        st.info("Model generation only available with training data")











