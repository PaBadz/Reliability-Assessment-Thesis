from functions.fuseki_connection import *
from streamlit_option_menu import option_menu
from streamlit_tags import st_tags

try:
    host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
    host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
except:
    st.info("Please select a database first")
    st.stop()



selected2 = option_menu("Data Preparation Options", ["Binned Features", "Regression Function", "Missing Values"],
                        icons=['collection', 'arrow-down-up', 'slash-circle'],
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
    st.session_state["unique_values_dict"], st.session_state["DF_uniqueValues"] = getUniqueValues(host)
    for key, value in st.session_state["unique_values_dict"].items():
        res = value.split(', ')
        st.session_state["unique_values_dict"][key] = res
except Exception as e:
    st.info("No unique values found")
    #st.write(e)
    st.stop()




if selected2 == "Binned Features":
    st.markdown("""## Binning of cardinal features""")
    st.write(st.session_state.level_of_measurement_dic)


    for key, values in st.session_state.level_of_measurement_dic.items():
        data_restrictions_dic = dict()
        data = list()
        if values == 'Cardinal':
            keywords = st_tags(
                label=f'Enter Keywords: {key}',
                text='Press enter to add more',
                key=f'BinnedValues_{key}')

            st.markdown("""---""")
            st.write(st.session_state.BinnedValues_age)
        else:
            pass

    lower_border = st.number_input("Select lower border")

    upper_border = st.number_input("Select upper border")
    bins = st.number_input("Select amount of bins", min_value=int(2))
    binwidth = (upper_border-lower_border)/bins

    st.write(binwidth)







elif selected2 == "Regression Function":
    st.markdown("""## Option for Missing Values?""")


elif selected2 == "Missing Values":
    st.markdown("""## How were missing data replaced?""")

