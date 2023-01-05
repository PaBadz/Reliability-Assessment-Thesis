from functions.fuseki_connection import *
from functions.functions_Reliability import *
from functions.functions_DataPreparation import *
from streamlit_option_menu import option_menu
from streamlit_tags import st_tags

try:
    host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
    host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
except:
    st.info("Please select a database first")
    st.stop()

getDefault(host)
getAttributes(host)

data_preparation_options = option_menu("Data Preparation Options", ["Binned Features", "Missing Values"],
                                       icons=['collection', 'slash-circle'],
                                       menu_icon="None", default_index=0, orientation="horizontal")

if not any(key.startswith('level_of_measurement_') for key in st.session_state):
    st.session_state["dataframe_feature_names"] = get_feature_names(host)

try:
    st.session_state["level_of_measurement_dic"], st.session_state["DF_feature_scale_name"] = getFeatureScale(host)
    for key, value in st.session_state["level_of_measurement_dic"].items():
        st.session_state[f'level_of_measurement_{key}'] = value
except:
    st.session_state["DF_feature_scale_name"] = pd.DataFrame()
    st.session_state["level_of_measurement_dic"] = dict()

try:
    st.session_state["volatility_of_features_dic"], st.session_state[
        "DF_feature_volatility_name"] = getFeatureVolatility(host)
except:
    st.session_state["volatility_of_features_dic"] = dict()

try:
    st.session_state["unique_values_dict"] = getUniqueValuesSeq(host)
except Exception as e:
    st.error("No Unique Values in database. If this is the first time a new dataset is uploaded please define a scale for each feature and upload the unique values.")




if data_preparation_options == "Binned Features":
    st.markdown("""## Binning of cardinal features""")
    for key, values in st.session_state.level_of_measurement_dic.items():
        data_restrictions_dic = dict()
        data = list()
        if values == 'Cardinal':
            keywords = st_tags(
                label=f'Enter Keywords: {key}',
                text='Press enter to add more',
                key=f'binnedValues_{key}')

            st.markdown("""---""")
        else:
            pass
    st.write(st.session_state.binnedValues_balance)




    lower_border = st.number_input("Select lower border")

    upper_border = st.number_input("Select upper border")
    bins = st.number_input("Select amount of bins", min_value=int(2))
    binwidth = (upper_border-lower_border)/bins

    st.write(binwidth)




elif data_preparation_options == "Missing Values":

    determinationNameUUID = 'DocuOfHandlingOfMissingValues'
    determinationName = 'DocuOfHandlingOfMissingValues'
    label = 'detMissingValues@en'

    ending_time = getTimestamp()

    starting_time = getTimestamp()



    st.markdown("""## How were missing data replaced?""")
    st.info("If missing values of feature were replaced, insert how it was done. If not, leave empty.")
    tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])
    # create a dictionary with features which have missing values
    for key, values in st.session_state.level_of_measurement_dic.items():
        if 'missingValues_of_features_dic' not in st.session_state:
            st.session_state["missingValues_of_features_dic"] = dict()

        if key in st.session_state["missingValues_of_features_dic"]:
            st.session_state[f'missingValues_{key}'] = \
                st.session_state["missingValues_of_features_dic"][key]
        else:
            st.session_state[f'missingValues_{key}'] = ""

        if values == 'Cardinal':
            with tab1:
                with st.expander(f"Missing Values of {key}"):
                    st.session_state[f'missingValues_{key}'] = st.text_input("How were missing values replaced?", value=st.session_state[f'missingValues_{key}'],on_change=update_missing_values,key=(f'missingValues_{key}_widget'), args=(key,))
        elif values == 'Ordinal':
            with tab2:
                with st.expander(f"Missing Values of {key}"):
                    st.session_state[f'missingValues_{key}'] = st.text_input("How were missing values replaced?", value=st.session_state[f'missingValues_{key}'],on_change=update_missing_values,key=(f'missingValues_{key}_widget'),args=(key,))
        elif values == 'Nominal':
            with tab3:
                with st.expander(f"Missing Values of {key}"):
                    st.session_state[f'missingValues_{key}'] = st.text_input("How were missing values replaced?", value=st.session_state[f'missingValues_{key}'],on_change=update_missing_values,key=(f'missingValues_{key}_widget'),args=(key,))
    if st.button("Submit", type="primary"):
        uuid_DocuOfHandlingOfMissingValues = determinationDUA(host_upload, determinationName,
                                                             label,
                                                             starting_time, ending_time)

        name = "HandlingOfMissingValues"

        uploadDPE(host_upload, host, st.session_state["missingValues_of_features_dic"],
                  uuid_DocuOfHandlingOfMissingValues, name)
    st.write(st.session_state.missingValues_of_features_dic)