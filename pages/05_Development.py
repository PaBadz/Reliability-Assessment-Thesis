import stat

import pandas as pd
import streamlit
from st_draggable_list import DraggableList

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode
from functions.perturbation_algorithms_ohne_values import *
from functions.functions_Reliability import *

try:
    host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
    host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
except:
    st.info("Please select a database first")
    st.stop()
# ------------------------------------------------------------------------------------------------------------------------


getDefault(host)
getAttributes(host)


if "data_restrictions_dict" not in st.session_state:
    st.session_state["data_restrictions_dict"] = dict()

# horizontal menu
selected2 = option_menu(None, ["Choose Algorithms", "Define Perturbation Options"],
                        icons=['house', 'gear'],
                        orientation="horizontal")

options_cardinal = ['5% perturbation', '10% perturbation','Percentage perturbation',  'Sensor Precision', 'Fixed amount', 'Range perturbation']
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


                            elif st.session_state.volatility_of_features_dic[columns] == 'Medium Volatility':
                                st.info("Feature has medium volatility!")
                        except:
                            st.info("No level of volatility determined")
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
                            try:
                                if "Sensor Precision" in st.session_state.cardinal_val[columns]:
                                    if columns not in st.session_state.loaded_feature_sensor_precision_dict.keys():
                                        st.error(f"No Sensor Precision for {columns} in Data Understanding step determined. ")
                                        st.info("Go to Data Understanding and determine sensor precision for this feature.")
                                        st.session_state.loaded_feature_sensor_precision_dict[columns]
                            except:
                                pass


                        except Exception as e:
                            st.write(e)
                            st.info('No Cardinal Values', icon="ℹ️")

            if level == "Ordinal":
                settingList = dict()
                with tab2:
                    with st.expander(label=f"Algorithms for ***{columns}***"):
                        try:
                            if st.session_state.volatility_of_features_dic[columns] == 'High Volatility':
                                st.warning("Feature has high volatility!")
                                st.info(
                                    "Switch to perturbation Recommendations to see which algorithms were used in the past.")
                            elif st.session_state.volatility_of_features_dic[columns] == 'Medium Volatility':
                                st.info("Feature has medium volatility!")
                        except:
                            st.info("No level of volatility determined")

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
                            elif st.session_state.volatility_of_features_dic[columns] == 'Medium Volatility':
                                st.info("Feature has medium volatility!")
                        except:
                            st.info("No level of volatility determined")

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

        st.write(st.session_state["loaded_feature_sensor_precision_dict"])
        st.write(st.session_state["DF_feature_sensor_precision"])

        try:
            uploaded_DataRestriction = getRestriction(host)
            if "flag_data_restriction" not in st.session_state:
                st.session_state.flag_data_restriction = False
                st.session_state.data_restriction_URN = pd.DataFrame(columns=uploaded_DataRestriction.columns)
            if st.session_state.data_restriction_URN.empty:
                st.info("No Data Restriction selected")
            else:
                st.success("Data Restriction option selected")




            with st.expander("Show selected Data Restriction:"):
                colored_header(
                    label="Data Restriction",
                    description="",
                    color_name="red-50",
                )
                st.dataframe(st.session_state.data_restriction_URN[["Feature", "Value"]], use_container_width=True)

            try:

                options_data_restriction = uploaded_DataRestriction["DataRestrictionActivity"].unique().tolist()
                data_restriction = st.selectbox("Select Data Restriction", options=options_data_restriction)


                selected_DataRestriction = uploaded_DataRestriction.loc[uploaded_DataRestriction["DataRestrictionActivity"] == data_restriction]


                st.dataframe(selected_DataRestriction[["Feature", "Value"]], use_container_width=True)



                if st.button("Get Restriction", type='primary'):

                    st.session_state.data_restriction_URN = selected_DataRestriction

                    try:
                        for key, value in st.session_state["level_of_measurement_dic"].items():
                            if value == "Cardinal":
                                defaultValuesCardinalRestriction(key)
                            if value == "Ordinal":
                                defaultValuesOrdinalRestriction(key)
                            if value == "Nominal":
                                defaultValuesNominalRestriction(key)
                        st.session_state["data_restrictions_dict"] = getDataRestrictionSeq(data_restriction, host)
                        st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()

                        st.session_state.data_restriction_final.update(st.session_state.data_restrictions_dict)
                        st.session_state["flag_data_restriction"] = True

                        st.experimental_rerun()






                    except Exception as e:
                        st.write(e)
                        st.info("Dont forget to upload unique values")


                if st.button("Deselect Restriction"):
                    try:
                        st.session_state["data_restrictions_dict"] = getUniqueValuesSeq(host)
                        st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()
                        st.session_state.data_restriction_final.update(st.session_state.data_restrictions_dict)
                        st.session_state["flag_data_restriction"] = False
                        st.session_state.data_restriction_URN = pd.DataFrame(columns=uploaded_DataRestriction.columns)
                        st.experimental_rerun()
                    except Exception as e:
                        st.write(e)
                        st.write("Didnt work")



            except Exception as e:
                st.write(e)


        except Exception as e:
            st.error(e)
            st.info("No Data Restrictions available.")
            st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()
            st.session_state.data_restriction_URN = pd.DataFrame(columns=['DataRestrictionActivity', 'DataRestrictionEntity', 'Label', 'Feature', 'Value'])

# Define Algorithmns



try:
    if selected2 == 'Define Perturbation Options':




        if "perturbed_value_list" not in st.session_state:
            st.session_state.perturbed_value_list = {}
            for columns in st.session_state.dataframe_feature_names["featureName.value"]:
                st.session_state.perturbed_value_list[columns] = []

        tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])
        settings = dict()
        perturbed_value_list = dict()
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
                if "perturbedList" not in st.session_state:
                    st.session_state.perturbedList = dict()
                perturbedList = dict()

                with st.expander(f"Settings for feature {key}"):

                    for method in value:
                        if f"steps_{key}_{method}" not in st.session_state:
                            st.session_state[f"steps_{key}_{method}"] = 1

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
                                st.session_state[f"additional_value_{key}_{method}"] = st.session_state.data_restriction_final[key][0]
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
                                          value=st.session_state[f"steps_{key}_{method}"],
                                          key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                          args=(key, method)))

                            settingList[method] = (
                                percentage_perturbation_settings(st.session_state[f"steps_{key}_{method}"]))
                            st.write("---------------")

                        if method == "5% perturbation":
                            st.markdown(f"##### {method}")
                            settingList[method] = (
                                percentage_perturbation_settings(5))
                            st.write("---------------")

                        if method == "10% perturbation":
                            st.markdown(f"##### {method}")

                            settingList[method] = (
                                percentage_perturbation_settings(10))
                            st.write("---------------")




                        elif method == 'Sensor Precision':
                            try:
                                if key not in st.session_state.loaded_feature_sensor_precision_dict:
                                    st.warning("Sensor Precision is not determined in Data Understanding Step")
                                    st.info("When sensor precision is changed, old entity will be invalid and new one is created.")
                                    # set precision to 0
                                    # raise error
                                    st.session_state.loaded_feature_sensor_precision_dict[key]
                                    # st.session_state[f"additional_value_{key}_{method}"] = 0.01
                                else:
                                    st.session_state[f"additional_value_{key}_{method}"] = \
                                    st.session_state.loaded_feature_sensor_precision_dict[key]

                                st.markdown(f"##### {method}")
                                # step = st.number_input("Define stepsize", min_value=0.01, max_value=float(
                                #     st.session_state.unique_values_dict[key][-1]), step=0.01,
                                #                        key=f"step_sensor_precision_{key}")

                                st.session_state[f"steps_{key}_{method}"] = int(
                                    st.number_input("Steps", min_value=int(1), step=int(1),
                                              value=int(st.session_state[f"steps_{key}_{method}"]),
                                              key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                              args=(key, method)))

                                # st.session_state[f"additional_value_{key}_{method}"] = round(float(
                                #     st.number_input("Sensor Precision", min_value=float(0.01), max_value=float(100),
                                #               value=float(st.session_state[f"additional_value_{key}_{method}"]),
                                #               key=f"additional_value_widget_{key}_{method}",#step=float(step)
                                #               on_change=update_additional_value, args=(key, method))),2)

                                st.write(f"Sensor Precision: **{st.session_state.loaded_feature_sensor_precision_dict[key]}**")

                                # st.session_state[f"steps_{key}_{method}"] = int(
                                #     st.number_input("Steps", min_value=int(1), step=int(1),
                                #               value=int(st.session_state[f"steps_{key}_{method}"]),
                                #               key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                #               args=(key, method)))

                                settingList[method] = (sensorPrecision_settings(st.session_state[f"additional_value_{key}_{method}"],
                                                         st.session_state[f"steps_{key}_{method}"]))
                            except Exception as e:
                                st.write(e)
                                st.error(f"No Sensor Precision for {key} in Data Understanding step determined. ")
                                st.info("Go to Data Understanding and determine sensor precision for this feature.")
                                want_to_contribute = st.button("Data Understanding")
                                if want_to_contribute:
                                    switch_page("Data Understanding")

                            st.write("---------------")

                        elif method == 'Fixed amount':
                            st.markdown(f"##### Define settings for algorithm: {method}")
                            st.session_state[f"additional_value_{key}_{method}"] =  float(st.number_input("Amount",value=float(st.session_state[f"additional_value_{key}_{method}"]),min_value=float(
                                    st.session_state.data_restriction_final[key][0]), max_value=float(
                                    st.session_state.data_restriction_final[key][1]),
                                          key=f"additional_value_widget_{key}_{method}",
                                          on_change=update_additional_value,
                                          args=(key, method)))
                            #float(
                                # st.slider("Amount", min_value=float(
                                #     st.session_state.data_restriction_final[key][0]), max_value=float(
                                #     st.session_state.data_restriction_final[key][1]), step=float(1),
                                #           value=st.session_state[f"additional_value_{key}_{method}"],
                                #           key=f"additional_value_widget_{key}_{method}",
                                #           on_change=update_additional_value,
                                #           args=(key, method)))

                            st.session_state[f"steps_{key}_{method}"] = int(
                                st.number_input("Steps", #min_value=int(1), max_value=int(100), step=int(1),
                                          value=st.session_state[f"steps_{key}_{method}"],
                                          key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                          args=(key, method)))

                            settingList[method] = (
                                fixedAmountSteps_settings(st.session_state[f"additional_value_{key}_{method}"],
                                                          st.session_state[f"steps_{key}_{method}"]))

                            st.write("---------------")

                        elif method == 'Range perturbation':
                            st.markdown(f"##### Define settings for algorithm: {method}")

                            if f"additional_value_{key}_{method}_bound" not in st.session_state:
                                st.session_state[f"additional_value_{key}_{method}_bound"] = [
                                    float(st.session_state.data_restriction_final[key][0]),
                                    float(st.session_state.data_restriction_final[key][-1])]

                            with st.form(f"Input values {key}"):
                                lower = st.number_input("Input value", )
                                upper = st.number_input("Input upper value",max_value=float(
                                    st.session_state.data_restriction_final[key][-1]))
                                if st.form_submit_button("Upload"):
                                    st.session_state[f"additional_value_{key}_{method}_bound"] = [float(lower),
                                                                                                  float(upper)]

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
                                st.number_input("Steps", step = int(1),#min_value=int(1), max_value=int(100), step=int(1),
                                          value=st.session_state[f"steps_{key}_{method}"],
                                          key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                          args=(key, method)))

                            settingList[method] = (
                                perturbRange_settings(st.session_state[f"additional_value_{key}_{method}_bound"][0],
                                                      st.session_state[f"additional_value_{key}_{method}_bound"][1],
                                                      st.session_state[f"steps_{key}_{method}"]))
                            perturbedList[method] = (
                                perturbRange(st.session_state[f"additional_value_{key}_{method}_bound"][0],
                                             st.session_state[f"additional_value_{key}_{method}_bound"][1],
                                             st.session_state[f"steps_{key}_{method}"]))
                            st.write("---------------")
                            st.write("---------------")

                if settingList:
                    settings[key] = settingList
                if perturbedList:
                    perturbed_value_list[key] = perturbedList
            st.session_state['settings'] = settings
            st.session_state['perturbed_value_list'] = perturbed_value_list

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
                if "perturbedList" not in st.session_state:
                    st.session_state.perturbedList = dict()
                perturbedList = dict()

                with st.expander(f"Einstellungen für column {key}"):
                    for method in value:
                        if f"steps_{key}_{method}" not in st.session_state:
                            st.session_state[f"steps_{key}_{method}"] = 0
                        if f"value_perturbate{key}_{method}" not in st.session_state:
                            st.session_state[f"value_perturbate{key}_{method}"] = \
                                st.session_state.data_restriction_final[key][0]
                        if f"additional_value_{key}_{method}" not in st.session_state:
                            st.session_state[f"additional_value_{key}_{method}"] = 0

                        if method == "Perturb in order":
                            st.session_state[f"steps_{key}_{method}"] = int(
                                st.slider("Steps", min_value=int(1),
                                          max_value=int(len(st.session_state.data_restriction_final[key]) - 1),
                                          step=int(1),
                                          value=st.session_state[f"steps_{key}_{method}"],
                                          key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                          args=(key, method)))

                            settingList[method] = (
                                perturbInOrder_settings(st.session_state[f"steps_{key}_{method}"]))#,st.session_state.data_restriction_final[key]

                            st.write("---------------")

                        if method == "Perturb all values":
                            st.write("All unique values will be perturbed")
                            st.session_state[f"value_perturbate{key}_{method}"] = (
                                st.select_slider(f'{key}', options=
                                st.session_state.data_restriction_final[key], value=st.session_state[
                                    f"value_perturbate{key}_{method}"],

                                                 help="Wähle den zu perturbierenden Wert aus",
                                                 key=f"value_perturbation_widget_{key}_{method}",
                                                 on_change=update_value_perturbate,
                                                 args=(key, method)))
                            settingList[method] = (
                                perturbAllValues_settings(st.session_state[f"value_perturbate{key}_{method}"]))#,st.session_state.data_restriction_final[key]))

                            perturbedList[method] = (
                                perturbAllValues(st.session_state[f"value_perturbate{key}_{method}"],
                                                 st.session_state.data_restriction_final[key]))
                            st.write("---------------")

                    if settingList:
                        settings[key] = settingList
                    if perturbedList:
                        perturbed_value_list[key] = perturbedList
                st.session_state['settings'] = settings
                st.session_state['perturbed_value_list'] = perturbed_value_list

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
                if "perturbedList" not in st.session_state:
                    st.session_state.perturbedList = dict()
                perturbedList = dict()

                with st.expander(f"Einstellungen für column {key}"):
                    for method in value:
                        if f"steps_{key}_{method}" not in st.session_state:
                            st.session_state[f"steps_{key}_{method}"] = 0
                        if f"value_perturbate{key}_{method}" not in st.session_state:
                            st.session_state[f"value_perturbate{key}_{method}"] = \
                                st.session_state.data_restriction_final[key][0]
                        if f"additional_value_{key}_{method}" not in st.session_state:
                            st.session_state[f"additional_value_{key}_{method}"] = 0

                        if method == "Perturb all values":
                            st.write("All unique values will be perturbed")
                            st.write(st.session_state.data_restriction_final[key])
                            st.session_state[f"value_perturbate{key}_{method}"] = (
                                st.select_slider(f'{key}', options=
                                st.session_state.data_restriction_final[key], value=st.session_state[
                                    f"value_perturbate{key}_{method}"],

                                                 help="Wähle den zu perturbierenden Wert aus",
                                                 key=f"value_perturbation_widget_{key}_{method}",
                                                 on_change=update_value_perturbate,
                                                 args=(key, method)))
                            settingList[method] = (
                                perturbAllValues_settings(st.session_state.data_restriction_final[key]))#st.session_state[f"value_perturbate{key}_{method}"]))#,st.session_state.data_restriction_final[key]))

                            st.write("---------------")

                    if settingList:
                        settings[key] = settingList
                    if perturbedList:
                        perturbed_value_list[key] = perturbedList
                st.session_state['settings'] = settings
                st.session_state['perturbed_value_list'] = perturbed_value_list

        if st.session_state['settings']!={}:
            with st.expander("Show Perturbation Setting"):
                st.write(st.session_state['settings'])




                #todo ausgliedern
                # kann auch implementiert werden bei predict --> dadurch verpflichtend

            if st.session_state.data_restriction_URN["DataRestrictionEntity"].empty:
                st.info("No Data Restriction selected")
            else:
                st.write(st.session_state.data_restriction_URN["DataRestrictionEntity"])


            labelPerturbation = st.text_input("Insert additional label for the defined Perturbation Options",help="This is optional. Name your Perturbation Option in order to find it easier later. Ever Perturbation Option should be uniquely named")
            if st.button("Save Modeling Activity to Database", type='primary', help="Modeling Activity + Generation of Perturbation Option with BUA, DUA, DPA as input and Perturbation Option. Save the Modeling Activity and Entity to the Database. Later this button will be replaced and done automatically."):
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
                ending_time = getTimestamp()

                try:
                    # st.write(st.session_state["flag_data_restriction"])
                    # if st.session_state["flag_data_restriction"] == False:
                    #
                    #     query = (f"""
                    #          SELECT ?featureID ?featureName ?DataUnderstandingEntityID ?DUA {{
                    #             ?featureID rdf:type rprov:Feature .
                    #             ?featureID rdfs:label ?featureName.
                    #             ?DataUnderstandingEntityID rprov:toFeature ?featureID.
                    #             ?DataUnderstandingEntityID rprov:wasGeneratedByDUA ?DUA.
                    #              FILTER(?rprov!=rprov:SensorPrecisionOfFeature)}}""")
                    #
                    # else:

                    # query = (f"""
                    #                                   SELECT ?featureID ?featureName ?rprov ?DataUnderstandingEntityID ?DUA WHERE{{
                    #         ?featureID rdf:type rprov:Feature .
                    #         ?featureID rdfs:label ?featureName.
                    #         ?DataUnderstandingEntityID rprov:toFeature ?featureID.
    				# 		?DataUnderstandingEntityID rdf:type ?rprov.
                    #         ?DataUnderstandingEntityID rprov:wasGeneratedByDUA ?DUA.
                    #
                    #         FILTER(      ?rprov!=owl:NamedIndividual)
                    #         FILTER(?rprov!=rprov:DataRestriction)
                    #         FILTER(?rprov!=rprov:SensorPrecisionOfFeature)""")

                    query = (f"""SELECT ?featureID ?featureName ?rprov ?DataUnderstandingEntityID ?DUA WHERE{{
    			?featureID rdf:type rprov:Feature .
                            ?featureID rdfs:label ?featureName.
                            ?DataUnderstandingEntityID rprov:toFeature ?featureID.
    						?DataUnderstandingEntityID rdf:type ?rprov.
                            ?DataUnderstandingEntityID rprov:wasGeneratedByDUA|rprov:wasGeneratedByDPA ?DUA.
                        
                          FILTER(      ?rprov!=owl:NamedIndividual)
                            FILTER(?rprov!=rprov:DataRestriction)
    FILTER(?rprov!=rprov:SensorPrecisionOfFeature)  
    
    }}""")


                    results_update = get_connection_fuseki(host, (prefix+query))
                    # get Activities for PerturbationOption
                    result_2 = pd.json_normalize(results_update["results"]["bindings"])
                    result_2 = result_2.groupby(["featureID.value", "featureName.value"], as_index=False)[
                        "DataUnderstandingEntityID.value"].agg(list)




                    #for key in st.session_state['settings']:
                        # TODO Decide whether PerturbationOption is generated for each feature or all together
                        # upload ModelingActivity to fueski


                        ####################################################################################################

                    uuid_DefinitionOfPerturbationOption = determinationDUA(host_upload, determinationName,
                                                                           label,
                                                                           starting_time, ending_time)
                        ####################################################################################################



                    # if feature is in perturbation settings
                    # create list with activities an loop in order to insert them as modelingEntityWasDerivedFrom

                    for key in st.session_state['settings']:
                        if key in result_2["featureName.value"].values:
                            uploaded_entities = (result_2[result_2["featureName.value"] == key])
                            # TODO delete data restcition if not chosen


                            liste = (uploaded_entities["DataUnderstandingEntityID.value"].values).tolist()



                            # insert URN if flag is true and also look if feature is in data restrictions
                            try:
                                if key in st.session_state.data_restriction_URN["Feature"].values:

                                    data_restriction = st.session_state.data_restriction_URN[st.session_state.data_restriction_URN["Feature"] == key]["DataRestrictionEntity"].reset_index(drop=True)
                                    liste[0].append(data_restriction[0])
                            except Exception as e:
                                st.write(e)
                            try:
                                # check if algorithm is "Sensor Precision" and then check if there is an entry in the database with SensorPrecision for this feature, if so then check if the values are the same
                                # if values are the same, append dataunderstandingentity into liste and proceed
                                # if values are different, throw error and  write info that precision level is different to saved one
                                # right now dataunderstandingentity will not be generated
                                for perturbationOption in st.session_state['cardinal_val'][key]:

                                    if perturbationOption == "Sensor Precision":

                                        if key in st.session_state.DF_feature_sensor_precision["featureName.value"].values:

                                            data_precision = st.session_state.DF_feature_sensor_precision[(
                                                st.session_state.DF_feature_sensor_precision["featureName.value"] == key)&(
                                                st.session_state.loaded_feature_sensor_precision_dict[key] == round(st.session_state.settings[key]["Sensor Precision"]["sensorPrecision"],2))][
                                                "DataUnderstandingEntityID.value"].reset_index(drop=True)
                                            liste[0].append(data_precision[0])
                            except Exception as e:

                               st.info(f"Different precision level for feature {key}. Right now this will not lead to creation of data understanding entity for sensor precision")

                            # create another loop in order to get different UUIDs for PerturbationOptions
                            #KG sollen die einzelnen Optionen einzeln oder gesammelt gespeichert werden
                            for method, perturbationOption in st.session_state['settings'][key].items():
                                uuid_PerturbationOption = uuid.uuid4()













                                # get dataunderstandingentity for sensor precision and if perturbation option contains sensor precision insert into list
                                # create new dataunderstandingentity if sensor precision is different?
                                # update dataunderstandingentity if sensor precision is different?



                                for entities in liste:


                                    # Entities werden hier ausgegeben
                                    for entity in entities:


                                        perturbationOptionlabel = str(perturbationOption)

                                        perturbationOptionlabel = perturbationOptionlabel.replace("'","").replace("{","").replace("}","")


                                        if method == "Perturb all values":
                                            query = (
                                                f"""INSERT DATA {{<urn:uuid:{uuid_PerturbationOption}> rdf:type rprov:{name}, owl:NamedIndividual;
                                                                                                         rprov:perturbedFeature <{uploaded_entities["featureID.value"].values[0]}>;
                                                                                                         rprov:generationAlgorithm "{method}";
                                                                                                         rprov:values "{perturbationOption}"@en;
                                                                                                         rprov:modelingEntityWasDerivedFrom <{entity}>;
                                                                                                         rprov:wasGeneratedByMA  <urn:uuid:{uuid_DefinitionOfPerturbationOption}>;
                                                                                                         rdfs:label "{labelPerturbation}-{method}"@en.
                                                                                                       }}""")  ##{st.session_state['settings'][key]}rprov:values "{perturbationOption}"@en;
                                        else:

                                            query = (f"""INSERT DATA {{<urn:uuid:{uuid_PerturbationOption}> rdf:type rprov:{name}, owl:NamedIndividual;
                                                                  rprov:perturbedFeature <{uploaded_entities["featureID.value"].values[0]}>;
                                                                  rprov:generationAlgorithm "{method}";
                                                                  rprov:values "{perturbationOption}"@en;
                                                                  rprov:modelingEntityWasDerivedFrom <{entity}>;
                                                                  rprov:wasGeneratedByMA  <urn:uuid:{uuid_DefinitionOfPerturbationOption}>;
                                                                  rdfs:label "{labelPerturbation}-{method}: {perturbationOptionlabel}"@en.
                                                                }}""")
                                            #{st.session_state['settings'][key]}




                                        # host_upload.setQuery(prefix + query)
                                        # host_upload.setMethod(POST)
                                        # host_upload.query()

                    # st.stop()
                except Exception as e:
                    st.write(e)
                    st.error("Error: Could not create DUA")



except Exception as e:
    st.warning(e)
