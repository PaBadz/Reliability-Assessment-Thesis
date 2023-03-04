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
    get_connection_fuseki, prefix, getApproach, uploadApproach, getTimestamp, determinationActivity, get_dataset
from functions.perturbation_algorithms_ohne_values import percentage_perturbation_settings, sensorPrecision_settings, \
    fixedAmountSteps_settings, perturbRange_settings, perturbRange, perturbBin_settings, perturbInOrder_settings, \
    perturbAllValues_settings, perturbAllValues

login()

host, host_upload = get_dataset()


try:
    getUniqueValuesSeq(host)
except Exception as e:
    st.error("Please upload feature values in Data Understanding step")
    if st.button("Data Understanding"):
        switch_page("Data Understanding")
    st.stop()

try:
    getDefault(host)
except:
    st.error("Couldn't load unique values. If already inserted refresh page.")
# horizontal menu
selected2 = option_menu(None, ["Choose Perturbation Option", "Define Perturbation Options"],
                        icons=['check2-circle', 'gear'],
                        orientation="horizontal")
with st.expander("Show information"):
    try:
        getAttributes(host)
    except Exception as e:
        st.error("Please refresh page or change database.")
        st.stop()
    if "data_restriction_final" not in st.session_state:
        st.session_state.data_restriction_final = st.session_state.unique_values_dict
    try:
        # TODO include data restriction in getAttributes
        uploaded_DataRestriction = getRestriction(host)
        st.session_state["data_restrictions_dict"] = getDataRestrictionSeq(
            uploaded_DataRestriction["DUA.value"][0], host)

        st.session_state.data_restriction_final.update(st.session_state["data_restrictions_dict"])
    except:
        st.warning("No Data Restrictions determined")

if "data_restrictions_dict" not in st.session_state:
    st.session_state["data_restrictions_dict"] = dict()
if st.session_state.dataframe_feature_names.empty:
    st.stop()

# Algorithm Options
options_cardinal = ['5% Perturbation', '10% Perturbation', 'Percentage Perturbation',
                    'Fixed Amount Perturbation', 'Range Perturbation', 'Sensor Precision Perturbation','Bin Perturbation']
options_ordinal = ['Perturb in order', 'Perturb all values']
options_nominal = ['Perturb all values']

if "default" not in st.session_state:
    st.session_state.cardinal_val = {}
    st.session_state.ordinal_val = {}
    st.session_state.nominal_val = {}
    st.session_state.default = {}
    for columns in st.session_state.dataframe_feature_names["featureName.value"]:
        st.session_state.default[columns] = []

if selected2 == 'Choose Perturbation Option':

    colored_header(
        label="Choose Perturbation Option per feature",
        description="Here you can select which algorithms should be used for the perturbation options per feature.",
        color_name="red-50",
    )
    tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])
    # TODO insert infobox if volatility is high with recommendation
    for columns, level in st.session_state.level_of_measurement_dic.items():

        if level == "Cardinal":
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


                    except Exception as e:
                        st.info('No Cardinal Values', icon="ℹ️")

                    try:
                        if "Sensor Precision Perturbation" in st.session_state.cardinal_val[columns]:
                            if columns not in st.session_state.loaded_feature_sensor_precision_dict.keys():
                                st.error(
                                    f"No Sensor Precision for {columns} in Data Understanding step determined. Go to Data Understanding and determine sensor precision for this feature.")
                            else:
                                st.write("Sensor Precision for this feature: ",
                                         st.session_state.loaded_feature_sensor_precision_dict[columns])
                    except:
                        pass
                    try:
                        if "Bin Perturbation" in st.session_state.cardinal_val[columns]:
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
        description="Show chosen algorithms for each feature",
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


try:
    if selected2 == 'Define Perturbation Options':

        if "entities" not in st.session_state:
            st.session_state.entities = dict()


        tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])
        settings = dict()
        perturbationLevel = dict()
        options_perturbation_level = ["Red", "Orange", "Green"]
        with tab1:
            # check if algorithm for level of scale is chosen
            is_empty = True
            for values in st.session_state['cardinal_val'].values():
                if values:
                    is_empty = False

            if is_empty:
                st.info("No Algorithm for cardinal feature chosen")

            for key, values in st.session_state['cardinal_val'].items():


                settingList = dict()
                perturbationLevel_list = dict()


                with st.expander(f"Settings for feature {key}"):
                    try:
                        if values:

                            query = f"""SELECT ?featureID ?featureName ?rprov ?DataUnderstandingEntityID ?label ?DUA WHERE{{
                                                     ?featureID rdf:type rprov:Feature .
                                                     ?featureID rdfs:label '{key}'.
                                                     ?DataUnderstandingEntityID rprov:toFeature ?featureID.
                                                     ?DataUnderstandingEntityID rdf:type ?rprov.
                                                     ?DataUnderstandingEntityID rprov:wasGeneratedByDUA|rprov:wasGeneratedByDPA|rprov:wasGeneratedByBUA ?DUA.   
                                                     ?DataUnderstandingEntityID rdfs:label ?label.
                                                     FILTER(?rprov!=owl:NamedIndividual)
                                                     FILTER(?rprov!=rprov:ScaleOfFeature)  
                                                     FILTER(?rprov!=rprov:SensorPrecisionOfFeature)  
                                                     FILTER(?rprov!=rprov:RangeOfBinnedFeature)
                                                     FILTER(?rprov!=rprov:UniqueValuesOfFeature)
                                                     FILTER NOT EXISTS{{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}}

                             }}"""

                            try:
                                results_update = get_connection_fuseki(host, (prefix + query))

                                # get Activities for PerturbationOption
                                result_2 = pd.json_normalize(results_update["results"]["bindings"])
                                entities_selection = result_2["label.value"].tolist()

                                if len(entities_selection) > 0:
                                    entities = st.multiselect(
                                        label="Select entities which should be included in the perturbation option",
                                        options=entities_selection, default=entities_selection)


                            except Exception as e:
                                entities = []
                                st.info("No Level of volatility, Data Restrictions or missing values determined")

                            query = f"""SELECT ?featureID ?featureName ?rprov ?DataUnderstandingEntityID ?label ?DUA WHERE{{
                                                                             ?featureID rdf:type rprov:Feature .
                                                                             ?featureID rdfs:label '{key}'.
                                                                             ?DataUnderstandingEntityID rprov:toFeature ?featureID.
                                                                             ?DataUnderstandingEntityID rdf:type ?rprov.
                                                                             ?DataUnderstandingEntityID rprov:wasGeneratedByDUA|rprov:wasGeneratedByDPA|rprov:wasGeneratedByBUA ?DUA.
                                                                             ?DataUnderstandingEntityID rdfs:label ?label.
                                                                             FILTER(?rprov!=owl:NamedIndividual)
                                                                             FILTER(?rprov!=rprov:SensorPrecisionOfFeature)  
                                                                             FILTER(?rprov!=rprov:RangeOfBinnedFeature)
                                                                             FILTER(?rprov!=rprov:UniqueValuesOfFeature)
                                                                             FILTER NOT EXISTS{{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}}
                                }}"""

                            try:
                                results_update = get_connection_fuseki(host, (prefix + query))
                                # get Activities for PerturbationOption
                                result_2 = pd.json_normalize(results_update["results"]["bindings"])
                                entities.append(result_2["label.value"][0])
                            except Exception as e:
                                st.error(e)

                            try:
                                st.session_state["entities"][key] = (result_2[result_2['label.value'].isin(entities)])[
                                    "DataUnderstandingEntityID.value"].tolist()
                                st.write(result_2[result_2['label.value'].isin(entities)])

                                flag = False

                                for value in entities:
                                    if value.startswith("restriction"):
                                        flag = True
                                if flag == True:
                                    st.session_state.data_restriction_final[key] = \
                                    st.session_state.data_restrictions_dict[key]

                                else:

                                    st.session_state.data_restriction_final[key] = (
                                    st.session_state.unique_values_dict[key])
                                st.session_state.data_restriction_final[key]
                            except Exception as e:
                                st.error(e)
                    except Exception as e:
                        st.error(e)
                    for method in values:
                        st.write(method)
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

                        if method == 'Percentage Perturbation':
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
                            settingList[method] = (
                                percentage_perturbation_settings(st.session_state[f"steps_{key}_{method}"])                                                                )
                            perturbationLevel_list[method] =  st.session_state[
                                                                     f"assignedPerturbationLevel_{key}_{method}"]
                            st.write("---------------")

                        if method == "5% Perturbation":
                            st.markdown(f"##### {method}")
                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                "Select Perturbation Level", options=options_perturbation_level,
                                index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help="Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change",
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))
                            settingList[method] = (
                                percentage_perturbation_settings(5))
                            perturbationLevel_list[method] =  st.session_state[
                                                                     f"assignedPerturbationLevel_{key}_{method}"]
                            st.write("---------------")

                        if method == "10% Perturbation":
                            st.markdown(f"##### {method}")
                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                "Select Perturbation Level", options=options_perturbation_level,
                                index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help="Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change",
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                percentage_perturbation_settings(10))
                            perturbationLevel_list[method] =  st.session_state[
                                                                     f"assignedPerturbationLevel_{key}_{method}"]
                            st.write("---------------")

                        elif method == 'Sensor Precision Perturbation':
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
                                    help="Determines whether the prediction with this perturbation option is allowed to change: "
                                         "Red means thet the prediction for that perturbation option should not change. "
                                         "Orange means that prediction might change. Green means that prediction is expected to change",
                                    key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                    on_change=update_perturbation_level,
                                    args=(key, method))

                                st.write(
                                    f"Sensor Precision: **{st.session_state.loaded_feature_sensor_precision_dict[key]}**")

                                settingList[method] = (
                                    sensorPrecision_settings(st.session_state[f"additional_value_{key}_{method}"],
                                                         st.session_state[f"steps_{key}_{method}"]))
                                perturbationLevel_list[method] = st.session_state[
                                    f"assignedPerturbationLevel_{key}_{method}"]

                            except Exception as e:
                                st.write("Sensor Precision for this feature should be determined in Data Understanding step.")
                            st.write("---------------")

                        elif method == 'Fixed Amount Perturbation':
                            st.markdown(f"##### Define settings for algorithm: {method}")
                            st.session_state[f"additional_value_{key}_{method}"] = float(st.number_input("Amount",
                                                value=float(st.session_state[f"additional_value_{key}_{method}"]),
                                                min_value=float(0.01),
                                                max_value=float(st.session_state.data_restriction_final[key][1]),
                                                key=f"additional_value_widget_{key}_{method}",
                                                on_change=update_additional_value,
                                                args=(key, method)))


                            st.session_state[f"steps_{key}_{method}"] = int(
                                st.number_input("Steps",
                                                min_value=int(1),
                                                step=int(1),
                                                value=st.session_state[f"steps_{key}_{method}"],
                                                key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                                args=(key, method)))

                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                "Select Perturbation Level", options=options_perturbation_level,
                                index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help="Determines whether the prediction with this perturbation option is allowed to change: "
                                     "Red means thet the prediction for that perturbation option should not change. "
                                     "Orange means that prediction might change. Green means that prediction is expected to change",
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                fixedAmountSteps_settings(st.session_state[f"additional_value_{key}_{method}"],
                                                          st.session_state[f"steps_{key}_{method}"]))
                            perturbationLevel_list[method] =  st.session_state[
                                                                     f"assignedPerturbationLevel_{key}_{method}"]

                            st.write("---------------")

                        elif method == 'Range Perturbation':
                            st.markdown(f"##### Define settings for algorithm: {method}")

                            if f"additional_value_{key}_{method}_bound" not in st.session_state:
                                st.session_state[f"additional_value_{key}_{method}_bound"] = [
                                    float(st.session_state.data_restriction_final[key][0]),
                                    float(st.session_state.data_restriction_final[key][-1])]


                            lower_border = round(st.number_input("Select lower border",
                                value=float(st.session_state.data_restriction_final[key][0]),
                                min_value=float(st.session_state.data_restriction_final[key][0]),
                                max_value=float(st.session_state.data_restriction_final[key][-1]),
                                key=f"lower_border_range_perturbation_{key}"),2)

                            upper_border = round(st.number_input("Select upper border",
                                value=float(st.session_state.data_restriction_final[key][-1]),
                                                                 min_value=lower_border,
                                max_value=float(st.session_state.data_restriction_final[key][-1]),
                                key=f"upper_border_range_perturbation_{key}"),2)


                            if st.session_state[f"lower_border_range_perturbation_{key}"] \
                                    >= st.session_state[f"upper_border_range_perturbation_{key}"]:
                                st.error("Lower bound range must be smaller than upper bound.")
                                st.stop()
                            else:
                                st.session_state[f"additional_value_{key}_{method}_bound"] = \
                                    [float(lower_border),float(upper_border)]



                            if st.session_state[f"steps_{key}_{method}"] == 0:
                                st.session_state[f"steps_{key}_{method}"] = 1

                            st.session_state[f"steps_{key}_{method}"] = int(st.number_input("Steps",
                                    min_value=int(1),
                                    step=int(1),
                                    value=st.session_state[f"steps_{key}_{method}"],
                                    key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                    args=(key, method)))

                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                "Select Perturbation Level",
                                options=options_perturbation_level,
                                index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help="Determines whether the prediction with this perturbation option is allowed to change: "
                                     "Red means thet the prediction for that perturbation option should not change. "
                                     "Orange means that prediction might change. Green means that prediction is expected to change",
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                perturbRange_settings(st.session_state[f"additional_value_{key}_{method}_bound"][0],
                                                      st.session_state[f"additional_value_{key}_{method}_bound"][1],
                                                      st.session_state[f"steps_{key}_{method}"]))
                            perturbationLevel_list[method] =  st.session_state[
                                                                     f"assignedPerturbationLevel_{key}_{method}"]

                            st.write("---------------")


                        elif method == 'Bin Perturbation':
                            st.markdown(f"##### Define settings for algorithm: {method}")
                            try:
                                if key not in st.session_state.loaded_bin_dict:
                                    st.warning("Bin is not determined in Data Understanding Step")

                                    st.write(st.session_state.loaded_bin_dict[key])

                                else:

                                    st.write([[st.session_state.loaded_bin_dict[key][i],
                                               st.session_state.loaded_bin_dict[key][i + 1]] for i in
                                              range(len(st.session_state.loaded_bin_dict[key]) - 1)])

                                    st.session_state[f"steps_{key}_{method}"] = int(
                                        st.number_input("Steps",  min_value=int(1), step=int(1),
                                                        value=st.session_state[f"steps_{key}_{method}"],
                                                        key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                                        args=(key, method)))



                                    st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                        "Select Perturbation Level",
                                        options=options_perturbation_level,
                                        index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                        help="Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change",
                                        key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                        on_change=update_perturbation_level,
                                        args=(key, method))

                                    settingList[method] = (
                                        perturbBin_settings(st.session_state[f"steps_{key}_{method}"]))
                                    perturbationLevel_list[method] = st.session_state[
                                        f"assignedPerturbationLevel_{key}_{method}"]

                                    st.write("---------------")
                            except Exception as e:
                                st.write(
                                    "Binning for this feature should be determined in Data Preparation step.")


                if settingList:
                    settings[key] = settingList
                if perturbationLevel_list:
                    perturbationLevel[key] = perturbationLevel_list
            st.session_state['settings'] = settings
            st.session_state['perturbationLevel'] = perturbationLevel


        with tab2:

            # check if algorithm for level of scale is chosen
            is_empty = True
            for values in st.session_state['ordinal_val'].values():
                if values:
                    is_empty = False

            if is_empty:
                st.info("No Algorithm for ordinal feature chosen")

            for key, values in st.session_state['ordinal_val'].items():
                # if "settingList" not in st.session_state:
                #     st.session_state.settingList = dict()
                settingList = dict()
                perturbationLevel_list = dict()

                with st.expander(f"Settings for column {key}"):
                    try:
                        if values:
                            query = f"""SELECT ?featureID ?featureName ?rprov ?DataUnderstandingEntityID ?label ?DUA WHERE{{
                                                    ?featureID rdf:type rprov:Feature .
                                                     ?featureID rdfs:label '{key}'.
                                                     ?DataUnderstandingEntityID rprov:toFeature ?featureID.
                                                    ?DataUnderstandingEntityID rdf:type ?rprov.
                                                     ?DataUnderstandingEntityID rprov:wasGeneratedByDUA|rprov:wasGeneratedByDPA|rprov:wasGeneratedByBUA ?DUA.
                             ?DataUnderstandingEntityID rdfs:label ?label.
                                                     FILTER(?rprov!=owl:NamedIndividual)

                                                     FILTER(?rprov!=rprov:ScaleOfFeature)  
                                                     FILTER(?rprov!=rprov:SensorPrecisionOfFeature)  
                                                     FILTER(?rprov!=rprov:RangeOfBinnedFeature)
                                                     FILTER(?rprov!=rprov:UniqueValuesOfFeature)
                                                     FILTER NOT EXISTS{{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}}

                             }}"""

                            try:
                                results_update = get_connection_fuseki(host, (prefix + query))
                                # get Activities for PerturbationOption
                                result_2 = pd.json_normalize(results_update["results"]["bindings"])
                                entities_selection = result_2["label.value"].tolist()

                                if len(entities_selection) > 0:
                                    entities = st.multiselect(
                                        label="Select entities which should be included in the perturbation option",
                                        options=entities_selection, default=entities_selection)

                            except:
                                entities = []
                                st.info("No Level of volatility, Data Restrictions or missing values determined")

                            query = f"""SELECT ?featureID ?featureName ?rprov ?DataUnderstandingEntityID ?label ?DUA WHERE{{
                                                                            ?featureID rdf:type rprov:Feature .
                                                                             ?featureID rdfs:label '{key}'.
                                                                             ?DataUnderstandingEntityID rprov:toFeature ?featureID.
                                                                             ?DataUnderstandingEntityID rdf:type ?rprov.
                                                                             ?DataUnderstandingEntityID rprov:wasGeneratedByDUA|rprov:wasGeneratedByDPA|rprov:wasGeneratedByBUA ?DUA.
                                                                             ?DataUnderstandingEntityID rdfs:label ?label.
                                                                             FILTER(?rprov!=owl:NamedIndividual)
                                                                             FILTER(?rprov!=rprov:SensorPrecisionOfFeature)  
                                                                             FILTER(?rprov!=rprov:RangeOfBinnedFeature)
                                                                             FILTER(?rprov!=rprov:UniqueValuesOfFeature)
                                                                             FILTER NOT EXISTS{{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}}

                                                     }}"""

                            try:
                                results_update = get_connection_fuseki(host, (prefix + query))

                                # get Activities for PerturbationOption
                                result_2 = pd.json_normalize(results_update["results"]["bindings"])
                                entities.append(result_2["label.value"][0])
                            except:
                                pass

                            st.session_state["entities"][key] = (result_2[result_2['label.value'].isin(entities)])[
                                "DataUnderstandingEntityID.value"].tolist()
                            st.write(result_2[result_2['label.value'].isin(entities)])

                            flag = False

                            for value in entities:
                                if value.startswith("restriction"):
                                    flag = True

                            if flag == True:
                                st.session_state.data_restriction_final[key] = st.session_state.data_restrictions_dict[
                                    key]

                            else:
                                st.session_state.data_restriction_final[key] = (
                                st.session_state.unique_values_dict[key])
                    except Exception as e:
                        st.error(e)
                    for method in values:
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

                            if len(st.session_state.data_restriction_final[key]) ==2:
                                st.session_state[f"steps_{key}_{method}"] = 2
                            else:
                                st.session_state[f"steps_{key}_{method}"] = int(
                                    st.number_input("Steps",
                                                    min_value=int(1), step=int(1),
                                                    value=st.session_state[f"steps_{key}_{method}"],
                                                    key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                                    args=(key, method)))


                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                "Select Perturbation Level",
                                options=options_perturbation_level,
                                index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help="Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change",
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                perturbInOrder_settings(st.session_state[f"steps_{key}_{method}"]))
                            perturbationLevel_list[method] = st.session_state[
                                f"assignedPerturbationLevel_{key}_{method}"]

                            st.write("---------------")

                        if method == "Perturb all values":
                            st.markdown(f"##### Define settings for algorithm: {method}")
                            with st.expander("Show all values:"):
                                st.session_state.data_restriction_final[key]

                            with st.expander("Show all values:"):
                                st.session_state.data_restriction_final[key]

                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                "Select Perturbation Level",
                                options=options_perturbation_level,
                                index=options_perturbation_level.index(st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help="Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change",
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                perturbAllValues_settings())  # st.session_state[f"value_perturbate{key}_{method}"],
                            perturbationLevel_list[method] = st.session_state[
                                f"assignedPerturbationLevel_{key}_{method}"]


                            st.write("---------------")

                if settingList:
                    settings[key] = settingList
                if perturbationLevel_list:
                    perturbationLevel[key] = perturbationLevel_list
            st.session_state['settings'] = settings
            st.session_state['perturbationLevel'] = perturbationLevel


        with tab3:
            # check if algorithm for level of scale is chosen
            is_empty = True
            for values in st.session_state['nominal_val'].values():
                if values:
                    is_empty = False

            if is_empty:
                st.info("No Algorithm for nominal feature chosen")

            for key, values in st.session_state['nominal_val'].items():
                if "settingList" not in st.session_state:
                    st.session_state.settingList = dict()
                settingList = dict()
                perturbationLevel_list = dict()

                with st.expander(f"Settings for column {key}"):
                    try:

                        if values:
                            query = f"""SELECT ?featureID ?featureName ?rprov ?DataUnderstandingEntityID ?label ?DUA WHERE{{
                                                     ?featureID rdf:type rprov:Feature .
                                                     ?featureID rdfs:label '{key}'.
                                                     ?DataUnderstandingEntityID rprov:toFeature ?featureID.
                                                     ?DataUnderstandingEntityID rdf:type ?rprov.
                                                     ?DataUnderstandingEntityID rprov:wasGeneratedByDUA|rprov:wasGeneratedByDPA|rprov:wasGeneratedByBUA ?DUA.
                                                     ?DataUnderstandingEntityID rdfs:label ?label.
                                                     FILTER(?rprov!=owl:NamedIndividual)

                                                     FILTER(?rprov!=rprov:ScaleOfFeature)  
                                                     FILTER(?rprov!=rprov:SensorPrecisionOfFeature)  
                                                     FILTER(?rprov!=rprov:RangeOfBinnedFeature)
                                                     FILTER(?rprov!=rprov:UniqueValuesOfFeature)
                                                     FILTER NOT EXISTS{{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}}

                             }}"""

                            try:
                                results_update = get_connection_fuseki(host, (prefix + query))

                                # get Activities for PerturbationOption
                                result_2 = pd.json_normalize(results_update["results"]["bindings"])
                                entities_selection = result_2["label.value"].tolist()

                                if len(entities_selection) > 0:
                                    entities = st.multiselect(
                                        label="Select entities which should be included in the perturbation option",
                                        options=entities_selection, default=entities_selection)

                            except:
                                entities = []
                                st.info("No Level of volatility, Data Restrictions or missing values determined")

                            query = f"""SELECT ?featureID ?featureName ?rprov ?DataUnderstandingEntityID ?label ?DUA WHERE{{
                                                                            ?featureID rdf:type rprov:Feature .
                                                                             ?featureID rdfs:label '{key}'.
                                                                             ?DataUnderstandingEntityID rprov:toFeature ?featureID.
                                                                             ?DataUnderstandingEntityID rdf:type ?rprov.
                                                                             ?DataUnderstandingEntityID rprov:wasGeneratedByDUA|rprov:wasGeneratedByDPA|rprov:wasGeneratedByBUA ?DUA.
                                                                             ?DataUnderstandingEntityID rdfs:label ?label.
                                                                             FILTER(?rprov!=owl:NamedIndividual)
                                                                             FILTER(?rprov!=rprov:SensorPrecisionOfFeature)  
                                                                             FILTER(?rprov!=rprov:RangeOfBinnedFeature)
                                                                             FILTER(?rprov!=rprov:UniqueValuesOfFeature)
                                                                             FILTER NOT EXISTS{{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}}

                                                     }}"""

                            try:
                                results_update = get_connection_fuseki(host, (prefix + query))

                                # get Activities for PerturbationOption
                                result_2 = pd.json_normalize(results_update["results"]["bindings"])
                                entities.append(result_2["label.value"][0])
                            except:
                                pass

                            st.session_state["entities"][key] = (result_2[result_2['label.value'].isin(entities)])[
                                "DataUnderstandingEntityID.value"].tolist()
                            st.write(result_2[result_2['label.value'].isin(entities)])

                            flag = False

                            for value in entities:
                                if value.startswith("restriction"):
                                    flag = True

                            if flag == True:
                                st.session_state.data_restriction_final[key] = st.session_state.data_restrictions_dict[
                                    key]

                            else:
                                st.session_state.data_restriction_final[key] = (
                                st.session_state.unique_values_dict[key])
                    except:
                        pass

                    for method in values:
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
                                perturbAllValues_settings())
                            perturbationLevel_list[method] = st.session_state[
                                f"assignedPerturbationLevel_{key}_{method}"]
                            st.write("---------------")

                if settingList:
                    settings[key] = settingList
                if perturbationLevel_list:
                    perturbationLevel[key] = perturbationLevel_list
            st.session_state['settings'] = settings
            st.session_state['perturbationLevel'] = perturbationLevel


        if st.session_state['settings'] != {}:
            st.write("-------")
            with st.expander("Show Perturbation Setting"):
                st.write(st.session_state['settings'])

            with st.form("Insert label for the defined Perturbation Options"):
                st.info("This label be shown in the options for the Deployment. Therefore it is advised to add as much information as possible.")
                labelPerturbation = st.text_input("Insert label for the defined Perturbation Options",
                                                  help="Name your Perturbation Option in order to find it easier later.")

                if st.form_submit_button("Upload Perturbation Option", type ="primary"):
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

                    try:
                        getApproach(host)
                    except Exception as e:
                        uuid_activity = uuid.uuid4()
                        uuid_entity = uuid.uuid4()
                        uploadApproach(host_upload, uuid_activity, uuid_entity)
                else:
                    st.stop()

                # Modeling Phase

                # KG label nötig? Um die PerturbationOption zu identifizieren?

                # First create ModelingActivity
                label = "Definition of Perturbation Option"
                determinationNameUUID = 'DefinitionOfPerturbationOption'
                determinationName = 'DefinitionOfPerturbationOption'
                name = 'PerturbationOption'
                rprovName = 'PerturbationOption'

                # Get BUE PerturbationApproach
                business_understanding_entity = getApproach(host)

                # TODO ausgliedern
                try:
                    ending_time = getTimestamp()
                    uuid_DefinitionOfPerturbationOption = determinationActivity(host_upload, determinationName,
                                                                                label,
                                                                                ending_time)


                    # if feature is in perturbation settings
                    # create list with activities an loop in order to insert them as modelingEntityWasDerivedFrom

                    for key in st.session_state['settings']:
                        featureID = st.session_state.DF_feature_scale_name[
                            st.session_state.DF_feature_scale_name["featureName.value"] == key]



                        # create another loop in order to get different UUIDs for PerturbationOptions
                        # KG sollen die einzelnen Optionen einzeln oder gesammelt gespeichert werden
                        for method, perturbationOption in st.session_state['settings'][key].items():

                            uuid_PerturbationOption = uuid.uuid4()
                            liste_entities = st.session_state["entities"][key].copy()

                            if method == "Bin Perturbation":
                                bin_entity = \
                                st.session_state.DF_bin_dict[st.session_state.DF_bin_dict["label.value"] == key][
                                    "DPE.value"].reset_index(drop=True)
                                liste_entities.append(bin_entity[0])

                            if method == "Sensor Precision Perturbation":
                                sensor_precision = st.session_state.DF_feature_sensor_precision[
                                    st.session_state.DF_feature_sensor_precision["featureName.value"] == key][
                                    "DataUnderstandingEntityID.value"].reset_index(drop=True)
                                liste_entities.append(sensor_precision[0])

                            # get dataunderstandingentity for sensor precision and if perturbation option contains sensor precision insert into list
                            # create new dataunderstandingentity if sensor precision is different?
                            # update dataunderstandingentity if sensor precision is different?



                            for entities in liste_entities:
                                perturbationOptionlabel = str(perturbationOption)

                                perturbationOptionlabel = perturbationOptionlabel.replace("'", "").replace("{",
                                                                                                           "").replace(
                                    "}", "")


                                query = (f"""INSERT DATA {{<urn:uuid:{uuid_PerturbationOption}> rdf:type rprov:{name}, owl:NamedIndividual;
                                                      rprov:perturbedFeature <{featureID["featureID.value"].values[0]}>;
                                                      rprov:generationAlgorithm "{method}";
                                                      rprov:assignedPerturbationSettings "{perturbationOption}";
                                                      rprov:assignedPerturbationLevel "{st.session_state['perturbationLevel'][key][method]}";
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
