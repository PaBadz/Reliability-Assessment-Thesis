import os.path
import uuid
import streamlit_nested_layout

import pandas as pd
import requests
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from SPARQLWrapper import SPARQLWrapper, JSON, POST
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
from yaml.loader import SafeLoader


from functions.fuseki_connection import host_dataset_first_initialize, set_database, getTimestamp, \
    determinationActivity, upload_features, getAttributes, get_feature_names, prefix, uploadUniqueValues, \
    get_connection_fuseki

st.set_page_config(
    page_title="Masterthesis Pascal Badzura",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.streamlit.io/en/stable/getting_started.html',
        'About': "# This is the Masterthesis of Pascal Badzura."
    }
)





with open(os.path.join(os.path.abspath(os.getcwd()),"config.yaml"))as file:
    config = yaml.load(file, Loader=SafeLoader)


authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

if "username" not in st.session_state:
    name, authentication_status, username = authenticator.login('Login', 'main')
    st.session_state.username = username


name, authentication_status, username = authenticator.login('Login', 'main')


if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{st.session_state["name"]}*')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
    st.stop()
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
    with st.expander("Register new user"):
        try:
            if authenticator.register_user('Register user', preauthorization=False):
                st.success('User registered successfully')
                with open(os.path.join(os.path.abspath(os.getcwd()),"config.yaml"), 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
        except Exception as e:
            st.error(e)
    st.stop()


def get_dataset_from_fuseki():
    sparql = SPARQLWrapper(host_dataset_first_initialize)
    sparql.setReturnFormat(JSON)
    fuseki_datasets = sparql.query().convert()

    # if 'fueski_dataset_options' not in st.session_state:
    st.session_state['fueski_dataset_options'] = ["None"]
    for dataset in fuseki_datasets["datasets"]:
        st.session_state['fueski_dataset_options'].append(dataset["ds.name"])

    if 'fueski_dataset_options' not in st.session_state:
        st.stop()

    if 'fuseki_database' not in st.session_state:
        st.session_state['fuseki_database'] = "None"


if st.session_state.username == "analyst":
    colored_header(
        label="Masterthesis",
        description="Design and Implementation of a web-based User Interface for the guided Assessment of Reliability of Classification Results using the Perturbation Approach",
        color_name="red-70"
    )

    # if st.button('Load all datasets from Fuseki', type='primary'):
        # Get all datasets from fuseki
    get_dataset_from_fuseki()
    sparql = SPARQLWrapper(host_dataset_first_initialize)
    # sparql.setCredentials("admin", "vesB24jhOU4zxNy")
    sparql.setReturnFormat(JSON)
    fuseki_datasets = sparql.query().convert()

    if 'fueski_dataset_options' not in st.session_state:
        st.session_state['fueski_dataset_options'] = ["None"]
        for dataset in fuseki_datasets["datasets"]:
            st.session_state['fueski_dataset_options'].append(dataset["ds.name"])

    if 'fueski_dataset_options' not in st.session_state:
        st.stop()

    if 'fuseki_database' not in st.session_state:
        st.session_state['fuseki_database'] = "None"
    index = st.session_state['fueski_dataset_options'].index(st.session_state['fuseki_database'])

    st.session_state.fuseki_database = st.selectbox('Please select dataset', index=index,
                                                    options=st.session_state['fueski_dataset_options'],
                                                    on_change=set_database, key='name_fuseki_database')

    host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
    host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
    st.warning("Please switch to Deployment page")
    want_to_contribute = st.button("Deployment",type="primary")
    if want_to_contribute:
        switch_page("Deployment")
    st.stop()




colored_header(
        label="Masterthesis of Pascal Badzura",
        description="Design and Implementation of a web-based User Interface for the guided Assessment of Reliability of Classification Results using the Perturbation Approach",
        color_name="red-70"
    )


success = False
selected2 = option_menu(None, ["Select dataset", "Upload dataset"],
                        icons=['nothing','cloud-upload'],
                        menu_icon="", default_index=0, orientation="horizontal")
st.write('--------------')
# st.markdown("**In Order to continue please upload a dataset to the server or choose a dataset from the database**")

if selected2 == 'Upload dataset':
    st.info("If there is no dataset please open expander below and create dataset.")

    with st.expander("Create new dataset"):
        new_dataset = st.text_input("Insert dataset name")
        if st.button("Create new dataset"):
            headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                       'Authorization': 'Basic $(echo -n admin:password | base64)'}
            r = requests.post(host_dataset_first_initialize, data=f"dbName={new_dataset.replace(' ', '')}&dbType=tdb",
                              headers=headers)

            get_dataset_from_fuseki()
            st.success("New dataset created")


# Get all datasets from fuseki
get_dataset_from_fuseki()




index = st.session_state['fueski_dataset_options'].index(st.session_state['fuseki_database'])

st.session_state.fuseki_database = st.selectbox('Please select dataset', index=index,options=st.session_state['fueski_dataset_options'],on_change=set_database, key='name_fuseki_database')
host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")

if not any(key.startswith('level_of_measurement_') for key in st.session_state):
    st.session_state["dataframe_feature_names"] = get_feature_names(host)



if st.session_state.fuseki_database=="None":
    st.stop()



if selected2 == "Select dataset":
    st.markdown("#### Process of reliability of predictions based on CRISP-DM")
    st.markdown("""CRISP-DM stands for Cross Industry Standard for Data Mining Processes. In this Web App you will be able to reproduce the process of reliability of predictions based on CRISP-DM. The process is divided into 6 steps: 
    """)

    page = st.button("Business Understanding")
    if page:
        switch_page("Business Understanding")

    page = st.button("Data Understanding")
    if page:
        switch_page("Data Understanding")

    page = st.button("Data Preparation")
    if page:
        switch_page("Data Preparation")

    page = st.button("Upload Model")
    if page:
        switch_page("Prediction Model")

    page = st.button("Modeling Perturbation Options")
    if page:
        switch_page("Modeling")

    page = st.button("Deploy Perturbation Options")
    if page:
        switch_page("Deployment")

if selected2 == 'Upload dataset':
    st.write("---------------------")
    upload_option = st.radio(label ="Select upload option",options=["JSON", "CSV"])


    if upload_option == "JSON":

        with st.expander("File needs to follow this schema"):
            st.json("""{
      "FeatureName1": {"levelOfScale": "Cardinal", 	"uniqueValues": ["minValue", "maxValue"]},
      "FeatureName2": {"levelOfScale": "Nominal", 	"uniqueValues": ["x", "y","z"]},
      "FeatureName3": {"levelOfScale": "Ordinal", 	"uniqueValues": ["1", "2", "3"]}
    }
    """)



        uploaded_file = st.file_uploader(f"Upload JSON file", accept_multiple_files=False,
                                         on_change=set_database)
        if not uploaded_file:
            st.stop()

        st.info("When data is uploaded via JSON, the steps Determination of level of scale and Creation of order of ordinal data are automatically created and unique values are uploaded.")


        import json


        uploaded_file_bytes = uploaded_file.read()

        uploaded_file_JSON = json.loads(uploaded_file_bytes.decode('utf-8'))



        determinationNameUUID = 'DeterminationOfFeature'
        determinationName = 'DeterminationOfFeature'
        label = '"detOfFeature"@en'
        name = 'Feature'
        rprovName = 'Feature'

        if st.button(f"Upload dataset to {st.session_state.fuseki_database}", type='primary'):
            # insert first RDF into graph
            data = open('example_upload.ttl').read()
            headers = {'Content-Type': 'text/turtle;charset=utf-8'}

            r = requests.put(f"http://localhost:3030{st.session_state.fuseki_database}?default", data,
                             headers=headers)

            sparqlupdate = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
            uuid_determinationFeature = uuid.uuid4()
            starting_time = getTimestamp()
            ending_time = getTimestamp()



            uuid_determinationFeature = determinationActivity(host_upload, determinationName, label,
                                                              starting_time, ending_time)



            for key in uploaded_file_JSON.keys():
                uuid_Feature = uuid.uuid4()
                upload_features(host_upload, uuid_Feature, key, uuid_determinationFeature)
            uuid_determinationScale = determinationActivity(host_upload, "DeterminationOfScaleOfFeature", "detScaleOfFeature@en",
                                                            starting_time, ending_time)

            st.info("Uploading Unique Values. This process may take a while.")
            st.write(uploaded_file_JSON)

            for key in uploaded_file_JSON.keys():

                query = (f"""PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                            PREFIx rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        SELECT ?subject WHERE {{?subject rdf:type rprov:Feature. ?subject rdfs:label '{key}'}}""")
                results_update = get_connection_fuseki(host, query)

                result_2 = pd.json_normalize(results_update["results"]["bindings"])

                uuid_ScaleOfFeature = uuid.uuid4()

                dicName = 'level_of_measurement_dic'
                rprovName = 'scale'

                query = (f"""INSERT DATA {{<urn:uuid:{uuid_ScaleOfFeature}> rdf:type rprov:ScaleOfFeature, owl:NamedIndividual;
                              rprov:{rprovName} "{uploaded_file_JSON[key]["levelOfScale"]}";
                              rdfs:label "{rprovName} {key}"@en;
                              rprov:toFeature <{result_2["subject.value"][0]}>;
                              rprov:wasGeneratedByDUA  <urn:uuid:{uuid_determinationScale}>;
                              prov:generatedAtTime '{ending_time}'^^xsd:dateTime.
                            }}""")
                sparqlupdate.setQuery(prefix + query)
                sparqlupdate.setMethod(POST)
                sparqlupdate.query()



                ##### UNIQUE VALUES


                determinationNameUUID = 'DeterminationOfUniqueValuesOfFeature_'
                determinationName = 'DeterminationOfUniqueValuesOfFeature'
                label = '"detUniqueValuesOfFeature"@en'
                dicName = 'unique_values_of_features_dic'
                name = 'UniqueValuesOfFeature'
                rprovName = 'uniqueValues'
                try:
                    ending_time = getTimestamp()
                    uuid_determinationUniqueValues = determinationActivity(host_upload,determinationName, label, starting_time, ending_time)

                    uuid_UniqueValues_entity = uuid.uuid4()
                    uuid_UniqueValues_seq = uuid.uuid4()

                    query = (f"""INSERT DATA {{<urn:uuid:{uuid_UniqueValues_entity}> rdf:type rprov:{name}, owl:NamedIndividual;
                                                  rprov:{rprovName} <urn:uuid:{uuid_UniqueValues_seq}>;
                                                  rdfs:label "{rprovName} {key}";
                                                  rprov:toFeature <{result_2["subject.value"][0]}>;
                                                  rprov:wasGeneratedByDUA  <urn:uuid:{uuid_determinationUniqueValues}>;
                                                  prov:generatedAtTime '{ending_time}'^^xsd:dateTime;
                                                }}""")
                    sparqlupdate.setQuery(prefix + query)
                    sparqlupdate.setMethod(POST)
                    sparqlupdate.query()

                    if uploaded_file_JSON[key]["levelOfScale"] == "Nominal":
                        i = 0
                        for values in uploaded_file_JSON[key]["uniqueValues"]:
                            query = (f"""INSERT DATA {{<urn:uuid:{uuid_UniqueValues_seq}> rdf:type rdf:Bag, owl:NamedIndividual;
                                                              rdf:_{i}  '{values}';}}""")
                            sparqlupdate.setQuery(prefix + query)
                            sparqlupdate.setMethod(POST)
                            sparqlupdate.query()
                            i = i + 1
                    else:
                        i = 0
                        for values in uploaded_file_JSON[key]["uniqueValues"]:
                            query = (f"""INSERT DATA {{<urn:uuid:{uuid_UniqueValues_seq}> rdf:type rdf:Seq, owl:NamedIndividual;
                                                              rdf:_{i}  '{values}';}}""")
                            sparqlupdate.setQuery(prefix + query)
                            sparqlupdate.setMethod(POST)
                            sparqlupdate.query()
                            i = i + 1
                except Exception as e:
                    st.error(e)

            switch_page("Data Understanding")


    if upload_option == "CSV":

        uploaded_file = st.file_uploader("Upload file to the server", accept_multiple_files=False,on_change=set_database)

        if not uploaded_file:
            st.stop()
        starting_time = getTimestamp()

        if uploaded_file is not None:
            uploaded_file_df = pd.read_csv(uploaded_file)

        st.info("""If data is uploaded via CSV, the steps Determination of level of scale and Creation of order of ordinal data must be created manually and unique values uploaded.
The following steps are necessary for this:

1) Select Target variable
2) Upload features to server

The data is forwarded to the data understanding step, where the following steps must be taken:

3) Determination of scale
4) Determination of order for ordinal data
5) Upload unique values """)
        st.dataframe(uploaded_file_df,use_container_width=True)
        if 'dataset' not in st.session_state:
            st.session_state['dataset'] = 'None'

        if "unique_values_dict" not in st.session_state:
            with st.form(key="formUploadFeatures"):
                # Dataset will be split and saved in the database
                # select target variable
                y = st.selectbox('Select target variable', uploaded_file_df.columns, index=len(uploaded_file_df.columns) - 1, help="By default, the last column is selected as the target variable.")

                X = uploaded_file_df.drop(y, axis=1)

                y = uploaded_file_df[y]
                df = pd.DataFrame(data=X, columns=X.columns)

                if st.session_state.fuseki_database == 'None':
                    st.stop()
                host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
                host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")



                X = df



                if uploaded_file_df is not None:
                    df = pd.DataFrame(data=X, columns=X.columns)
                    st.session_state['df'] = df
                    st.session_state['X'] = X

                    # y needed if model is generated in this webapp
                    st.session_state['y'] = y
                else:
                    st.write("No Data")
                    st.stop()


            # TODO outsource to function
            # Determination of feature


            # if st.button("Upload dataset to the server", type='primary', help="Determines the features of the dataset, in the next step you can determine the scale of the features"):
                determinationNameUUID = 'DeterminationOfFeature'
                determinationName = 'DeterminationOfFeature'
                label = '"detOfFeature"@en'
                dicName = 'volatility_of_features_dic'
                name = 'Feature'
                rprovName = 'Feature'




                if st.form_submit_button(f"Upload dataset to {st.session_state.fuseki_database}",type='primary'):
                    # insert first RDF into graph
                    data = open('example_upload.ttl').read()
                    headers = {'Content-Type': 'text/turtle;charset=utf-8'}

                    r = requests.put(f"http://localhost:3030{st.session_state.fuseki_database}?default", data,
                                     headers=headers)


                    sparqlupdate = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
                    uuid_determinationFeature = uuid.uuid4()
                    ending_time = getTimestamp()

                    uuid_determinationFeature = determinationActivity(host_upload, determinationName, label,
                                                                    starting_time, ending_time)
                    unique_values_dict = {}

                    for features in df.columns:
                        # save unique_values of feature in dictionary
                        unique_values = sorted(df[f'{features}'].unique().tolist())

                        unique_values_dict[features] = unique_values

                        uuid_Feature = uuid.uuid4()

                        success = upload_features(host_upload,uuid_Feature, features, uuid_determinationFeature)





                    st.session_state['first_unique_values_dict'] = unique_values_dict
                    switch_page("Data Understanding")





#
#
