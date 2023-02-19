import uuid

import pandas as pd
import regex as re
import streamlit as st
import streamlit_ext as ste
import streamlit_nested_layout
from SPARQLWrapper import SPARQLWrapper
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, ColumnsAutoSizeMode
from streamlit_extras.colored_header import colored_header
from streamlit_option_menu import option_menu
from streamlit_sortables import sort_items

from functions.functions import switch_page
from functions.functions_Reliability import getDefault, getPerturbationOptions, getPerturbationRecommendations, \
    changePerturbationOption, getRestriction, defaultValuesCardinalRestriction, defaultValuesOrdinalRestriction, \
    defaultValuesNominalRestriction, deleteTable
from functions.functions_deployment import get_perturbation_level, color_map
from functions.fuseki_connection import login, getAttributes, getDataRestrictionSeqDeployment, \
    getFeatureVolatilityDeployment, getMissingValuesDeployment, getTimestamp, determinationActivity, \
    uploadPerturbationAssessment, uploadClassificationCase, getAttributesDeployment, getBinValuesSeq, getBinsDeployment, \
    getUniqueValuesSeq
from functions.perturbation_algorithms_ohne_values import percentage_perturbation, sensorPrecision, fixedAmountSteps, \
    perturbRange, perturbInOrder, perturbAllValues
pd.set_option("styler.render.max_elements", 999_999_999_999)

login()

try:
    if st.session_state.username == "user":
        pass
except:
    st.warning("Please Login")
    st.stop()

try:
    host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
    host_upload: SPARQLWrapper = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
    if st.session_state.fuseki_database == "None":
        st.error("Select dataset")
        st.stop()
except:
    st.stop()
# ------------------------------------------------------------------------------------------------------------------------

try:
    getUniqueValuesSeq(host)

except Exception as e:
    st.error("Please upload feature values in Data Understanding step")
    if st.button("Data Understanding"):
        switch_page("Data Understanding")
    st.stop()

try:
    getDefault(host)
except Exception as e:
    st.error("Couldn't load unique values. If already inserted refresh page.")
try:
    getAttributesDeployment(host)
except Exception as e:
    st.error("Please refresh page or change database.")
    st.stop()

# # horizontal menu
menu_perturbation = option_menu(None, ["Perturbation Option", 'Perturbation Mode', "Perturbation"],
                                icons=['house', 'gear'],
                                orientation="horizontal")

try:
    savedPerturbationOptions = getPerturbationOptions(host)
except Exception as e:
    st.write(e)
    st.info("There are no Perturbation Options to select at the moment.")
    st.stop()


if menu_perturbation == 'Perturbation Option':
    hide_table_row_index = """
                                            <style>
                                            thead tr th:first-child {display:none}
                                            tbody th {display:none}
                                            </style>
                                            """
    st.markdown(hide_table_row_index, unsafe_allow_html=True)


    try:
        recommendations = getPerturbationRecommendations(host)
    except:
        st.info("There are no recommendations at the moment.")

    with st.expander("Show all perturbation options"):
        st.dataframe(
            savedPerturbationOptions[["FeatureName", "PerturbationOption", "label"]].reset_index(drop=True),
            use_container_width=True)


    def extract_chars(s):
        return s.split('-')[0]


    savedPerturbationOptions['group'] = savedPerturbationOptions['label'].apply(extract_chars)
    options_group=["None"]
    options_group.extend(savedPerturbationOptions["group"].unique().tolist())
    def deletePO():
        del st.session_state.perturbationOptions

    modelingActivityGroupSelection = st.selectbox("Select group", options=options_group, index =0, on_change=deletePO,help="Here you can select the perturbation options which were defined together, if selected all perturbation options within this group are selected together")
    modelingActivityIDGroup = savedPerturbationOptions.loc[savedPerturbationOptions["group"]==modelingActivityGroupSelection]["ModelingActivity"].unique()



    if "perturbationOptions" not in st.session_state:

        # save the selected options in a dictionary in order to perform the perturbation
        st.session_state.perturbationOptions_settings = {}

        # save all information for the selected perturbation options in a dictionary
        st.session_state.assessmentPerturbationOptions = {}  # pd.DataFrame(columns=savedPerturbationOptions.columns)
        st.session_state.df_test = pd.DataFrame()
        # save default values for each feature
        st.session_state.perturbationOptions = {}
        for columns in st.session_state.dataframe_feature_names["featureName.value"]:
            st.session_state.perturbationOptions[columns] = []
            st.session_state.assessmentPerturbationOptions[columns] = []


    colored_header(
        label="Choose Perturbation Options",
        description="",
        color_name="red-50",
    )
    tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])

    df_test = pd.DataFrame(columns=savedPerturbationOptions.columns)
    # create expander for each feature where the perturbation options can be selected
    for feature_names, level_of_scale in st.session_state.level_of_measurement_dic.items():

        if level_of_scale == "Cardinal":

            with tab1:
                if feature_names not in savedPerturbationOptions["FeatureName"].values:
                    pass
                else:
                    with st.expander(label=f"Algorithms for ***{feature_names}***"):
                        with st.expander("Show all available Perturbation Options"):
                            st.dataframe(
                                savedPerturbationOptions.query('FeatureName == "%s"' % feature_names)[
                                    ["FeatureName", "PerturbationOption", "label", "Settings"]],
                                use_container_width=True)

                        settingList = {}

                        settings = {}


                        with st.expander("Show past perturbation options"):
                            try:
                                if recommendations[recommendations["featureName.value"] == feature_names].empty:
                                    st.info("No recommendations available")
                                    st.markdown(
                                        ":information_source: :green[This means this feature was never perturbed before].")
                                else:
                                    recommendations[recommendations["featureName.value"] == feature_names]
                            except:
                                pass

                        try:
                            try:
                                if len(st.session_state.perturbationOptions[feature_names])==0:
                                    options = (
                                        savedPerturbationOptions.loc[savedPerturbationOptions['FeatureName'] == feature_names][
                                            "label"])
                                elif len(st.session_state.perturbationOptions[feature_names])>0:
                                    same_entity = (
                                        savedPerturbationOptions.loc[(
                                            savedPerturbationOptions['label'] == st.session_state.perturbationOptions[feature_names][0])&(savedPerturbationOptions['FeatureName'] == feature_names)]["DataRestrictionEntities"]).reset_index(drop=True)
                                    options=savedPerturbationOptions.loc[
                                        (savedPerturbationOptions["DataRestrictionEntities"].isin(same_entity)) & (
                                                    savedPerturbationOptions['FeatureName'] == feature_names)]["label"]

                                if modelingActivityGroupSelection != "None":
                                    try:
                                        st.session_state.perturbationOptions[feature_names] =(
                                            savedPerturbationOptions.loc[(
                                             savedPerturbationOptions['ModelingActivity'] ==modelingActivityIDGroup[0]) & (
                                             savedPerturbationOptions['FeatureName'] == feature_names)][
                                            "label"]).reset_index(drop=True)

                                        same_entity = (
                                            savedPerturbationOptions.loc[(
                                                                                 savedPerturbationOptions['label'] ==
                                                                                 st.session_state.perturbationOptions[
                                                                                     feature_names][0]) & (
                                                                                     savedPerturbationOptions[
                                                                                         'FeatureName'] == feature_names)][
                                                "DataRestrictionEntities"]).reset_index(drop=True)
                                        options = savedPerturbationOptions.loc[
                                            (savedPerturbationOptions["DataRestrictionEntities"].isin(same_entity)) & (
                                                    savedPerturbationOptions['FeatureName'] == feature_names)]["label"]
                                    except:
                                        options = (
                                            savedPerturbationOptions.loc[
                                                savedPerturbationOptions['FeatureName'] == feature_names][
                                                "label"])
                                else:
                                    pass
                            except:
                                options = (
                                    savedPerturbationOptions.loc[
                                        savedPerturbationOptions['FeatureName'] == feature_names][
                                        "label"])



                            st.session_state.perturbationOptions[feature_names] = st.multiselect(f'{feature_names}',
                                                                                                 options=options,
                                                                                                 default=
                                                                                                 st.session_state.perturbationOptions[
                                                                                                     feature_names],

                                                                                                 key=f"perturbationOption_{feature_names}",
                                                                                                 on_change=changePerturbationOption,
                                                                                                 args=(
                                                                                                     feature_names,), help="Select Perturbation Options for this Feature. If more than one Perturbation Option is selected the Perturbation Level of the first Perturbation Option is used "
                                                                                                 )


                            chosen_perturbationOptions_feature = (
                                savedPerturbationOptions.loc[(savedPerturbationOptions['label'].isin(
                                    st.session_state.perturbationOptions[feature_names])) & (savedPerturbationOptions[
                                                                                                 'FeatureName'] == feature_names)])

                            df_test = pd.concat([df_test, chosen_perturbationOptions_feature])


                            if not chosen_perturbationOptions_feature.empty:
                                st.session_state.assessmentPerturbationOptions[
                                feature_names] = chosen_perturbationOptions_feature.to_dict("list")
                            else:
                                st.session_state.assessmentPerturbationOptions[
                                    feature_names] = []


                            for index, row in chosen_perturbationOptions_feature.iterrows():
                                keys = re.findall("'(.*?)'", row["Settings"])
                                values = re.findall(': (.*?)(?:,|})', row["Settings"])

                                # create nested dictionary with column name as key and keys as second key and values as values
                                settings = (dict(zip(keys, values)))
                                # convert values to float except if the key is step
                                for key, value in settings.items():
                                    if key == "steps":
                                        settings[key] = int(value)
                                    elif key == "PerturbationLevel":
                                        index = keys.index(key)
                                    else:
                                        settings[key] = float(value)

                                settings["PerturbationLevel"] = keys[index + 1]

                                if row["PerturbationOption"] in settingList:
                                    settingList[row["PerturbationOption"]].append(settings)
                                else:
                                    settingList[row["PerturbationOption"]] = settings





                            st.session_state.perturbationOptions_settings[feature_names] = (settingList)
                            if len(st.session_state.perturbationOptions_settings[feature_names]) > 1:
                                st.info("If Perturbation Options differ in Perturbation Level, first one is used for visualization purposes.")

                            if feature_names in st.session_state.assessmentPerturbationOptions.keys() and \
                                    st.session_state.perturbationOptions[feature_names] != []:
                                st.table(chosen_perturbationOptions_feature[
                                             ["FeatureName", "PerturbationOption", "Settings", "label"]])
                                for i_perturbationOptions in range(0, len(
                                        st.session_state.perturbationOptions[feature_names])):
                                    with st.expander(f"Settings for Perturbation Option {i_perturbationOptions+1}"):



                                        data_understanding_entity = \
                                            st.session_state.assessmentPerturbationOptions[feature_names][
                                                "PerturbationOptionID"][i_perturbationOptions]

                                        featureID = st.session_state.assessmentPerturbationOptions[feature_names]["FeatureID"][
                                            0]
                                        data_restriction_entity = getDataRestrictionSeqDeployment(data_understanding_entity,
                                                                                                  featureID, host)

                                        if data_restriction_entity:
                                            st.success(f"Data Restriction for this feature:  {data_restriction_entity[feature_names]}")
                                        else:
                                            st.info("No Data Restriction selected for this perturbation option")


                                        volatility_entity = getFeatureVolatilityDeployment(data_understanding_entity,
                                                                                           featureID, host)

                                        try:
                                            if volatility_entity["volatilityLevel.value"][0] == 'High Volatility':
                                                st.error("Feature has high volatility!")

                                            elif volatility_entity["volatilityLevel.value"][0] == 'Medium Volatility':
                                                st.warning(
                                                    "Feature has medium volatility!")
                                            elif volatility_entity["volatilityLevel.value"][0] == 'Low Volatility':
                                                st.info("Feature has medium volatility!")




                                        except Exception as e:
                                            st.info(f"Perturbation Option {i_perturbationOptions + 1} has no level of volatility saved")

                                        missing_values_entity = getMissingValuesDeployment(data_understanding_entity,
                                                                                           featureID, host)

                                        try:
                                            st.success(f"Missing values were replaced with: {missing_values_entity['MissingValues.value'][0]}")



                                        except Exception as e:
                                            st.info(f"Perturbation Option {i_perturbationOptions + 1} has no replacement for missing values determined")



                                        if st.session_state.assessmentPerturbationOptions[feature_names]["PerturbationOption"][i_perturbationOptions] == "Bin perturbation":
                                            st.success(f"Bins determined for this Perturbation Option:")
                                            bin_values_entity = getBinsDeployment(data_understanding_entity,featureID, host)
                                            bin_values_entity_list = bin_values_entity["item.value"].tolist()

                                            st.write([[bin_values_entity_list[i],
                                                       bin_values_entity_list[i + 1]] for i in
                                                      range(len(bin_values_entity_list) - 1)])

                            # TODO connect to
                        except Exception as e:
                            st.write(e)
                            st.info('No Cardinal Values', icon="ℹ️")

        if level_of_scale == "Ordinal":
            with tab2:
                if feature_names not in savedPerturbationOptions["FeatureName"].values:
                    pass
                else:
                    with st.expander(label=f"Algorithms for ***{feature_names}***"):
                        settingList = {}

                        settings = {}

                        with st.expander("Show past perturbation options"):
                            try:
                                if recommendations[recommendations["featureName.value"] == feature_names].empty:
                                    st.info("No recommendations available")
                                    st.markdown(
                                        ":information_source: :green[This means this feature was never perturbed before].")
                                else:
                                    recommendations[recommendations["featureName.value"] == feature_names]
                            except:
                                pass

                        try:
                            try:
                                if len(st.session_state.perturbationOptions[feature_names]) == 0:
                                    options = (
                                        savedPerturbationOptions.loc[
                                            savedPerturbationOptions['FeatureName'] == feature_names][
                                            "label"])
                                elif len(st.session_state.perturbationOptions[feature_names]) > 0:
                                    same_entity = (
                                        savedPerturbationOptions.loc[(
                                                                             savedPerturbationOptions['label'] ==
                                                                             st.session_state.perturbationOptions[
                                                                                 feature_names][0]) & (
                                                                                 savedPerturbationOptions[
                                                                                     'FeatureName'] == feature_names)][
                                            "DataRestrictionEntities"]).reset_index(drop=True)
                                    options = savedPerturbationOptions.loc[
                                        (savedPerturbationOptions["DataRestrictionEntities"].isin(same_entity)) & (
                                                savedPerturbationOptions['FeatureName'] == feature_names)]["label"]

                                if modelingActivityGroupSelection != "None":
                                    try:
                                        st.session_state.perturbationOptions[feature_names] = (
                                            savedPerturbationOptions.loc[(
                                                                                 savedPerturbationOptions[
                                                                                     'ModelingActivity'] ==
                                                                                 modelingActivityIDGroup[0]) & (
                                                                                 savedPerturbationOptions[
                                                                                     'FeatureName'] == feature_names)][
                                                "label"]).reset_index(drop=True)

                                        same_entity = (
                                            savedPerturbationOptions.loc[(
                                                                                 savedPerturbationOptions['label'] ==
                                                                                 st.session_state.perturbationOptions[
                                                                                     feature_names][0]) & (
                                                                                 savedPerturbationOptions[
                                                                                     'FeatureName'] == feature_names)][
                                                "DataRestrictionEntities"]).reset_index(drop=True)
                                        options = savedPerturbationOptions.loc[
                                            (savedPerturbationOptions["DataRestrictionEntities"].isin(same_entity)) & (
                                                    savedPerturbationOptions['FeatureName'] == feature_names)]["label"]
                                    except:
                                        options = (
                                            savedPerturbationOptions.loc[
                                                savedPerturbationOptions['FeatureName'] == feature_names][
                                                "label"])
                                else:
                                    pass
                            except:
                                options = (
                                    savedPerturbationOptions.loc[
                                        savedPerturbationOptions['FeatureName'] == feature_names][
                                        "label"])


                            st.session_state.perturbationOptions[feature_names] = st.multiselect(f'{feature_names}',
                                                                                                 options=options,
                                                                                                 default=
                                                                                                 st.session_state.perturbationOptions[
                                                                                                     feature_names],

                                                                                                 key=f"perturbationOption_{feature_names}",
                                                                                                 on_change=changePerturbationOption,
                                                                                                 args=(
                                                                                                     feature_names,)
                                                                                                 )



                            chosen_perturbationOptions_feature = (
                                savedPerturbationOptions.loc[(savedPerturbationOptions['label'].isin(
                                    st.session_state.perturbationOptions[feature_names])) & (savedPerturbationOptions[
                                                                                                 'FeatureName'] == feature_names)])
                            # st.write(chosen_perturbationOptions_feature)
                            df_test = pd.concat([df_test, chosen_perturbationOptions_feature])


                            # st.session_state.assessmentPerturbationOptions[feature_names] = chosen_perturbationOptions_feature()
                            st.session_state.assessmentPerturbationOptions[
                                feature_names] = chosen_perturbationOptions_feature.to_dict("list")
                            # st.write(st.session_state.assessmentPerturbationOptions[feature_names])

                            #
                            # st.session_state.perturbationOptions[feature_names] = st.selectbox(f'{feature_names}',
                            #                                                                      options=options,
                            #                                                                      # default=
                            #                                                                      # st.session_state.perturbationOptions[
                            #                                                                      #     feature_names],
                            #                                                                      key=f"perturbationOption_{feature_names}",
                            #                                                                      on_change=changePerturbationOption,
                            #                                                                      args=(feature_names,))

                            for index, row in chosen_perturbationOptions_feature.iterrows():
                                # st.write(index)

                                keys = re.findall("'(.*?)'", row["Settings"])
                                values = re.findall(': (.*?)(?:,|})', row["Settings"])

                                # create nested dictionary with column name as key and keys as second key and values as values
                                settings = (dict(zip(keys, values)))

                                # convert values to float except if the key is step
                                for key, value in settings.items():
                                    if key == "steps":
                                        settings[key] = int(value)
                                    elif key == "PerturbationLevel":
                                        index = keys.index(key)

                                settings["PerturbationLevel"] = keys[index + 1]

                                if row["PerturbationOption"] in settingList:
                                    settingList[row["PerturbationOption"]].append(settings)
                                else:
                                    settingList[row["PerturbationOption"]] = settings

                            st.session_state.perturbationOptions_settings[feature_names] = (settingList)
                            if len(st.session_state.perturbationOptions_settings[feature_names]) > 1:
                                st.info(
                                    "If Perturbation Options differ in Perturbation Level, first one is used for visualization purposes.")

                            if feature_names in st.session_state.assessmentPerturbationOptions.keys() and \
                                    st.session_state.perturbationOptions[feature_names] != []:
                                st.table(chosen_perturbationOptions_feature[
                                             ["FeatureName", "PerturbationOption", "Settings", "label"]])
                                for i_perturbationOptions in range(0, len(
                                        st.session_state.perturbationOptions[feature_names])):
                                    with st.expander(f"Settings for Perturbation Option {i_perturbationOptions + 1}"):

                                        data_understanding_entity = \
                                            st.session_state.assessmentPerturbationOptions[feature_names][
                                                "PerturbationOptionID"][i_perturbationOptions]

                                        featureID = \
                                        st.session_state.assessmentPerturbationOptions[feature_names]["FeatureID"][
                                            0]
                                        data_restriction_entity = getDataRestrictionSeqDeployment(
                                            data_understanding_entity,
                                            featureID, host)

                                        if data_restriction_entity:
                                            st.success(
                                                f"Data Restriction for this feature:  {data_restriction_entity[feature_names]}")
                                        else:
                                            st.info("No Data Restriction selected for this perturbation option")

                                        volatility_entity = getFeatureVolatilityDeployment(data_understanding_entity,
                                                                                           featureID, host)

                                        try:
                                            if volatility_entity["volatilityLevel.value"][0] == 'High Volatility':
                                                st.error("Feature has high volatility!")

                                            elif volatility_entity["volatilityLevel.value"][0] == 'Medium Volatility':
                                                st.warning(
                                                    "Feature has medium volatility!")
                                            elif volatility_entity["volatilityLevel.value"][0] == 'Low Volatility':
                                                st.info("Feature has medium volatility!")




                                        except Exception as e:
                                            st.info(
                                                f"Perturbation Option {i_perturbationOptions + 1} has no level of volatility saved")

                                        missing_values_entity = getMissingValuesDeployment(data_understanding_entity,
                                                                                           featureID, host)

                                        try:
                                            st.success(
                                                f"Missing values were replaced with: {missing_values_entity['MissingValues.value'][0]}")



                                        except Exception as e:
                                            st.info(
                                                f"Perturbation Option {i_perturbationOptions + 1} has no replacement for missing values determined")


                        except Exception as e:
                            st.write(e)
                            st.info('No Ordinal Values', icon="ℹ️")

        if level_of_scale == "Nominal":
            if feature_names not in savedPerturbationOptions["FeatureName"].values:
                pass
            else:

                with tab3:
                    with st.expander(label=f"Algorithms for ***{feature_names}***"):
                        settingList = {}

                        settings = {}
                        with st.expander("Show past perturbation options"):
                            try:
                                if recommendations[recommendations["featureName.value"] == feature_names].empty:
                                    st.info("No recommendations available")
                                    st.markdown(
                                        ":information_source: :green[This means this feature was never perturbed before].")
                                else:
                                    recommendations[recommendations["featureName.value"] == feature_names]
                            except:
                                pass

                        try:
                            try:
                                if len(st.session_state.perturbationOptions[feature_names]) == 0:
                                    options = (
                                        savedPerturbationOptions.loc[
                                            savedPerturbationOptions['FeatureName'] == feature_names][
                                            "label"])
                                elif len(st.session_state.perturbationOptions[feature_names]) > 0:
                                    same_entity = (
                                        savedPerturbationOptions.loc[(
                                                                             savedPerturbationOptions['label'] ==
                                                                             st.session_state.perturbationOptions[
                                                                                 feature_names][0]) & (
                                                                                 savedPerturbationOptions[
                                                                                     'FeatureName'] == feature_names)][
                                            "DataRestrictionEntities"]).reset_index(drop=True)
                                    options = savedPerturbationOptions.loc[
                                        (savedPerturbationOptions["DataRestrictionEntities"].isin(same_entity)) & (
                                                savedPerturbationOptions['FeatureName'] == feature_names)]["label"]

                                if modelingActivityGroupSelection != "None":
                                    try:
                                        st.session_state.perturbationOptions[feature_names] = (
                                            savedPerturbationOptions.loc[(
                                                                                 savedPerturbationOptions[
                                                                                     'ModelingActivity'] ==
                                                                                 modelingActivityIDGroup[0]) & (
                                                                                 savedPerturbationOptions[
                                                                                     'FeatureName'] == feature_names)][
                                                "label"]).reset_index(drop=True)

                                        same_entity = (
                                            savedPerturbationOptions.loc[(
                                                                                 savedPerturbationOptions['label'] ==
                                                                                 st.session_state.perturbationOptions[
                                                                                     feature_names][0]) & (
                                                                                 savedPerturbationOptions[
                                                                                     'FeatureName'] == feature_names)][
                                                "DataRestrictionEntities"]).reset_index(drop=True)
                                        options = savedPerturbationOptions.loc[
                                            (savedPerturbationOptions["DataRestrictionEntities"].isin(same_entity)) & (
                                                    savedPerturbationOptions['FeatureName'] == feature_names)]["label"]
                                    except:
                                        options = (
                                            savedPerturbationOptions.loc[
                                                savedPerturbationOptions['FeatureName'] == feature_names][
                                                "label"])
                                else:
                                    pass
                            except:
                                options = (
                                    savedPerturbationOptions.loc[
                                        savedPerturbationOptions['FeatureName'] == feature_names][
                                        "label"])

                            st.session_state.perturbationOptions[feature_names] = st.multiselect(f'{feature_names}',
                                                                                                 options=options,
                                                                                                 default=
                                                                                                 st.session_state.perturbationOptions[
                                                                                                     feature_names],

                                                                                                 key=f"perturbationOption_{feature_names}",
                                                                                                 on_change=changePerturbationOption,
                                                                                                 args=(
                                                                                                     feature_names,)
                                                                                                 )
                            chosen_perturbationOptions_feature = (
                            savedPerturbationOptions.loc[(savedPerturbationOptions['label'].isin(
                                st.session_state.perturbationOptions[feature_names])) & (
                                                                 savedPerturbationOptions[
                                                                     'FeatureName'] == feature_names)])

                            df_test = pd.concat([df_test, chosen_perturbationOptions_feature])

                            st.session_state.assessmentPerturbationOptions[
                                feature_names] = chosen_perturbationOptions_feature.to_dict("list")


                            for index, row in chosen_perturbationOptions_feature.iterrows():

                                keys = re.findall("'(.*?)'", row["Settings"])
                                values = re.findall(': \[(.*?)\]', row["Settings"])

                                keys = re.findall("'(.*?)'", row["Settings"])
                                values = re.findall(': (.*?)(?:,|})', row["Settings"])

                                # create nested dictionary with column name as key and keys as second key and values as values
                                settings_ = (dict(zip(keys, values)))

                                # convert values to float except if the key is step
                                for key, value in settings_.items():
                                    if key == "steps":
                                        settings[key] = int(value)
                                    elif key == "PerturbationLevel":
                                        index = keys.index(key)

                                settings["PerturbationLevel"] = keys[index + 1]
                                if row["PerturbationOption"] in settingList:
                                    settingList[row["PerturbationOption"]].append(settings)

                                else:
                                    settingList[row["PerturbationOption"]] = settings


                            st.session_state.perturbationOptions_settings[feature_names] = (settingList)
                            if len(st.session_state.perturbationOptions_settings[feature_names]) > 1:
                                st.info("If Perturbation Options differ in Perturbation Level, first one is used for visualization purposes.")


                            if feature_names in st.session_state.assessmentPerturbationOptions.keys() and \
                                    st.session_state.perturbationOptions[feature_names] != []:
                                st.table(chosen_perturbationOptions_feature[
                                             ["FeatureName", "PerturbationOption", "Settings", "label"]])
                                for i_perturbationOptions in range(0, len(
                                        st.session_state.perturbationOptions[feature_names])):
                                    with st.expander(f"Settings for Perturbation Option {i_perturbationOptions + 1}"):

                                        data_understanding_entity = \
                                            st.session_state.assessmentPerturbationOptions[feature_names][
                                                "PerturbationOptionID"][i_perturbationOptions]

                                        featureID = \
                                        st.session_state.assessmentPerturbationOptions[feature_names]["FeatureID"][
                                            0]
                                        data_restriction_entity = getDataRestrictionSeqDeployment(
                                            data_understanding_entity,
                                            featureID, host)

                                        if data_restriction_entity:
                                            st.success(
                                                f"Data Restriction for this feature:  {data_restriction_entity[feature_names]}")
                                        else:
                                            st.info("No Data Restriction selected for this perturbation option")

                                        volatility_entity = getFeatureVolatilityDeployment(data_understanding_entity,
                                                                                           featureID, host)

                                        try:
                                            if volatility_entity["volatilityLevel.value"][0] == 'High Volatility':
                                                st.error("Feature has high volatility!")

                                            elif volatility_entity["volatilityLevel.value"][0] == 'Medium Volatility':
                                                st.warning(
                                                    "Feature has medium volatility!")
                                            elif volatility_entity["volatilityLevel.value"][0] == 'Low Volatility':
                                                st.info("Feature has medium volatility!")




                                        except Exception as e:
                                            st.info(
                                                f"Perturbation Option {i_perturbationOptions + 1} has no level of volatility saved")

                                        missing_values_entity = getMissingValuesDeployment(data_understanding_entity,
                                                                                           featureID, host)

                                        try:
                                            st.success(
                                                f"Missing values were replaced with: {missing_values_entity['MissingValues.value'][0]}")



                                        except Exception as e:
                                            st.info(
                                                f"Perturbation Option {i_perturbationOptions + 1} has no replacement for missing values determined")




                        except Exception as e:
                            st.error(e)
                            st.info('No Nominal Values', icon="ℹ️")

    try:
        savedRestrictions = getRestriction(host)


        # data_restriction = st.selectbox("Select Data Restriction", options=savedRestrictions["DataRestrictionActivity"].unique())
        st.session_state["data_restriction_final_deployment"] = st.session_state.unique_values_dict.copy()


        for feature_name, level_of_scale in st.session_state["level_of_measurement_dic"].items():
            # gets unique values for each feature and updates if data restriction is applicable
            if level_of_scale == "Cardinal":
                defaultValuesCardinalRestriction(feature_name)
            if level_of_scale == "Ordinal":
                defaultValuesOrdinalRestriction(feature_name)
            if level_of_scale == "Nominal":
                defaultValuesNominalRestriction(feature_name)

        # look in assessmentPerturbationOptions if there are data restrictions for the feature and if so, update the data_restriction_dict


        for feature_name in st.session_state.assessmentPerturbationOptions.keys():
            try:
                data_restriction_entity = \
                st.session_state.assessmentPerturbationOptions[feature_name]["PerturbationOptionID"][0]

                featureID = st.session_state.assessmentPerturbationOptions[feature_name]["FeatureID"][0]

                st.session_state["data_restriction_deployment"] = getDataRestrictionSeqDeployment(data_restriction_entity,
                                                                                             featureID, host)
            except Exception as e:
                pass

            try:
                st.session_state.data_restriction_final_deployment.update(st.session_state.data_restriction_deployment)
            except Exception as e:
                pass





    except Exception as e:
        st.write(e)
        st.session_state["data_restriction_final_deployment"] = st.session_state.unique_values_dict.copy()


    colored_header(
        label="Show Algorithms",
        description="Define level of scale for each feature",
        color_name="red-50",
    )
    with st.expander("Show chosen Perturbation Options"):
        # delete empty dictionaries
        st.write(df_test)
        st.session_state.df_test = df_test
        try:

            for key in list(st.session_state.assessmentPerturbationOptions.keys()):

                if not st.session_state.assessmentPerturbationOptions[key]:
                    del st.session_state.assessmentPerturbationOptions[key]

            for feature in list(st.session_state.perturbationOptions_settings.keys()):

                if not st.session_state.perturbationOptions_settings[feature]:

                    del st.session_state.perturbationOptions_settings[feature]
        except Exception as e:
            st.error(e)

        # st.session_state.assessmentPerturbationOptions
        # st.write(st.session_state.perturbationOptions_settings)


    with st.expander("Show Data Restriction values"):

        st.write("Data Restriction", st.session_state.data_restriction_final_deployment)


    # Define Algorithmns

if menu_perturbation == 'Perturbation Mode':
    st.write("Choose perturbation Mode")
    st.write("It does not make sense, that the user is able to select the data restriction, only for the development"
             "in the development view it is neccessary to connect the chosen data restriction with the perturbation option and not any")
    st.info("If you want to change the order of perturbation execution drag an drop accordingly")

    options = ['Full', 'Prioritized', 'Selected']

    feature_names = st.session_state["dataframe_feature_names"]["featureName.value"].values.tolist()

    if "pertubation_mode" not in st.session_state:
        st.session_state.pertubation_mode = "Full"


    def change(value):
        st.session_state.pertubation_mode = value


    pertubation_mode = st.radio(
        "Which Perturbation Mode",
        ('Full', 'Prioritized', 'Selected'), index=options.index(st.session_state.pertubation_mode), on_change=change,
        args=(st.session_state.pertubation_mode,))
    if pertubation_mode == "Full":
        st.session_state.perturb_mode_values = feature_names

        st.session_state.pertubation_mode = "Full"

    if pertubation_mode == "Prioritized":
        st.session_state.pertubation_mode = "Prioritized"

        st.session_state.perturb_mode_values = sort_items(st.session_state.df_test["FeatureName"].tolist())

    if pertubation_mode == "Selected":
        st.session_state.perturb_mode_values = "Selected Perturbation Mode"

        st.info("Perturbation Mode might not work properly")
        st.error("maybe worthless, selected mode can be achieved otherwise")
        selected = st.multiselect("Select features which should be perturbed",
                                  options=st.session_state["dataframe_feature_names"]["featureName.value"],
                                  default=st.session_state.df_test["FeatureName"].tolist())
        st.session_state.perturb_mode_values = selected

        try:
            for feature in st.session_state.perturb_mode_values:
                st.session_state.pertubation_mode = "Selected"

        except Exception as e:
            st.error("Select only perturbation options for features selected")
            st.info("Perturb mode is set to Full")
            st.session_state.pertubation_mode = "Full"
            st.session_state.perturb_mode_values = feature_names
try:
    if menu_perturbation == 'Perturbation':
        if "perturb_mode_values" not in st.session_state:
            st.session_state.perturb_mode_values =st.session_state["dataframe_feature_names"][
                "featureName.value"].values.tolist()

        perturbed_value_list = dict()

        if "perturbed_value_list" not in st.session_state:
            st.session_state.perturbed_value_list = {}
            for columns in st.session_state.dataframe_feature_names["featureName.value"]:
                st.session_state.perturbed_value_list[columns] = []

        insert, delete = st.tabs(["Insert", "Delete"])

        with insert:

            if "df_aggrid_beginning" not in st.session_state:
                st.session_state.df_aggrid_beginning = pd.DataFrame(
                    columns=st.session_state.dataframe_feature_names["featureName.value"].tolist())



            with st.expander("Submit new Data", expanded=False):
                with st.form("Add Data"):
                    dic = dict()
                    col_cardinal, col_ordinal, col_nominal = st.columns(3, gap="medium")

                    for feature_name, level_of_scale in st.session_state.level_of_measurement_dic.items():
                        if level_of_scale == "Cardinal":
                            with col_cardinal:
                                dic[feature_name] = st.number_input(f"Select Value for {feature_name}",
                                                                    min_value=float(
                                                                        st.session_state.data_restriction_final_deployment[
                                                                            feature_name][0]),
                                                                    max_value=float(
                                                                        st.session_state.data_restriction_final_deployment[
                                                                            feature_name][-1]),
                                                                    key=f"add_data_{feature_name}")

                        if level_of_scale == "Ordinal":
                            with col_ordinal:
                                dic[feature_name] = st.selectbox(f"Select Value for {feature_name}",
                                                                 options=st.session_state.data_restriction_final_deployment[
                                                                     feature_name],
                                                                 key=f"add_data_{feature_name}")
                        if level_of_scale == "Nominal":
                            with col_nominal:
                                dic[feature_name] = st.selectbox(f"Select Value for {feature_name}",
                                                                 options=st.session_state.data_restriction_final_deployment[
                                                                     feature_name],
                                                                 key=f"add_data_{feature_name}")
                    if st.form_submit_button("Submit Data", type='primary'):
                        st.session_state.df_aggrid_beginning = st.session_state.df_aggrid_beginning.append(dic,
                                                                                                           ignore_index=True)
                        st.experimental_rerun()
                        st.success("Data added")


            with st.expander("Upload new Data"):
                new_cases = st.file_uploader("Upload csv file", type="csv")
                if new_cases is not None:
                    file = pd.read_csv(new_cases)
                    for columns in file:
                        if st.session_state.level_of_measurement_dic[columns]=="Cardinal":
                            file[columns] = file[columns].astype(float)
                        else:
                            file[columns] = file[columns].astype(str)

                    st.session_state.df_aggrid_beginning = file





        with delete:
            if st.session_state.df_aggrid_beginning.shape[0] == 0:
                st.write("No data available")
            else:

                drop_index = int(st.number_input("Row to delete", (st.session_state.df_aggrid_beginning.index[0] + 1),
                                                 (st.session_state.df_aggrid_beginning.index[-1] + 1)))

                try:
                    if st.button(f"Delete row  {drop_index}"):
                        st.session_state.df_aggrid_beginning = st.session_state.df_aggrid_beginning.drop(
                            drop_index - 1).reset_index(drop=True)
                        st.experimental_rerun()
                except Exception as e:
                    st.info(e)
            deleteTable("delete_selected_rows_table")
        colored_header(
            label="Select rows",
            description="Select one or mutliple rows. Each selected row represents a use case and is perturbed.",
            color_name="red-50",
        )
        if st.session_state.df_aggrid_beginning.shape[0] == 0:
            st.info("Insert new data to continue")
            st.stop()
        # configue aggrid table
        gb = GridOptionsBuilder.from_dataframe(st.session_state.df_aggrid_beginning)
        gb.configure_selection(selection_mode="multiple", use_checkbox=False, rowMultiSelectWithClick=True)
        gb.configure_auto_height(autoHeight=True)

        for feature_name, value in st.session_state.data_restriction_final_deployment.items():
            if st.session_state.level_of_measurement_dic[feature_name] != 'Cardinal':
                gb.configure_column(f"{feature_name}", editable=True, cellEditor="agSelectCellEditor",
                                    cellEditorPopup=True, cellEditorParams={"values": value},
                                    singleClickEdit=False,
                                    sortable=True, filter=True, resizable=True)
            else:
                gb.configure_column(f"{feature_name}", type=['numericColumn', "numberColumnFilter"], editable=True,
                                    sortable=True, filter=True, resizable=True)

        gridOptions = gb.build()

        data = AgGrid(st.session_state.df_aggrid_beginning,
                      gridOptions=gridOptions,
                      enable_enterprise_modules=False,
                      allow_unsafe_jscode=True,
                      editable=True,
                      columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                      data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                      update_mode=GridUpdateMode.SELECTION_CHANGED,
                      allowDragFromColumnsToolPanel=False,
                      alwaysShowVerticalScroll=True,
                      alwaysShowHorizontalScroll=True,
                      theme='streamlit')

        # TODO: Create Entity from selected rows, Values: PerturbedTestCase
        # Naming? Labeling?
        # Values Testcase? These are the predicted perturbed rows

        selected_rows = data["selected_rows"]
        selected_rows_DF = pd.DataFrame(selected_rows,
                                        columns=st.session_state.dataframe_feature_names["featureName.value"])
        try:
            for features in selected_rows_DF:
                if st.session_state.level_of_measurement_dic[features] == 'Cardinal':
                    selected_rows_DF[features] = selected_rows_DF[features].astype(float)
        except Exception as e:
            st.error(f"ERROR! Please change! {e}")


        if selected_rows_DF.shape[0] == 0:
            st.info("Select rows to continue")
            st.stop()

        with st.expander("Show selected rows"):
            st.dataframe(selected_rows_DF, use_container_width=True)


        with st.expander("Show Perturbation options"):
            st.write(st.session_state.perturbationOptions_settings)


        label_list = []
        for i in range(0, len(selected_rows)):
            label_case = st.text_input(f"Label for Case {i + 1}",
                                           help="Insert a name for the perturbation Assessment", key=f"label_{i}")

            if label_case !="":
                label_list.append(label_case)

        if len(label_list) != len(selected_rows):
            st.stop()


        checkbox_upload = st.checkbox("Upload Perturbation Options to Fuseki", help="This is for testing purposes")

        if st.button("Predict", type="primary"):

            def uploadPerturbationMode():
                st.session_state.perturb_mode_values = feature_names
                """ACTIVITY
                <http://www.semanticweb.org/dke/ontologies/2021/6/25_7273>
                rdf:type            rprov:DefinitionOfPerturbationMode , owl:NamedIndividual ;
                rdfs:label          "defPertMode"@en ;
                prov:endedAtTime    "0000-00-00T00:00:00Z" ;
                prov:startedAtTime  "0000-00-00T00:00:00Z" .
                """

                """ENTITY
                <http://www.semanticweb.org/dke/ontologies/2021/6/25_7283>
                rdf:type                rprov:PerturbationMode , owl:NamedIndividual ;
                rprov:pertModeValue           "{st.session_state.pertubation_mode}"@en ;
                rprov:pertModeValueSeq  <urn:uuid:{uuid_PerturbationModeSeq}>
                rprov:wasGeneratedByMA  <http://www.semanticweb.org/dke/ontologies/2021/6/25_7273> ;
                prov:generatedAtTime    "0000-00-00T00:00:00Z" .
                """

                '''
                i = 0
                for values in value:
                    query = ((f"""INSERT DATA {{<urn:uuid:{uuid_PerturbationModeSeq}> rdf:type rdf:Seq, owl:NamedIndividual;
                                          rdf:_{i}  '{values}';}}"""))
                    sparqlupdate.setQuery(prefix + query)
                    sparqlupdate.setMethod(POST)
                    sparqlupdate.query()
                    i = i + 1
                '''


            try:
                if "perturbedList" not in st.session_state:
                    st.session_state.perturbedList = dict()

                # TODO OUTSOURCE CODE
                # divide df based on level of measurement
                nominal = [key for key, value in st.session_state.level_of_measurement_dic.items() if
                           value == 'Nominal']
                ordinal = [key for key, value in st.session_state.level_of_measurement_dic.items() if
                           value == 'Ordinal']

                cardinal = [key for key, value in st.session_state.level_of_measurement_dic.items() if
                            value == 'Cardinal']

                ct = ColumnTransformer(transformers=[
                    ("OneHot", OneHotEncoder(handle_unknown='ignore'), nominal),
                    ("Ordinal", OrdinalEncoder(handle_unknown='error'), ordinal),
                    ("Cardinal", SimpleImputer(strategy='most_frequent'), cardinal)],
                    remainder='drop', verbose_feature_names_out=False)

                df = pd.DataFrame.from_dict(st.session_state.unique_values_dict, orient='index')
                df = df.transpose()
                x = pd.concat([df, selected_rows_DF]).reset_index(drop=True)
                x = x.fillna(method='ffill')

                try:
                    x_trans_df = pd.DataFrame(ct.fit_transform(x).toarray(), columns=ct.get_feature_names_out()).reset_index(drop=True)
                except:
                    x_trans_df = pd.DataFrame(ct.fit_transform(x), columns=ct.get_feature_names_out()).reset_index(drop=True)



                y_pred = pd.DataFrame(st.session_state.model.predict(x_trans_df))

                # TODO divide selected rows in order to have seperated dataframes for each row, Idee: Result DF / len(selected_rows_DF)
                # dadurch könnten die Selected rows getrennt werden

                result = selected_rows_DF
                # reset index for y_pred in order to be able to insert it to result
                result["prediction"] = y_pred.iloc[len(df):].reset_index(drop=True)

                # change values in selected rows to list in order to extend the list with perturbated values
                # this is done because we need to explode it later
                for row in selected_rows:
                    for feature, value in row.items():
                        if feature != "_selectedRowNodeInfo":
                            if st.session_state.level_of_measurement_dic[feature] != 'Cardinal':
                                row[feature] = [value]
                            else:
                                row[feature] = [round(float(value),3)]

            except Exception as e:
                st.error(f"ERROR! Please change! {e}")

            try:
                result_df = pd.DataFrame(
                    columns=result.columns)  # st.session_state.dataframe_feature_names["featureName.value"].tolist())
                if "result_df" not in st.session_state:
                    st.session_state['result_df'] = result_df

                index_perturb = list()
                # dictionary mit den ausgewählten methoden für jede column
                for i in range(0, len(selected_rows)):
                    try:
                        for column, method in st.session_state['perturbationOptions_settings'].items():

                            perturbedList = dict()

                            for k, v in selected_rows[i].items():

                                # TODO Hier die Umwandlung der perturbations auslagern
                                # Es muss für jede Methode eine andere möglichkeit geben
                                try:
                                    if k == column:
                                        for algorithm_keys in method.keys():

                                            if algorithm_keys == 'Percentage perturbation':

                                                perturbedList[algorithm_keys] = (
                                                    percentage_perturbation(method[algorithm_keys]["steps"],
                                                                            selected_rows[i][k][0],
                                                                            st.session_state.data_restriction_final_deployment[
                                                                                column]))


                                            elif algorithm_keys == '5% perturbation':
                                                try:
                                                    perturbedList[algorithm_keys] = (
                                                        percentage_perturbation(5, selected_rows[i][k][0],
                                                                                st.session_state.data_restriction_final_deployment[
                                                                                    column]))
                                                except Exception as e:
                                                    st.error(f"ERROR! Please change! {e}")

                                            elif algorithm_keys == '10% perturbation':
                                                perturbedList[algorithm_keys] = (
                                                    percentage_perturbation(10, selected_rows[i][k][0],
                                                                            st.session_state.data_restriction_final_deployment[
                                                                                column]))

                                            elif algorithm_keys == 'Sensor Precision':
                                                perturbedList[algorithm_keys] = (
                                                    sensorPrecision(method[algorithm_keys]["sensorPrecision"],
                                                                    method[algorithm_keys]["steps"],
                                                                    selected_rows[i][k][0],
                                                                    st.session_state.data_restriction_final_deployment[column]))
                                            elif algorithm_keys == 'Fixed amount':
                                                perturbedList[algorithm_keys] = (
                                                    fixedAmountSteps(method[algorithm_keys]["amount"],
                                                                     method[algorithm_keys]["steps"],
                                                                     selected_rows[i][k][0],
                                                                     st.session_state.data_restriction_final_deployment[column]))
                                            elif algorithm_keys == 'Range perturbation':
                                                perturbedList[algorithm_keys] = (
                                                    perturbRange(method[algorithm_keys]["lowerBound"],
                                                                 method[algorithm_keys]["upperBound"],
                                                                 method[algorithm_keys]["steps"]))

                                            elif algorithm_keys == "Bin perturbation":
                                                try:
                                                    for j in range(len(st.session_state.loaded_bin_dict[k]) - 1):
                                                        if float(st.session_state.loaded_bin_dict[k][j]) <= float(
                                                                selected_rows[i][k][0]) <= float(
                                                                st.session_state.loaded_bin_dict[k][j + 1]):
                                                            new_list = [float(st.session_state.loaded_bin_dict[k][j]),
                                                                        float(st.session_state.loaded_bin_dict[k][j + 1])]
                                                            break

                                                    perturbedList[algorithm_keys] = (
                                                        perturbRange(new_list[0],
                                                                     new_list[1],
                                                                     method[algorithm_keys]["steps"]))
                                                except:
                                                    st.error(f"Value of **{column}** outside of bin range. Change value or create new bins.")



                                            elif algorithm_keys == 'Perturb in order':
                                                try:
                                                    perturbedList[algorithm_keys] = (
                                                        perturbInOrder(method[algorithm_keys]["steps"],
                                                                       selected_rows[i][k][0],
                                                                       st.session_state.data_restriction_final_deploymental[
                                                                           column]))



                                                except Exception as e:
                                                    st.write(e)


                                            elif algorithm_keys == 'Perturb all values':
                                                perturbedList[algorithm_keys] = (
                                                    perturbAllValues(  # method[algorithm_keys]["value"],
                                                        selected_rows[i][k][0],
                                                        st.session_state.data_restriction_final_deployment[column]))
                                except Exception as e:
                                    st.error(e)
                                perturbed_value_list[column] = perturbedList

                    except Exception as e:
                        st.write(e)
                    # index perturb contains the different perturbation values for each case
                    index_perturb.append(perturbed_value_list.copy())
                with st.expander("Show perturbed values"):
                    st.write(perturbed_value_list)

                try:
                    for i in range(0, len(selected_rows)):
                        for column, method in index_perturb[i].items():

                            # for column, method in perturbed_values.items():
                            #
                            if method:
                                # ausgewählte methoden ist ein dictionary mit der methode als key und perturbated values als value

                                # für jede ausgwählte row in aggrid gebe ein dictionary mit key = column und value = values aus
                                for method_name, perturbed_values in method.items():

                                    for k, v in selected_rows[i].items():
                                        if k == column:
                                            selected_rows[i][k].extend(perturbed_values)

                    result_df = pd.DataFrame(selected_rows,
                                             columns=result.columns)
                except Exception as e:
                    st.empty(e)

                # insert predictions of case into perturbed cases
                result_df["prediction"] = result["prediction"]

                try:
                    # prio and selected
                    for x in st.session_state.perturb_mode_values[::-1]:
                        result_df = result_df.explode(x)

                    # all values in order to have values and not a list
                    for x in st.session_state["dataframe_feature_names"]["featureName.value"].values.tolist():
                        result_df = result_df.explode(x)

                except Exception as e:
                    st.write(e)

                # delete duplicate rows in order to prevent multiple same perturbations

                result_df = result_df.drop_duplicates(keep='first')


                result_df["Case"] = result_df.index

            except Exception as e:
                st.info(e)

            try:


                x = pd.concat([df, result_df.iloc[:, :-1]]).reset_index(drop=True)
                x_filled = x.fillna(method='ffill').copy()


                for columns in x_filled:
                    try:
                        if st.session_state.level_of_measurement_dic[columns] == "Cardinal":
                            x_filled[columns] = x_filled[columns].astype(float)
                        else:
                            x_filled[columns] = x_filled[columns].astype(str)
                    except:
                        pass
                # x_filled
                try:
                    x_trans_df = pd.DataFrame(ct.fit_transform(x_filled).toarray(), columns=ct.get_feature_names_out()).reset_index(
                    drop=True)
                except:
                    # st.write(e)
                    x_trans_df = pd.DataFrame(ct.fit_transform(x_filled), columns=ct.get_feature_names_out()).reset_index(
                    drop=True)


                # get predictions for perturbed cases
                y_pred = pd.DataFrame(st.session_state.model.predict(x_trans_df))
                # reset index in order to remove rows which were generated for the onehotencoder
                y_pred = y_pred.iloc[len(df):].reset_index(drop=True)
                # reset index in order to be able to insert y_pred correctly
                result_df = result_df.reset_index(drop=True)
                result_df["perturbation"] = y_pred


                # KG: DEPLOYMENT
                # KG

                # Todo: Perturbation Assessment --> contains info which is handed over to the anaylst: testcases (which also could be in the ClassificationCase)
                # try:
                #     with st.expander("3: get prediction for perturbed cases"):
                #         st.write(result_df.style.apply(lambda x: ["background-color: #FF4B4B"
                #                                   if (v != x.iloc[0])
                #                                   else "" for i, v in enumerate(x)], axis=0))
                # except Exception as e:
                #     st.error(e)

                try:
                    st.session_state["dfs"] = [value for key, value in result_df.groupby('Case')]
                except Exception as e:
                    st.error(e)

                for i, df in enumerate(st.session_state["dfs"]):

                    # KG: DEPLOYMENT
                    # KG: ClassificationCase
                    # KG: selected_rows are ClassificationCase Entity
                    # TODO: Create Entity from selected rows, Values: PerturbedTestCase

                    ending_time = getTimestamp()
                    starting_time = getTimestamp()

                    determinationNameUUID = 'PerturbationOfClassificationCase'
                    determinationName = 'PerturbationOfClassificationCase'

                    name = 'PerturbationOfClassificationCase'
                    rprovName = 'PerturbationOfClassificationCase'
                    uuid_PerturbationAssessment = uuid.uuid4()
                    ending_time = getTimestamp()
                    if checkbox_upload:
                        try:
                            uuid_DefinitionOfPerturbationOption = determinationActivity(host_upload, determinationName,
                                                                                        label_list[i],
                                                                                        starting_time, ending_time)

                            uploadPerturbationAssessment(host_upload, uuid_PerturbationAssessment, label_list[i],
                                                         uuid_DefinitionOfPerturbationOption,
                                                         st.session_state.perturbationOptions_settings,
                                                         st.session_state.assessmentPerturbationOptions)
                            uuid_ClassificationCase = uuid.uuid4()

                            rows = selected_rows_DF.iloc[i].to_dict()
                            uploadClassificationCase(host_upload, uuid_ClassificationCase, label_list[i],
                                                     uuid_PerturbationAssessment,
                                                     rows)
                        except Exception as e:
                            st.error(e)

                    if len(label_list)>1:
                        expand_option_case = False
                    else:
                        expand_option_case = True
                    with st.expander(f"Get prediction for perturbed **case: {label_list[i]}**",expanded=expand_option_case):
                        df = df.drop(columns=["Case"])
                        if len(df.index) > 2500:
                            st.info(f"There are more than 2500 new cases, this could lead to performance issues. {len(df.index)} rows are generated, if performance issues occur. Please select less perturbation options.")

                        try:
                            st.dataframe(df[0:2000].style.apply(lambda x: ["background-color: {}".format(color_map.get(get_perturbation_level(x.name, v), "")) if v !=
                                                x.iloc[0] else "" for i, v in enumerate(x)], axis=0),use_container_width=True)
                        except Exception as e:
                            st.dataframe(df)
                            st.write(e)

                        different_pred = df.iloc[:1]

                        different_pred2 = df[df['prediction'] != df['perturbation']]
                        # shows the first original prediction
                        different_pred3 = pd.concat([different_pred, different_pred2]).reset_index(drop=True)

                        ste.download_button(f'Download CSV file for Case: {label_list[i]}',
                                            df.to_csv(index=False),
                                            f"{label_list[i]}_{uuid_PerturbationAssessment}.csv")

                        if different_pred2.empty:
                            st.info(f"No prediction with perturbated values changed for case {label_list[i]}")
                        else:
                            with st.expander("4: show cases where prediction changed"):
                                st.dataframe(different_pred3.style.apply(lambda x: ["background-color: {}".format(
                                    color_map.get(get_perturbation_level(x.name, v), "")) if v !=
                                                                                             x.iloc[0] else "" for i, v
                                                                    in enumerate(x)], axis=0),use_container_width=True)









            except Exception as e:
                st.info(e)




except Exception as e:
    st.warning(e)
