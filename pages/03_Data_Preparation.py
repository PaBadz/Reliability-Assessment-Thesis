from functions.fuseki_connection import *
from streamlit_option_menu import option_menu
from streamlit_tags import st_tags

try:
    host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
    host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
except:
    st.info("Please select a database first")
    st.stop()



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
    st.markdown("""## How were missing data replaced?""")

