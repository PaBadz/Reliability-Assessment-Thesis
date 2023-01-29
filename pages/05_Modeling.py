import uuid

import numpy as np
import pandas as pd
import streamlit as st
import streamlit_nested_layout

from SPARQLWrapper import SPARQLWrapper, POST
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu

from functions.functions_Reliability import getDefault, changeAlgorithm, getRestriction, \
    defaultValuesCardinalRestriction, defaultValuesOrdinalRestriction, defaultValuesNominalRestriction, update_steps, \
    update_perturbation_level, update_additional_value, upper_lower_bound, update_value_perturbate
from functions.fuseki_connection import login, getAttributes, getDataRestrictionSeq, getUniqueValuesSeq, \
    get_connection_fuseki, prefix, getApproach, uploadApproach, getTimestamp, determinationActivity
from functions.perturbation_algorithms_ohne_values import percentage_perturbation_settings, sensorPrecision_settings, \
    fixedAmountSteps_settings, perturbRange_settings, perturbRange, perturbBin_settings, perturbInOrder_settings, \
    perturbAllValues_settings, perturbAllValues

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
# ------------------------------------------------------------------------------------------------------------------------

try:

    getDefault(host)
except:
    st.error("Please select other dataset or refresh page")
    st.stop()
try:
    getAttributes(host)
except:
    st.error("Please select other dataset or refresh page")
    st.stop()

if "data_restrictions_dict" not in st.session_state:
    st.session_state["data_restrictions_dict"] = dict()
if st.session_state.dataframe_feature_names.empty:
    st.stop()
# horizontal menu
selected2 = option_menu(None, ["Choose Algorithms", "Define Perturbation Options"],
                        icons=['house', 'gear'],
                        orientation="horizontal")
# Algorithm Options
options_cardinal = ['5% perturbation', '10% perturbation', 'Percentage perturbation', 'Sensor Precision',
                    'Fixed amount', 'Range perturbation', 'Bin perturbation']
options_ordinal = ['Perturb in order', 'Perturb all values']
options_nominal = ['Perturb all values']

if "default" not in st.session_state:
    st.session_state.cardinal_val = {}
    st.session_state.ordinal_val = {}
    st.session_state.nominal_val = {}
    st.session_state.default = {}
    for columns in st.session_state.dataframe_feature_names["featureName.value"]:
        st.session_state.default[columns] = []

if selected2 == 'Choose Algorithms':
    t1, t2 = st.tabs(["Algorithms", "Data Restriction"])
    with t1:
        colored_header(
            label="Choose Algorithms",
            description="",
            color_name="red-50",
        )
        tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])
        # TODO insert infobox if volatility is high with recommendation
        for columns, level in st.session_state.level_of_measurement_dic.items():

            if level == "Cardinal":
                settingList = dict()
                with tab1:

                    with st.expander(label=f"Algorithms for ***{columns}***"):
                        try:
                            if st.session_state.volatility_of_features_dic[columns] == 'High Volatility':
                                st.warning("Feature has high volatility!")
                            else:
                                st.info(f"Feature has {st.session_state.volatility_of_features_dic[columns]}!")

                        except:
                            st.info("Currently no level of volatility saved")
                        try:
                            st.session_state.default[columns] = st.multiselect(f'{columns}', options_cardinal,
                                                                               default=st.session_state.default[
                                                                                   columns],
                                                                               key=f"algo_{columns}",
                                                                               on_change=changeAlgorithm,
                                                                               args=(columns,))
                            st.session_state.cardinal_val[columns] = st.session_state.default[columns]
                            # TODO create dictionary similar to settingList in order to reuse code                           # settinglist[method] = [configurations]
                            st.write(st.session_state.cardinal_val[columns])

                        except Exception as e:
                            st.write(e)
                            st.info('No Cardinal Values', icon="ℹ️")

                        try:
                            if "Sensor Precision" in st.session_state.cardinal_val[columns]:
                                if columns not in st.session_state.loaded_feature_sensor_precision_dict.keys():
                                    st.error(
                                        f"No Sensor Precision for {columns} in Data Understanding step determined. Go to Data Understanding and determine sensor precision for this feature.")
                                else:
                                    st.write("Sensor Precision for this feature: ",
                                             st.session_state.loaded_feature_sensor_precision_dict[columns])
                        except:
                            pass
                        try:
                            if "Bin perturbation" in st.session_state.cardinal_val[columns]:
                                if columns not in st.session_state.loaded_bin_dict.keys():
                                    st.error(
                                        f"No Bin determined for feature {columns} in Data Preparation step determined. Go to Data Preparation and determine sensor precision for this feature.")
                                else:
                                    st.write("Bins determined for this Perturbation Option:",
                                             [[st.session_state.loaded_bin_dict[columns][i],
                                               st.session_state.loaded_bin_dict[columns][i + 1]] for i in
                                              range(len(st.session_state.loaded_bin_dict[columns]) - 1)])

                        except:
                            pass

            if level == "Ordinal":
                settingList = dict()
                with tab2:
                    with st.expander(label=f"Algorithms for ***{columns}***"):
                        try:
                            if st.session_state.volatility_of_features_dic[columns] == 'High Volatility':
                                st.warning("Feature has high volatility!")
                            else:
                                st.info(f"Feature has {st.session_state.volatility_of_features_dic[columns]}!")

                        except:
                            st.info("Currently no level of volatility saved")

                        try:
                            st.session_state.default[columns] = st.multiselect(f'{columns}', options_ordinal,
                                                                               default=st.session_state.default[
                                                                                   columns],
                                                                               key=f"algo_{columns}",
                                                                               on_change=changeAlgorithm,
                                                                               args=(columns,))
                            st.session_state.ordinal_val[columns] = st.session_state.default[columns]


                        except Exception as e:
                            st.write(e)
                            st.info('No Ordinal Values', icon="ℹ️")

            if level == "Nominal":
                settingList = dict()

                with tab3:
                    with st.expander(label=f"Algorithms for ***{columns}***"):
                        try:
                            if st.session_state.volatility_of_features_dic[columns] == 'High Volatility':
                                st.warning("Feature has high volatility!")
                            else:
                                st.info(f"Feature has {st.session_state.volatility_of_features_dic[columns]}!")

                        except:
                            st.info("Currently no level of volatility saved")

                        try:
                            st.session_state.default[columns] = st.multiselect(f'{columns}', options_nominal,
                                                                               default=st.session_state.default[
                                                                                   columns],
                                                                               key=f"algo_{columns}",
                                                                               on_change=changeAlgorithm,
                                                                               args=(columns,))
                            st.session_state.nominal_val[columns] = st.session_state.default[columns]
                        except:
                            st.info('No Nominal Values', icon="ℹ️")

        colored_header(
            label="Show Algorithms",
            description="Define level of scale for each feature",
            color_name="red-50",
        )
        with st.expander("Show chosen Algorithms"):
            try:
                if st.session_state['cardinal_val'] != {}:
                    st.write('**Cardinal**')
                    st.json(st.session_state['cardinal_val'])
                if st.session_state['ordinal_val'] != {}:
                    st.write('**Ordinal**')
                    st.json(st.session_state['ordinal_val'])
                if st.session_state['nominal_val'] != {}:
                    st.write('**Nominal**')
                    st.json(st.session_state['nominal_val'])
            except:
                st.info("If you select algorithms, they will be shown here", icon="ℹ️")

    # Select and Deselect Data Restriction
    with t2:
        try:
            uploaded_DataRestriction = getRestriction(host)
            if "data_restriction_URN" not in st.session_state:
                st.session_state.data_restriction_URN = pd.DataFrame(columns=uploaded_DataRestriction.columns)
            if st.session_state.data_restriction_URN.empty:
                st.error("No Data Restriction selected for this perturbation option selected")
            else:
                st.success("Data Restriction option selected")

            with st.expander("Show selected Data Restriction:"):
                colored_header(
                    label="Data Restriction",
                    description="",
                    color_name="red-50",
                )
                st.dataframe(st.session_state.data_restriction_URN[["Feature", "Value"]].reset_index(drop=True),
                             use_container_width=True)

            try:
                uploaded_DataRestriction = getRestriction(host)
                data_restriction = st.selectbox("Select Data Restriction",
                                                options=uploaded_DataRestriction["Comment"].unique())

                data_restriction_activity = uploaded_DataRestriction.loc[
                    uploaded_DataRestriction["Comment"] == data_restriction].reset_index(drop=True)

                st.dataframe(data_restriction_activity[["Label", "Feature", "Comment", "Value"]].reset_index(drop=True),
                             use_container_width=True)

                if st.button("Select Restriction", type="primary"):
                    st.session_state.data_restriction_URN = data_restriction_activity
                    try:
                        for key, value in st.session_state["level_of_measurement_dic"].items():
                            if value == "Cardinal":
                                defaultValuesCardinalRestriction(key)
                            if value == "Ordinal":
                                defaultValuesOrdinalRestriction(key)
                            if value == "Nominal":
                                defaultValuesNominalRestriction(key)
                        st.write(data_restriction_activity["DataRestrictionActivity"])
                        st.session_state["data_restrictions_dict"] = getDataRestrictionSeq(
                            data_restriction_activity["DataRestrictionActivity"][0], host)

                        st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()

                        st.session_state.data_restriction_final.update(st.session_state.data_restrictions_dict)
                        # st.session_state["flag_data_restriction"] = True

                        st.experimental_rerun()






                    except Exception as e:
                        st.write(e)
                        st.info("Dont forget to upload unique values")

                if st.button("Deselect Restriction"):
                    try:
                        st.session_state["data_restrictions_dict"] = dict()
                        st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()
                        st.session_state.data_restriction_final.update(st.session_state.data_restrictions_dict)
                        # st.session_state["flag_data_restriction"] = False
                        st.session_state.data_restriction_URN = pd.DataFrame(columns=uploaded_DataRestriction.columns)
                        st.experimental_rerun()
                    except Exception as e:
                        st.write(e)
                        st.write("Didnt work")



            except Exception as e:
                st.write(e)


        except Exception as e:
            st.info("No Data Restriction defined")
            st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()
            st.session_state.data_restriction_URN = pd.DataFrame(
                columns=['DataRestrictionActivity', 'DataRestrictionEntity', 'Label', 'Feature', 'Value'])

# Define Algorithmns


try:
    if selected2 == 'Define Perturbation Options':

        if "data_restriction_final" not in st.session_state:
            st.session_state.data_restriction_final = st.session_state.unique_values_dict


        tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])
        settings = dict()
        options_perturbation_level = ["Red", "Orange", "Green"]
        with tab1:

            # check if algorithm for level of scale is chosen
            is_empty = True
            for values in st.session_state['cardinal_val'].values():
                if values:
                    is_empty = False

            if is_empty:
                st.info("No Algorithm for cardinal feature chosen")

            for key, value in st.session_state['cardinal_val'].items():

                if "settingList" not in st.session_state:
                    st.session_state.settingList = dict()
                settingList = dict()
                # if "perturbedList" not in st.session_state:
                #     st.session_state.perturbedList = dict()
                # perturbedList = dict()

                with st.expander(f"Settings for feature {key}"):
                    for method in value:
                        if f"steps_{key}_{method}" not in st.session_state:
                            st.session_state[f"steps_{key}_{method}"] = 1

                        if f"assignedPerturbationLevel_{key}_{method}" not in st.session_state:
                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = "Red"

                        # First Initialize value which is to perturbate
                        if f"value_perturbate{key}_{method}" not in st.session_state:
                            st.session_state[f"value_perturbate{key}_{method}"] = float(
                                st.session_state.data_restriction_final[key][0])

                        # set Data Restriction if selected
                        if st.session_state[f"value_perturbate{key}_{method}"] < float(
                                st.session_state.data_restriction_final[key][0]):
                            st.session_state[f"value_perturbate{key}_{method}"] = float(
                                st.session_state.data_restriction_final[key][0])

                        if f"additional_value_{key}_{method}" not in st.session_state:
                            if 0 < float(st.session_state.data_restriction_final[key][0]):
                                st.session_state[f"additional_value_{key}_{method}"] = \
                                st.session_state.data_restriction_final[key][0]
                            else:
                                st.session_state[f"additional_value_{key}_{method}"] = 0
                        if "lower_bound" not in st.session_state:
                            st.session_state[f"lower_bound{key}_{method}"] = 0
                        if "upper_bound" not in st.session_state:
                            st.session_state[f"upper_bound{key}_{method}"] = 0

                        if method == 'Percentage perturbation':
                            st.markdown(f"##### {method}")

                            st.session_state[f"steps_{key}_{method}"] = int(
                                st.number_input("Percentage of steps", min_value=int(1), max_value=int(100),
                                                value=int(st.session_state[f"steps_{key}_{method}"]),
                                                key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                                args=(key, method)))

                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                "Select Perturbation Level", options=options_perturbation_level,
                                index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help="Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change",
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level, args=(key, method))
                            if st.button("Ok", key =f"submit_{key}_{method}"):
                                settingList[method] = (
                                percentage_perturbation_settings(st.session_state[f"steps_{key}_{method}"],
                                                                 st.session_state[
                                                                     f"assignedPerturbationLevel_{key}_{method}"]))
                            st.write("---------------")

                        if method == "5% perturbation":
                            st.markdown(f"##### {method}")
                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                "Select Perturbation Level", options=options_perturbation_level,
                                index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help="Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change",
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))
                            settingList[method] = (
                                percentage_perturbation_settings(5, st.session_state[
                                    f"assignedPerturbationLevel_{key}_{method}"]))
                            st.write("---------------")

                        if method == "10% perturbation":
                            st.markdown(f"##### {method}")
                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                "Select Perturbation Level", options=options_perturbation_level,
                                index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help="Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change",
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                percentage_perturbation_settings(10, st.session_state[
                                    f"assignedPerturbationLevel_{key}_{method}"]))
                            st.write("---------------")




                        elif method == 'Sensor Precision':
                            try:
                                if key not in st.session_state.loaded_feature_sensor_precision_dict:
                                    st.warning("Sensor Precision is not determined in Data Understanding Step")
                                    st.session_state.loaded_feature_sensor_precision_dict[key]

                                else:
                                    st.session_state[f"additional_value_{key}_{method}"] = \
                                        st.session_state.loaded_feature_sensor_precision_dict[key]

                                st.markdown(f"##### {method}")


                                st.session_state[f"steps_{key}_{method}"] = int(
                                    st.number_input("Steps", min_value=int(1), step=int(1),
                                                    value=int(st.session_state[f"steps_{key}_{method}"]),
                                                    key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                                    args=(key, method)))

                                st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                    "Select Perturbation Level", options=options_perturbation_level,
                                    index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                    help="Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change",
                                    key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                    on_change=update_perturbation_level,
                                    args=(key, method))

                                # st.session_state[f"additional_value_{key}_{method}"] = round(float(
                                #     st.number_input("Sensor Precision", min_value=float(0.01), max_value=float(100),
                                #               value=float(st.session_state[f"additional_value_{key}_{method}"]),
                                #               key=f"additional_value_widget_{key}_{method}",#step=float(step)
                                #               on_change=update_additional_value, args=(key, method))),2)

                                st.write(
                                    f"Sensor Precision: **{st.session_state.loaded_feature_sensor_precision_dict[key]}**")

                                # st.session_state[f"steps_{key}_{method}"] = int(
                                #     st.number_input("Steps", min_value=int(1), step=int(1),
                                #               value=int(st.session_state[f"steps_{key}_{method}"]),
                                #               key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                #               args=(key, method)))

                                settingList[method] = (
                                    sensorPrecision_settings(st.session_state[f"additional_value_{key}_{method}"],
                                                             st.session_state[f"steps_{key}_{method}"],
                                                             st.session_state[
                                                                 f"assignedPerturbationLevel_{key}_{method}"]))

                            except Exception as e:
                                st.write(
                                    "Sensor Precision for this feature should be determined in Data Understanding step.")


                                # st.write(e)
                            st.write("---------------")

                        elif method == 'Fixed amount':
                            st.markdown(f"##### Define settings for algorithm: {method}")
                            st.session_state[f"additional_value_{key}_{method}"] = float(st.number_input("Amount",
                                                                                                         value=float(
                                                                                                             st.session_state[
                                                                                                                 f"additional_value_{key}_{method}"]),
                                                                                                         min_value=float(
                                                                                                             st.session_state.data_restriction_final[
                                                                                                                 key][
                                                                                                                 0]),
                                                                                                         max_value=float(
                                                                                                             st.session_state.data_restriction_final[
                                                                                                                 key][
                                                                                                                 1]),
                                                                                                         key=f"additional_value_widget_{key}_{method}",
                                                                                                         on_change=update_additional_value,
                                                                                                         args=(
                                                                                                         key, method)))
                            # float(
                            # st.slider("Amount", min_value=float(
                            #     st.session_state.data_restriction_final[key][0]), max_value=float(
                            #     st.session_state.data_restriction_final[key][1]), step=float(1),
                            #           value=st.session_state[f"additional_value_{key}_{method}"],
                            #           key=f"additional_value_widget_{key}_{method}",
                            #           on_change=update_additional_value,
                            #           args=(key, method)))

                            st.session_state[f"steps_{key}_{method}"] = int(
                                st.number_input("Steps",  # min_value=int(1), max_value=int(100), step=int(1),
                                                value=st.session_state[f"steps_{key}_{method}"],
                                                key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                                args=(key, method)))

                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                "Select Perturbation Level", options=options_perturbation_level,
                                index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help="Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change",
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                fixedAmountSteps_settings(st.session_state[f"additional_value_{key}_{method}"],
                                                          st.session_state[f"steps_{key}_{method}"], st.session_state[
                                                              f"assignedPerturbationLevel_{key}_{method}"]))

                            st.write("---------------")

                        elif method == 'Range perturbation':
                            st.markdown(f"##### Define settings for algorithm: {method}")

                            if f"additional_value_{key}_{method}_bound" not in st.session_state:
                                st.session_state[f"additional_value_{key}_{method}_bound"] = [
                                    float(st.session_state.data_restriction_final[key][0]),
                                    float(st.session_state.data_restriction_final[key][-1])]

                            with st.form(f"Input values {key}"):
                                lower_border = st.number_input("Select lower border",
                                                               value=float(
                                                                   st.session_state.data_restriction_final[key][0]),
                                                               min_value=float(
                                                                   st.session_state.data_restriction_final[key][0]),
                                                               max_value=float(
                                                                   st.session_state.data_restriction_final[key][-1]),
                                                               key=f"lower_border_range_perturbation_{key}")
                                upper_border = st.number_input("Select upper border", value=float(
                                    st.session_state.unique_values_dict[key][-1]), max_value=float(
                                    st.session_state.unique_values_dict[key][-1]),
                                                               key=f"upper_border_range_perturbation_{key}")

                                # lower = st.number_input("Input lower value", )
                                # upper = st.number_input("Input upper value",max_value=float(
                                #     st.session_state.data_restriction_final[key][-1]))
                                if st.form_submit_button("Upload"):
                                    if st.session_state[f"lower_border_range_perturbation_{key}"] >= st.session_state[
                                        f"upper_border_range_perturbation_{key}"]:
                                        st.error("Lower bound range must be smaller than upper bound.")
                                    else:
                                        st.session_state[f"additional_value_{key}_{method}_bound"] = [
                                            float(lower_border),
                                            float(upper_border)]

                            st.session_state[f"additional_value_{key}_{method}_bound"] = (
                                st.slider("Amount", min_value=float(
                                    st.session_state.data_restriction_final[key][0]), max_value=float(
                                    st.session_state.data_restriction_final[key][-1]),
                                          value=st.session_state[f"additional_value_{key}_{method}_bound"],
                                          key=f"additional_value_widget_{key}_{method}",
                                          on_change=upper_lower_bound,
                                          args=(key, method)))

                            if st.session_state[f"steps_{key}_{method}"] == 0:
                                st.session_state[f"steps_{key}_{method}"] = 1

                            st.session_state[f"steps_{key}_{method}"] = int(
                                st.number_input("Steps", step=int(1),
                                                # min_value=int(1), max_value=int(100), step=int(1),
                                                value=st.session_state[f"steps_{key}_{method}"],
                                                key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                                args=(key, method)))

                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                "Select Perturbation Level", options=options_perturbation_level,
                                index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help="Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change",
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                perturbRange_settings(st.session_state[f"additional_value_{key}_{method}_bound"][0],
                                                      st.session_state[f"additional_value_{key}_{method}_bound"][1],
                                                      st.session_state[f"steps_{key}_{method}"],
                                                      st.session_state[f"assignedPerturbationLevel_{key}_{method}"]))

                            st.write("---------------")
                            st.write("---------------")

                        elif method == 'Bin perturbation':
                            st.markdown(f"##### Define settings for algorithm: {method}")
                            try:
                                if key not in st.session_state.loaded_bin_dict:
                                    st.warning("Sensor Precision is not determined in Data Understanding Step")

                                    st.write(st.session_state.loaded_bin_dict[key])

                                else:

                                    st.write([[st.session_state.loaded_bin_dict[key][i],
                                               st.session_state.loaded_bin_dict[key][i + 1]] for i in
                                              range(len(st.session_state.loaded_bin_dict[key]) - 1)])

                                    st.session_state[f"steps_{key}_{method}"] = int(
                                        st.number_input("Steps",  # min_value=int(1), max_value=int(100), step=int(1),
                                                        value=st.session_state[f"steps_{key}_{method}"],
                                                        key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                                        args=(key, method)))

                                    st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                        "Select Perturbation Level", options=options_perturbation_level,
                                        index=options_perturbation_level.index(
                                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                        help="Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change",
                                        key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                        on_change=update_perturbation_level,
                                        args=(key, method))

                                    settingList[method] = (
                                        perturbBin_settings(st.session_state[f"steps_{key}_{method}"], st.session_state[
                                            f"assignedPerturbationLevel_{key}_{method}"]))

                                    st.write("---------------")
                            except Exception as e:
                                st.write(e)
                                st.write(
                                    "Binning for this feature should be determined in Data Preparation step.")


                if settingList:
                    settings[key] = settingList
            st.session_state['settings'] = settings


        with tab2:

            # check if algorithm for level of scale is chosen
            is_empty = True
            for values in st.session_state['ordinal_val'].values():
                if values:
                    is_empty = False

            if is_empty:
                st.info("No Algorithm for ordinal feature chosen")

            for key, value in st.session_state['ordinal_val'].items():
                if "settingList" not in st.session_state:
                    st.session_state.settingList = dict()
                settingList = dict()

                with st.expander(f"Settings for column {key}"):

                    for method in value:
                        if f"assignedPerturbationLevel_{key}_{method}" not in st.session_state:
                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = "Red"
                        if f"steps_{key}_{method}" not in st.session_state:
                            st.session_state[f"steps_{key}_{method}"] = 1
                        if f"value_perturbate{key}_{method}" not in st.session_state:
                            st.session_state[f"value_perturbate{key}_{method}"] = \
                                st.session_state.data_restriction_final[key][0]
                        if f"additional_value_{key}_{method}" not in st.session_state:
                            st.session_state[f"additional_value_{key}_{method}"] = 0

                        if method == "Perturb in order":
                            st.markdown(f"##### Define settings for algorithm: {method}")
                            with st.expander("Show all values:"):
                                st.session_state.data_restriction_final[key]
                            st.session_state[f"steps_{key}_{method}"] = int(
                                st.slider("Steps", min_value=int(1),
                                          max_value=int(len(st.session_state.data_restriction_final[key]) - 1),
                                          step=int(1),
                                          value=st.session_state[f"steps_{key}_{method}"],
                                          key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                          args=(key, method)))

                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                "Select Perturbation Level", options=options_perturbation_level,
                                index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help="Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change",
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                perturbInOrder_settings(st.session_state[f"steps_{key}_{method}"],
                                                        st.session_state[f"assignedPerturbationLevel_{key}_{method}"]))

                            st.write("---------------")

                        if method == "Perturb all values":
                            st.markdown(f"##### Define settings for algorithm: {method}")

                            with st.expander("Show all values:"):
                                st.session_state.data_restriction_final[key]

                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                "Select Perturbation Level", options=options_perturbation_level,
                                index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help="Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change",
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                perturbAllValues_settings(st.session_state[
                                                              f"assignedPerturbationLevel_{key}_{method}"]))  # st.session_state[f"value_perturbate{key}_{method}"],


                            st.write("---------------")

                    if settingList:
                        settings[key] = settingList

                st.session_state['settings'] = settings


        with tab3:
            # check if algorithm for level of scale is chosen
            is_empty = True
            for values in st.session_state['nominal_val'].values():
                if values:
                    is_empty = False

            if is_empty:
                st.info("No Algorithm for nominal feature chosen")

            for key, value in st.session_state['nominal_val'].items():
                if "settingList" not in st.session_state:
                    st.session_state.settingList = dict()
                settingList = dict()

                with st.expander(f"Settings for column {key}"):


                    for method in value:
                        if f"assignedPerturbationLevel_{key}_{method}" not in st.session_state:
                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = "Red"
                        if f"steps_{key}_{method}" not in st.session_state:
                            st.session_state[f"steps_{key}_{method}"] = 0
                        if f"value_perturbate{key}_{method}" not in st.session_state:
                            st.session_state[f"value_perturbate{key}_{method}"] = \
                                st.session_state.data_restriction_final[key][0]
                        if f"additional_value_{key}_{method}" not in st.session_state:
                            st.session_state[f"additional_value_{key}_{method}"] = 0

                        if method == "Perturb all values":
                            st.markdown(f"##### Define settings for algorithm: {method}")

                            with st.expander("Show all values:"):
                                st.session_state.data_restriction_final[key]

                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                "Select Perturbation Level", options=options_perturbation_level,
                                index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help="Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change",
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                perturbAllValues_settings(st.session_state[
                                                              f"assignedPerturbationLevel_{key}_{method}"]))  # st.session_state.data_restriction_final[key],st.session_state[f"value_perturbate{key}_{method}"]))#,st.session_state.data_restriction_final[key]))

                            st.write("---------------")

                    if settingList:
                        settings[key] = settingList

                st.session_state['settings'] = settings


        if st.session_state['settings'] != {}:
            with st.expander("Show Perturbation Setting"):
                st.write(st.session_state['settings'])

                # todo ausgliedern
                # kann auch implementiert werden bei predict --> dadurch verpflichtend

            if st.session_state.data_restriction_URN["DataRestrictionEntity"].empty:
                st.info("No Data Restriction selected for this perturbation option selected")
            else:
                st.info("Data Restriction selected")

            with st.form("Insert additional label for the defined Perturbation Options"):
                st.info(
                    "This label should be chosen wisely. It will be shown in the options for the Deployment. Therefore it is advised to add as much information as possible.")
                labelPerturbation = st.text_input("Insert additional label for the defined Perturbation Options",
                                                  help="Name your Perturbation Option in order to find it easier later.")

                if st.form_submit_button("Submit label"):
                    query = (f""" SELECT  ?PerturbationOptionLabel WHERE{{
    						?DataUnderstandingEntityID rdf:type rprov:PerturbationOption.
    						?DataUnderstandingEntityID rdfs:label ?PerturbationOptionLabel.
                      }}""")

                    results = get_connection_fuseki(host, (prefix + query))
                    results = pd.json_normalize(results["results"]["bindings"])

                    # Iterate over the rows of the DataFrame
                    for index, row in results.iterrows():
                        # Get the part of the string before the first '-'
                        value = row["PerturbationOptionLabel.value"].split('-', 1)[0]

                        # Check if the searched value is present
                        if value == labelPerturbation:
                            raise ValueError(f"{labelPerturbation} found in column {row.name}")

            if st.button("Save Modeling Activity to Database", type='primary', help="Save the Modeling Activity and Entity to the Database."):
                # check if choice of assessment is defined
                try:
                    getApproach(host)
                except Exception as e:
                    uuid_activity = uuid.uuid4()
                    uuid_entity = uuid.uuid4()
                    uploadApproach(host_upload, uuid_activity, uuid_entity)

                # Modeling Phase
                # KG DEVELOPMENT
                # KG: DefinitionOfPertubartionOption
                # KG: Define ModelingActivity and then create PerturbationOption Entity with BUA, DUA, DPA as input

                ending_time = getTimestamp()

                starting_time = getTimestamp()
                # KG label nötig? Um die PerturbationOption zu identifizieren?

                # First create ModelingActivity
                label = "Definition of Perturbation Option"  # st.text_input("Definition of Perturbation Option",help="Insert a name for the perturbation option")
                determinationNameUUID = 'DefinitionOfPerturbationOption'
                determinationName = 'DefinitionOfPerturbationOption'

                name = 'PerturbationOption'
                rprovName = 'PerturbationOption'

                # Get BUE PerturbationApproach
                business_understanding_entity = getApproach(host)

                # TODO ausgliedern
                try:
                    query = (f"""SELECT ?featureID ?featureName ?rprov ?DataUnderstandingEntityID ?DUA WHERE{{
    			            ?featureID rdf:type rprov:Feature .
                            ?featureID rdfs:label ?featureName.
                            ?DataUnderstandingEntityID rprov:toFeature ?featureID.
    						?DataUnderstandingEntityID rdf:type ?rprov.
                            ?DataUnderstandingEntityID rprov:wasGeneratedByDUA|rprov:wasGeneratedByDPA|rprov:wasGeneratedByBUA ?DUA.
                            FILTER(?rprov!=owl:NamedIndividual)
                            FILTER(?rprov!=rprov:DataRestriction)
                            FILTER(?rprov!=rprov:SensorPrecisionOfFeature)  
                            FILTER(?rprov!=rprov:RangeOfBinnedFeature)
                            FILTER NOT EXISTS{{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}}
    
    }}""")

                    try:
                        results_update = get_connection_fuseki(host, (prefix + query))
                        # get Activities for PerturbationOption
                        result_2 = pd.json_normalize(results_update["results"]["bindings"])
                        result_2 = result_2.groupby(["featureID.value", "featureName.value"], as_index=False)[
                            "DataUnderstandingEntityID.value"].agg(list)
                    except:
                        st.info("No Level of volatility, missing values determined")

                    # for key in st.session_state['settings']:
                    # TODO Decide whether PerturbationOption is generated for each feature or all together
                    # upload ModelingActivity to fueski

                    ####################################################################################################

                    uuid_DefinitionOfPerturbationOption = determinationActivity(host_upload, determinationName,
                                                                                label,
                                                                                starting_time, ending_time)
                    ####################################################################################################

                    # if feature is in perturbation settings
                    # create list with activities an loop in order to insert them as modelingEntityWasDerivedFrom

                    for key in st.session_state['settings']:
                        try:
                            if key in result_2["featureName.value"].values:
                                uploaded_entities = (result_2[result_2["featureName.value"] == key])

                                # TODO delete data restcition if not chosen

                                # st.write(np.concatenate(
                                #     uploaded_entities["DataUnderstandingEntityID.value"].values).tolist())
                                liste = (np.concatenate(
                                    uploaded_entities["DataUnderstandingEntityID.value"].values).tolist())
                                liste.append(business_understanding_entity)
                        except:

                            liste = list()

                        featureID = st.session_state.DF_feature_scale_name[
                            st.session_state.DF_feature_scale_name["featureName.value"] == key]

                        try:
                            if key in st.session_state.data_restriction_URN["Feature"].values:
                                data_restriction = st.session_state.data_restriction_URN[
                                    st.session_state.data_restriction_URN["Feature"] == key][
                                    "DataRestrictionEntity"].reset_index(drop=True)
                                liste.append(data_restriction[0])
                        except Exception as e:
                            st.write(e)


                        # create another loop in order to get different UUIDs for PerturbationOptions
                        # KG sollen die einzelnen Optionen einzeln oder gesammelt gespeichert werden
                        for method, perturbationOption in st.session_state['settings'][key].items():
                            uuid_PerturbationOption = uuid.uuid4()
                            liste_new = liste.copy()

                            if method == "Bin perturbation":
                                bin_entity = \
                                st.session_state.DF_bin_dict[st.session_state.DF_bin_dict["label.value"] == key][
                                    "DPE.value"].reset_index(drop=True)
                                liste_new.append(bin_entity[0])

                            if method == "Sensor Precision":
                                sensor_precision = st.session_state.DF_feature_sensor_precision[
                                    st.session_state.DF_feature_sensor_precision["featureName.value"] == key][
                                    "DataUnderstandingEntityID.value"].reset_index(drop=True)
                                liste_new.append(sensor_precision[0])

                            # get dataunderstandingentity for sensor precision and if perturbation option contains sensor precision insert into list
                            # create new dataunderstandingentity if sensor precision is different?
                            # update dataunderstandingentity if sensor precision is different?

                            for entities in liste_new:
                                perturbationOptionlabel = str(perturbationOption)

                                perturbationOptionlabel = perturbationOptionlabel.replace("'", "").replace("{",
                                                                                                           "").replace(
                                    "}", "")

                                # if method == "Perturb all values":
                                #     query = (
                                #         f"""INSERT DATA {{<urn:uuid:{uuid_PerturbationOption}> rdf:type rprov:{name}, owl:NamedIndividual;
                                #                                                                  rprov:perturbedFeature <{featureID["featureID.value"].values[0]}>;
                                #                                                                  rprov:generationAlgorithm "{method}";
                                #                                                                  rprov:values "{perturbationOption}"@en;
                                #                                                                  rprov:modelingEntityWasDerivedFrom <{entities}>;
                                #                                                                  rprov:wasGeneratedByMA  <urn:uuid:{uuid_DefinitionOfPerturbationOption}>;
                                #                                                                  rdfs:label "{labelPerturbation}-{method}"@en.
                                #                                                                }}""")  ##{st.session_state['settings'][key]}rprov:values "{perturbationOption}"@en;
                                # else:

                                query = (f"""INSERT DATA {{<urn:uuid:{uuid_PerturbationOption}> rdf:type rprov:{name}, owl:NamedIndividual;
                                                      rprov:perturbedFeature <{featureID["featureID.value"].values[0]}>;
                                                      rprov:generationAlgorithm "{method}";
                                                      rprov:values "{perturbationOption}"@en;
                                                      rprov:modelingEntityWasDerivedFrom <{entities}>;
                                                      rprov:wasGeneratedByMA  <urn:uuid:{uuid_DefinitionOfPerturbationOption}>;
                                                      rdfs:label "{labelPerturbation}-{method}: {perturbationOptionlabel}"@en.
                                                    }}""")


                                host_upload.setQuery(prefix + query)
                                host_upload.setMethod(POST)
                                host_upload.query()
                    st.success("Perturbation Options saved")

                    # st.stop()
                except Exception as e:
                    st.write(e)
                    st.error("Error: Could not create DUA")



except Exception as e:
    st.warning(e)
