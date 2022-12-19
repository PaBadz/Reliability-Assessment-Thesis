from functions.fuseki_connection import *
from functions.functions import *
from datetime import datetime
from streamlit_option_menu import option_menu
# from streamlit_server_state import server_state, server_state_lock
import pandas as pd


def _set_database():
    for key in st.session_state.keys():
        if key == "fuseki_database" or key == "name_fuseki_database" or key == "fueski_dataset_options":
            pass
        else:
            del st.session_state[key]

    st.session_state.fuseki_database = st.session_state.name_fuseki_database



st.set_page_config(
    page_title="Masterthesis Pascal Badzura",
    page_icon="🦈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.streamlit.io/en/stable/getting_started.html',
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.title('Masterthesis Reliability of Predictions')
try:
    st.write(st.session_state)
except:
    st.write("No session state yet")
selected2 = option_menu(None, ["Database", "Upload"],
                        icons=['database', 'cloud-upload'],
                        menu_icon="", default_index=0, orientation="horizontal")
st.markdown("#### In Order to continue please upload a dataset to the server or choose a dataset from the database")
if st.button('Load all datasets from Fuseki', type='primary'):


    # Get all datasets from fuseki
    sparql = SPARQLWrapper(host)
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


st.session_state.fuseki_database = st.selectbox('Please insert a name for the database', index=index,options=st.session_state['fueski_dataset_options'],on_change=_set_database, key='name_fuseki_database')
host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")




if st.session_state.fuseki_database=="None":
    st.stop()


if selected2 == "Database":


    st.markdown("#### Process of reliability of predictions based on CRISP-DM")
    st.text("""CRISP-DM stands for Cross Industry Standard for Data Mining Processes. In this Web App you will be able to 
            reproduce the process of reliability of predictions based on CRISP-DM. The process is divided into 6 steps.
            - Business Understanding
            - Data Understanding
            - Data Preparation
            - Data Modeling
            - Evaluation
            - Deployment""")


    # if 'dataset_name' not in st.session_state:
    #     st.session_state['dataset_name'] = 'None'
    data = None
    # if 'unique_values_dict' not in st.session_state:
    #     with open('unique_values.json') as f:
    #         st.session_state['unique_values_dict'] = json.load(f)

    st.stop()


def getTimestamp():
    return datetime.now().strftime("%d.%m.%Y - %H:%M:%S")

if selected2 == 'Upload':
    st.info("""The following steps must be carried out when using the device for the first time!
- Select the prediction variable and upload the dataset to the server.
- First time selection of the scale level
- Creating the order of ordinal data and uploading the unique values of the variables
- If a model is to be created, this must also be done when uploading the dataset. Upload of the model can also take place later.""")

    data = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
    if not data:
        st.stop()
    starting_time = getTimestamp()
    for uploaded_file in data:
        if uploaded_file is not None:
            uploaded_file_df = pd.read_csv(uploaded_file)
        st.dataframe(uploaded_file_df)
    if 'dataset' not in st.session_state:
        st.session_state['dataset'] = 'None'

    # Dataset will be split and saved in the database
    # select target variable
    y = st.selectbox('Choose target variable', uploaded_file_df.columns, index=len(uploaded_file_df.columns) - 1)

    X = uploaded_file_df.drop(y, axis=1)

    # Only test prupose. Must be deleted
    X.drop(columns=X.columns[int(0)], axis=1, inplace=True)
    X.drop(columns=X.columns[int(15)], axis=1, inplace=True)
    y = uploaded_file_df[y]
    df = pd.DataFrame(data=X, columns=X.columns)





    if st.session_state.fuseki_database == 'None':
        st.stop()
    host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
    host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")



    X = df
    st.dataframe(df)


    if uploaded_file_df is not None:
        df = pd.DataFrame(data=X, columns=X.columns)
        st.session_state['df'] = df
        st.session_state['X'] = X
        st.session_state['y'] = y
        st.session_state.cardinal_val = {}
        st.session_state.ordinal_val = {}
        st.session_state.nominal_val = {}
        st.session_state.default = {}
        for columns in df.columns:
            st.session_state.default[columns] = []
    else:
        st.write("No Data")
        st.stop()

    # Determination of feature
    if st.button("Upload dataset to the server", type='primary', help="Determines the features of the dataset, in the next step you can determine the scale of the features"):
        determinationNameUUID = 'DeterminationOfOfFeature'
        determinationName = 'DeterminationOfOfFeature'
        label = '"detOfFeature"@en'
        dicName = 'volatility_of_features_dic'
        name = 'Feature'
        rprovName = 'Feature'

        sparqlupdate = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
        uuid_determinationFeature = uuid.uuid4()
        ending_time = getTimestamp()

        uuid_determinationFeature = determinationDUA(host_upload, determinationName, label,
                                                        starting_time, ending_time)
        unique_values_dict = {}

        for features in df.columns:
            # save unique_values of feature in dictionary
            unique_values = sorted(df[f'{features}'].unique().tolist())

            unique_values_dict[features] = unique_values

            uuid_Feature = uuid.uuid4()
            query = (f"""PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                                  PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                                  PREFIX prov:  <http://www.w3.org/ns/prov#>
                                  PREFIX owl: <http://www.w3.org/2002/07/owl#>
                                  PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                                  PREFIX instance:<http://www.semanticweb.org/dke/ontologies#>
                                    INSERT DATA {{<urn:uuid:{uuid_Feature}> rdf:type rprov:Feature, owl:NamedIndividual;
                                    rdfs:label '{features}';
                                    rprov:wasGeneratedByDUA <urn:uuid:{uuid_determinationFeature}>.}}""")
            sparqlupdate.setQuery(query)
            sparqlupdate.setMethod(POST)
            sparqlupdate.query()


        if "unique_values_dict" not in st.session_state:
            st.session_state['unique_values_dict'] = unique_values_dict

            st.success("Features uploaded")
            st.info("In the next step you can determine the scale of the features")

            # create_model = st.button("Determine level of scale for each feature", help(
            #     "It is neccessary to upload unique values to the server. Before this is possible, determination of scale of feature is needed. All Values for Nominal/Ordinal are saved. For Cardinal Features only min/max are saved."),
            #                          type='primary')
            # if create_model:
            #     switch_page("Data Understanding")
