import streamlit as st
from functions.functions_Reliability import *


from sklearn.model_selection import train_test_split
from functions.functions import *
from sklearn.metrics import accuracy_score
import pickle

try:
    host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
    host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
except:
    st.info("Please select a database first")
    st.stop()

tab1, tab2 = st.tabs(["Data", "Model"])


with tab2:
    from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
    from sklearn.impute import SimpleImputer
    from sklearn.compose import ColumnTransformer

    try:
        # divide df based on level of measurement
        nominal = [key for key, value in st.session_state.level_of_measurement_dic.items() if value == 'Nominal']
        ordinal = [key for key, value in st.session_state.level_of_measurement_dic.items() if value == 'Ordinal']
        cardinal = [key for key, value in st.session_state.level_of_measurement_dic.items() if value == 'Cardinal']

        # st.write(df[[key for key, value in st.session_state.level_of_measurement_dic.items() if value == 'Nominal']])
        ct = ColumnTransformer(transformers=[("OneHot", OneHotEncoder(handle_unknown='ignore'), nominal),
                                             ("Ordinal", OrdinalEncoder(handle_unknown='error'), ordinal),
                                             ("Cardinal", SimpleImputer(strategy='median'), cardinal)],
                               remainder='drop', verbose_feature_names_out=False)

        x_trans_df = pd.DataFrame(ct.fit_transform(st.session_state['X']), columns=ct.get_feature_names_out())

        X_train, X_test, y_train, y_test = train_test_split(x_trans_df, st.session_state['y'], test_size=0.2,
                                                            random_state=1234)
        #
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
        # # TODO: Encode Nominal and Ordinal Values and decode them again to visualize the results


        clf.fit(X_train, y_train)
        st.session_state['model']  = clf
        y_pred = pd.DataFrame(clf.predict(X_test))
        #
        #
        df_result = pd.DataFrame(X_test.reset_index(), columns=ct.get_feature_names_out())

        # if df_result not in st.session_state:
        #     st.session_state['df_result'] = None
        df_result["Prediction"] = y_pred
        st.write(df_result)
        # st.session_state['df_result'] = df_result
        #
        #
        acc = accuracy_score(y_test, y_pred)

        st.write(f'Classifier = {st.session_state["classifier_name"]}')
        st.write(f'Accuracy =', acc)
        #
        #
        filename = st.text_input("Enter the name of the model", ".sav")

        if st.button("Save Model"):
            pickle.dump(clf, open(filename, 'wb'))
        st.download_button("Download Model", data=pickle.dumps(clf), file_name="model.pkl")
    except Exception as e:
        st.write(e)
        pass


with tab1:
    st.markdown("Upload Model")
    if "model" in st.session_state:
        st.write(st.session_state['model'].feature_names_in_)
    loaded_model2 = st.file_uploader("Upload Model")

    if loaded_model2 is None:
        pass
    else:
        loaded_model = pickle.load(loaded_model2)
        st.write(type(loaded_model))
        st.write(loaded_model.feature_names_in_)
        st.session_state.model = loaded_model

