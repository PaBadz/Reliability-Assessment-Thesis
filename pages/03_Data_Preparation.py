import streamlit as st
from SPARQLWrapper import SPARQLWrapper
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
import streamlit_nested_layout

from functions.functions_Reliability import getDefault
from functions.fuseki_connection import login, getAttributes, getTimestamp, uploadBinValues, determinationActivity, \
    deleteWasGeneratedByDPA, uploadMissingValues, getAttributesDataPreparation

login()
try:
    if st.session_state.username == "user":
        page = st.button("Deployment")
        if page:
            switch_page("Deployment")
        st.stop()
except:
    st.warning("Please Login")
    st.stop()

try:
    host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
    host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
except:
    st.info("Please select a database first")
    st.stop()


try:
    getDefault(host)

except:
    st.error("Please select other dataset or refresh page")
    st.stop()
try:
    getAttributesDataPreparation(host)
except:
    st.error("Please select other dataset or refresh page")
    st.stop()

if "data_restriction_final" not in st.session_state:
    st.session_state.data_restriction_final = st.session_state.unique_values_dict


if st.session_state.dataframe_feature_names.empty:
    st.stop()

data_preparation_options = option_menu("Data Preparation Options", ["Binned Features", "Missing Values"],
                                       icons=['collection', 'slash-circle'],
                                       menu_icon="None", default_index=0, orientation="horizontal")


if data_preparation_options == "Binned Features":
    if "Cardinal" not in set(st.session_state.DF_feature_scale_name["scale.value"].to_list()):
        st.info("No Cardinal values determined in this dataset, therefore no binning can be performed")


    st.write("""## Binning of cardinal features""")
    st.write("""Only Binning by distance is implemented as of now.\n
             Please insert upper and lower bound and define amount of bins.
             Below you can see the generated bins.""")

    if "bin_dict" not in st.session_state:
        st.session_state.bin_dict = dict()
    if st.session_state["loaded_bin_dict"] == {}:
        for key, values in st.session_state.level_of_measurement_dic.items():
            if values == 'Cardinal':
                if f"bin_{key}" not in st.session_state:
                    st.session_state[f"bin_{key}"] = list()
                with st.expander(f"Bin {key}"):


                    try:
                        lower_border = st.number_input("Select lower border",value =float(st.session_state.data_restriction_final[key][0]), min_value=float(st.session_state.data_restriction_final[key][0]), max_value=float(st.session_state.data_restriction_final[key][-1]), key = f"lower_border_{key}")
                        upper_border = st.number_input("Select upper border",value =float(st.session_state.data_restriction_final[key][-1]),  max_value = float(st.session_state.data_restriction_final[key][-1]),key = f"upper_border_{key}")

                        if st.session_state[f"lower_border_{key}"] >= st.session_state[f"upper_border_{key}"]:
                            st.error("Lower bound range must be smaller than upper bound.")
                        else:
                            bins = st.number_input("Select amount of bins", min_value=int(1), key=f"amount_bin_{key}")
                            step = (upper_border - lower_border) / (bins)

                            if st.button("Save", key=f"bin_{key}_button"):
                                if bins > 1:
                                    st.session_state[f"bin_{key}"] = [
                                        round(lower_border + n * step, 1) for n in
                                        range(bins + 1)]
                                    st.session_state["bin_dict"][key] = st.session_state[f"bin_{key}"]

                                else:
                                    try:
                                        del st.session_state["bin_dict"][key]
                                    except:
                                        pass



                    except:
                        st.error("Lower bound range must be smaller than upper bound.")









        st.write(st.session_state.bin_dict)
        if st.button("Submit bins", key="button_bins"):
            determinationName = 'DocuOfRangeOfBinnedFeature'
            label = '"DocuOfRangeOfBinnedFeature"@en'

            name = 'RangeOfBinnedFeature'
            rprovName = 'RangeOfBinnedFeature'
            ending_time = getTimestamp()

            starting_time = getTimestamp()

            uuid_determinationBin = determinationActivity(host_upload, determinationName, label, starting_time,
                                                              ending_time)
            uploadBinValues(host_upload, host, st.session_state["bin_dict"], uuid_determinationBin, rprovName)
            st.experimental_rerun()
    else:
        # st.write(st.session_state["DF_bin_dict"])
        st.markdown("""
                       **Here you can see how what bins were generatedfor each feature**

                       If you want to change click on the button below.
                       """)
        st.write(st.session_state["loaded_bin_dict"])

        if st.button("Change bins"):
            deleteWasGeneratedByDPA(host_upload, st.session_state["DF_bin_dict"])
            del st.session_state["bin_dict"]
            del st.session_state["DF_bin_dict"]

            st.experimental_rerun()

elif data_preparation_options == "Missing Values":

    determinationNameUUID = 'DocuOfHandlingOfMissingValues'
    determinationName = 'DocuOfHandlingOfMissingValues'
    label = 'detMissingValues@en'

    ending_time = getTimestamp()

    starting_time = getTimestamp()



    st.markdown("""## How were missing data replaced?""")
    st.info("If missing values of feature were replaced, insert how it was done. If not, leave empty.")
    tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])

    if st.session_state.loaded_missingValues_of_features_dic=={}:

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

                        st.session_state[f'missingValues_{key}'] = st.text_input("How were missing values replaced?", value=st.session_state[f'missingValues_{key}'],key=(f'missingValues_{key}_widget'))
                        if st.session_state[f'missingValues_{key}'] != "":
                            st.session_state["missingValues_of_features_dic"][key]=st.session_state[f'missingValues_{key}']
            elif values == 'Ordinal':
                with tab2:
                    with st.expander(f"Missing Values of {key}"):
                        st.session_state[f'missingValues_{key}'] = st.text_input("How were missing values replaced?", value=st.session_state[f'missingValues_{key}'],key=(f'missingValues_{key}_widget'))
                        if st.session_state[f'missingValues_{key}'] != "":
                            st.session_state["missingValues_of_features_dic"][key]=st.session_state[f'missingValues_{key}']
            elif values == 'Nominal':
                with tab3:
                    with st.expander(f"Missing Values of {key}"):
                        st.session_state[f'missingValues_{key}'] = st.text_input("How were missing values replaced?", value=st.session_state[f'missingValues_{key}'],key=(f'missingValues_{key}_widget'))
                        if st.session_state[f'missingValues_{key}'] != "":
                            st.session_state["missingValues_of_features_dic"][key]=st.session_state[f'missingValues_{key}']
        st.write(st.session_state["missingValues_of_features_dic"])
        if st.button("Submit", type="primary"):
            uuid_DocuOfHandlingOfMissingValues = determinationActivity(host_upload, determinationName,
                                                                 label,
                                                                 starting_time, ending_time)

            name = "HandlingOfMissingValues"

            uploadMissingValues(host_upload, host, st.session_state["missingValues_of_features_dic"],
                      uuid_DocuOfHandlingOfMissingValues, name)
            st.session_state.loaded_missingValues_of_features_dic = st.session_state["missingValues_of_features_dic"]
            st.experimental_rerun()
    else:
        st.markdown("""
                **Here you can see how missing values were replaced for each feature**

                If you want to change click on the button below.
                """)
        st.write(st.session_state["loaded_missingValues_of_features_dic"])

        if st.button("Change missing values"):



            deleteWasGeneratedByDPA(host_upload,st.session_state["DF_feature_missing_values_dic"])
            del st.session_state["loaded_missingValues_of_features_dic"]
            del st.session_state["DF_feature_missing_values_dic"]

            st.experimental_rerun()
