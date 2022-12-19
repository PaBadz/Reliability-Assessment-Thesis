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

if "data_restrictions_dict" not in st.session_state:
    st.session_state["data_restrictions_dict"] = dict()

# horizontal menu
selected2 = option_menu(None, ["Choose Algorithms", "Perturbation"],
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
    t1, t2, t3 = st.tabs(["Algorithms", "Data Restriction", "Perturbation Recommendations"])
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
                with tab1:

                    with st.expander(label=f"Algorithms for ***{columns}***"):
                        try:
                            if st.session_state.volatility_of_features_dic[columns] == 'High Volatility':
                                st.warning("Feature has high volatility!")
                                st.info(
                                    "Switch to perturbation Recommendations to see which algrorithms were used in the past.")


                            elif st.session_state.volatility_of_features_dic[columns] == 'Medium Volatility':
                                st.info(
                                    "Feature has medium volatility!  \nSwitch to perturbation Recommendations to see which algrorithms were used in the past.")
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

                        except Exception as e:
                            st.write(e)
                            st.info('No Cardinal Values', icon="ℹ️")

            if level == "Ordinal":
                with tab2:
                    with st.expander(label=f"Algorithms for ***{columns}***"):
                        try:
                            if st.session_state.volatility_of_features_dic[columns] == 'High Volatility':
                                st.warning("Feature has high volatility!")
                                st.info(
                                    "Switch to perturbation Recommendations to see which algrorithms were used in the past.")
                            elif st.session_state.volatility_of_features_dic[columns] == 'Medium Volatility':
                                st.info(
                                    "Feature has medium volatility!  \nSwitch to perturbation Recommendations to see which algrorithms were used in the past.")
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

                with tab3:
                    with st.expander(label=f"Algorithms for ***{columns}***"):
                        try:

                            if st.session_state.volatility_of_features_dic[columns] == 'High Volatility':
                                st.warning("Feature has high volatility!")
                                st.info(
                                    "Switch to perturbation Recommendations to see which algrorithms were used in the past.")
                            elif st.session_state.volatility_of_features_dic[columns] == 'Medium Volatility':
                                st.info(
                                    "Feature has medium volatility!  \nSwitch to perturbation Recommendations to see which algrorithms were used in the past.")
                        except:
                            st.info("   No level of volatility determined")

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
            d = getRestriction(host)
            data_restriction = st.selectbox("Select Data Restriction", options=d["URN"].unique())

            st.write(d.loc[d["URN"] == data_restriction])
            if st.button("Get Restriction", type='primary'):
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



                except Exception as e:
                    st.write(e)
                    st.info("Dont forget to upload unique values")

            if st.button("Deselect Restriction"):
                try:
                    st.session_state["data_restrictions_dict"] = getUniqueValuesSeq(host)
                    st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()
                    st.session_state.data_restriction_final.update(st.session_state.data_restrictions_dict)
                    st.write(st.session_state.data_restriction_final)
                    st.experimental_rerun()
                except Exception as e:
                    st.write(e)
                    st.write("Didnt work")


        except Exception as e:

            st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()

            # st.write(st.session_state["data_restrictions_dict"])

    with t3:
        # TODO recommencation system
        st.info("Not implemented yet")
        st.info("Right now it only show if a feature has a high volatility!")
        st.write(st.session_state["volatility_of_features_dic"])
        st.write(st.session_state["DF_feature_volatility_name"])

# Define Algorithmns



try:
    if selected2 == 'Perturbation':
        col1, col2, col3 = st.columns([3, 0.2, 7])
        with col1:
            if "perturbed_value_list" not in st.session_state:
                st.session_state.perturbed_value_list = {}
                for columns in st.session_state.dataframe_feature_names["featureName.value"]:
                    st.session_state.perturbed_value_list[columns] = []

            tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])
            settings = dict()
            perturbed_value_list = dict()
            with tab1:

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
                                st.session_state[f"additional_value_{key}_{method}"] = 0
                            if "lower_bound" not in st.session_state:
                                st.session_state[f"lower_bound{key}_{method}"] = 0
                            if "upper_bound" not in st.session_state:
                                st.session_state[f"upper_bound{key}_{method}"] = 0

                            if method == 'Percentage perturbation':
                                st.markdown(f"##### {method}")

                                st.session_state[f"steps_{key}_{method}"] = int(
                                    st.slider("Percentage of steps", min_value=int(1), max_value=int(100), step=int(1),
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
                                        st.session_state[f"additional_value_{key}_{method}"] = 0
                                    else:
                                        st.session_state[f"additional_value_{key}_{method}"] = \
                                        st.session_state.loaded_feature_sensor_precision_dict[key]

                                    st.markdown(f"##### {method}")
                                    step = st.number_input("Define stepsize", min_value=0.01, max_value=float(
                                        st.session_state.unique_values_dict[key][-1]), step=0.01,
                                                           key=f"step_sensor_precision_{key}")

                                    st.session_state[f"additional_value_{key}_{method}"] = float(
                                        st.slider("Sensor Precision", min_value=float(1), max_value=float(100),
                                                  value=float(st.session_state[f"additional_value_{key}_{method}"]),
                                                  key=f"additional_value_widget_{key}_{method}",step=float(step),
                                                  on_change=update_additional_value, args=(key, method)))
                                    st.session_state[f"steps_{key}_{method}"] = int(
                                        st.slider("Steps", min_value=int(1), max_value=int(100), step=int(1),
                                                  value=int(st.session_state[f"steps_{key}_{method}"]),
                                                  key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                                  args=(key, method)))

                                    settingList[method] = (
                                    sensorPrecision_settings(st.session_state[f"additional_value_{key}_{method}"],
                                                             st.session_state[f"steps_{key}_{method}"]))
                                except Exception as e:
                                    st.write(e)
                                st.write("---------------")

                            elif method == 'Fixed amount':
                                st.markdown(f"##### Define settings for algorithm: {method}")
                                st.session_state[f"additional_value_{key}_{method}"] = int(
                                    st.slider("Amount", min_value=int(1), max_value=int(100), step=int(1),
                                              value=st.session_state[f"additional_value_{key}_{method}"],
                                              key=f"additional_value_widget_{key}_{method}",
                                              on_change=update_additional_value,
                                              args=(key, method)))

                                st.session_state[f"steps_{key}_{method}"] = int(
                                    st.slider("Steps", min_value=int(1), max_value=int(100), step=int(1),
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
                                    lower = st.number_input("Input value")
                                    upper = st.number_input("Input upper value")
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
                                    st.slider("Steps", min_value=int(1), max_value=int(100), step=int(1),
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
            with st.expander("Show Perturbation Setting"):
                st.write(st.session_state['settings'])
            with st.form("Save Modeling Activity to Database"):
                #KG DEVELOPMENT
                #KG: DefinitionOfPertubationOption
                #KG: Define ModelingActivity and then create PerturbationOption Entity with BUA, DUA, DPA as input

                ending_time = getTimestamp()

                starting_time = getTimestamp()
                # KG label nötig? Um die PerturbationOption zu identifizieren?

                label = st.text_input("Definition of Perturbation Option",help="Insert a name for the perturbation option")
                determinationNameUUID = 'DefinitionOfPerturbationOption'
                determinationName = 'DefinitionOfPerturbationOption'

                name = 'PerturbationOption'
                rprovName = 'PerturbationOption'
                ending_time = getTimestamp()

                #todo ausgliedern
                # kann auch implementiert werden bei predict --> dadurch verpflichtend

                if st.form_submit_button("Save Modeling Activity to Database"):
                    # Modeling Phase

                    try:

                        for key in st.session_state['settings']:
                            uuid_DefinitionOfPerturbationOption = determinationDUA(host_upload, determinationName,
                                                                                   label,
                                                                                   starting_time, ending_time)

                            query = (f"""PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                                PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                                PREFIX prov:  <http://www.w3.org/ns/prov#>
                                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                                PREFIX instance:<http://www.semanticweb.org/dke/ontologies#>
                                 SELECT ?featureID ?featureName ?DataUnderstandingEntityID ?DUA {{
                                    ?featureID rdf:type rprov:Feature .
                                    ?featureID rdfs:label ?featureName.
                                    ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
                                    ?DataUnderstandingEntityID rprov:toFeature ?featureID.
                                    ?DataUnderstandingEntityID rprov:wasGeneratedByDUA ?DUA.}}""")
                            results_update = get_connection_fuseki(host, query)

                            result_2 = pd.json_normalize(results_update["results"]["bindings"])

                            if key in result_2["featureName.value"].values:
                                uuid_PerturbationOption = uuid.uuid4()
                                st.write(key)
                                test = (result_2[result_2["featureName.value"]==key])
                                liste = (test["DataUnderstandingEntityID.value"].values).tolist()

                                for activitites in liste:
                                    # TODO Check generationAlgorithm - key only for testing purposes
                                    query = (f"""INSERT DATA {{<urn:uuid:{uuid_PerturbationOption}> rdf:type rprov:{name}, owl:NamedIndividual;
                                                          rprov:perturbedFeature <{test["featureID.value"].values[0]}>;
                                                          rprov:generationAlgorithm "{key}, {st.session_state['settings'][key]}";
                                                          rprov:modelingEntityWasDerivedFrom <{activitites}>;
                                                          rprov:wasGeneratedByMA  <urn:uuid:{uuid_DefinitionOfPerturbationOption}>;
                                                        }}""")
                                    host_upload.setQuery(prefix + query)
                                    host_upload.setMethod(POST)
                                    host_upload.query()

                    except Exception as e:
                        st.write(e)
                        st.error("Error: Could not create DUA")
                #


        with col3:

            insert, delete = st.tabs(["Insert", "Delete"])

            with insert:

                if "df_r" not in st.session_state:
                    st.session_state.df_r = pd.DataFrame(
                        columns=st.session_state.dataframe_feature_names["featureName.value"].tolist())
                if st.button("Add empty row"):

                    a = ["" for a in st.session_state.df_r]
                    st.session_state.df_r.loc[len(st.session_state.df_r)] = a

                with st.expander("Submit new Data"):
                    with st.form("Add Data"):
                        dic = dict()
                        for key, value in st.session_state.level_of_measurement_dic.items():
                            if value == "Cardinal":
                                dic[key] = st.slider(f"Select Value for {key}",
                                                     min_value=float(st.session_state.data_restriction_final[key][0]),
                                                     max_value=float(st.session_state.data_restriction_final[key][-1]),
                                                     key=f"add_data_{key}")
                            if value == "Ordinal":
                                dic[key] = st.selectbox(f"Select Value for {key}",
                                                        options=st.session_state.data_restriction_final[key],
                                                        key=f"add_data_{key}")
                            if value == "Nominal":
                                dic[key] = st.selectbox(f"Select Value for {key}",
                                                        options=st.session_state.data_restriction_final[key],
                                                        key=f"add_data_{key}")
                        if st.form_submit_button("Submit Data"):
                            st.write(dic)
                            st.session_state.df_r = st.session_state.df_r.append(dic, ignore_index=True)





            with delete:
                if st.session_state.df_r.shape[0] == 0:
                    st.write("No data available")
                else:

                    drop_index = int(st.number_input("Index to drop", (st.session_state.df_r.index[0]), (st.session_state.df_r.index[-1])))

                    try:
                        if st.button(f"Drop row with index {drop_index}"):
                            st.session_state.df_r = st.session_state.df_r.drop(drop_index).reset_index(drop=True)
                            #st.session_state.df_r.index += 1
                    except Exception as e:
                        st.info(e)

                st.write(st.session_state.df_r)

        # with tab3:
        #     with st.expander("Show Perturbed Values"):
        #         st.write(st.session_state['perturbed_value_list'])
        #     st.subheader("Both perturbated tables combined")
        #
        #     for i in st.session_state.result_df:
        #         st.write(i)
        #         st.write(type(i))
        #     for i in st.session_state.df_r:
        #         st.write(i)
        #         st.write(type(i))
        #
        #     final_df = pd.concat([st.session_state['result_df'], st.session_state['df_r']])
        #     st.write(final_df)

        gb = GridOptionsBuilder.from_dataframe(st.session_state.df_r)
        # gb.configure_default_column(groupable=False,value=True,
        #                             editable=True, sortable=True, filter=True, resizable=True,
        #                             sizeColumnsToFit=True)

        cellRenderer = JsCode('''
        cellRenderer.prototype.init = function (params) {
            this.eGui = document.createElement('span');
            this.eGui.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="100" viewBox="0 0 18 18"><path d="M5 8l4 4 4-4z"/></svg>' + params.value;
        };

        cellRenderer.prototype.getGui = function () {
            return this.eGui;
        };''')

        gb.configure_selection(selection_mode="multiple", use_checkbox=False, rowMultiSelectWithClick=True)
        gb.configure_auto_height(autoHeight=True)

        for key, value in st.session_state.data_restriction_final.items():
            if st.session_state.level_of_measurement_dic[key] != 'Cardinal':
                gb.configure_column(f"{key}", editable=True, cellEditor="agSelectCellEditor",
                                    cellEditorPopup=True, cellEditorParams={"values": value}, singleClickEdit=False,
                                    sortable=True, filter=True, resizable=True, )
                # cellRenderer=cellRenderer, singleClickEdit=True, width=90,
                # cellEditorParams={"values": value})
            else:
                gb.configure_column(f"{key}", type=['numericColumn', "numberColumnFilter"], editable=True,
                                    sortable=True, filter=True, resizable=True, )

        gridOptions = gb.build()

        data = AgGrid(st.session_state.df_r,
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

        # KG: DEPLOYMENT
        # KG: ClassificationCase
        # KG: selected_rows are ClassificationCase Entity
        # TODO: Create Entity from selected rows, Values: PerturbedTestCase
        # Naming? Labeling?
        # Values Testcase? These are the predicted perturbed rows


        selected_rows = data["selected_rows"]
        deleteTable("2")
        selected_rows_DF = pd.DataFrame(selected_rows,
                                        columns=st.session_state.dataframe_feature_names["featureName.value"])
        try:
            for features in selected_rows_DF:
                if st.session_state.level_of_measurement_dic[features] == 'Cardinal':
                    selected_rows_DF[features] = selected_rows_DF[features].astype(float)
        except Exception as e:
            st.error(f"ERROR! Please change! {e}")
        st.write("### show selected rows")
        st.write(selected_rows_DF)

        st.write("Choose perturbation Mode")
        perturbationMode = st.radio("Choose perturbation Mode", options=["Prioritized", "Selected"], horizontal=True,
                                    label_visibility="collapsed")
        if perturbationMode == "Prioritized":
            data = list()
            with st.expander("Prioritized Perturbation Mode"):
                if f'order_feature' not in st.session_state:
                    st.session_state[f'order_feature'] = list()
                    for feature_name in st.session_state["dataframe_feature_names"]["featureName.value"]:
                        dictionary_values = {'name': feature_name}
                        data.append(dictionary_values)
                        st.session_state[f'order_feature'] = data
                else:
                    data = st.session_state[f'order_feature']

                prio = DraggableList(data, width="50%", key=f'order_feature')
            st.session_state.perturb_mode = prio
        else:
            with st.expander("Selected Perturbation Mode"):

                st.info("Perturbation Mode might not work properly")
                st.info("maybe worthless, selected mode can be achieved otherwise")
                selected = st.multiselect("Select features which should be perturbed",
                                          options=st.session_state["dataframe_feature_names"]["featureName.value"],
                                          default=st.session_state["dataframe_feature_names"]["featureName.value"])
            st.session_state.perturb_mode = selected

        if st.button("Predict"):
            if "perturbedList" not in st.session_state:
                st.session_state.perturbedList = dict()



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

            x_trans_df = pd.DataFrame(ct.fit_transform(x), columns=ct.get_feature_names_out()).reset_index(
                drop=True)
            st.write(x_trans_df)
            y_pred = pd.DataFrame(st.session_state.model.predict(x_trans_df))

            # TODO divide selected rows in order to have seperated dataframes for each row, Idee: Result DF / len(selected_rows_DF)
                # dadurch könnten die Selected rows getrennt werden
            result = selected_rows_DF
            result["prediction"] = y_pred.iloc[len(df):].reset_index(drop=True)
            """
            1) get prediction for selected rows
            """
            st.write(result)

            st.session_state.df_r = result

            # change values in selected rows to list in order to extend the list with perturbated values
            for i in selected_rows:
                for k, v in i.items():
                    if k != "_selectedRowNodeInfo":
                        i[k] = [v]

            # SOllen die perturbated values mit method key in das dataframe geladen werden
            # eventuell mehrere dataframes pro perturbation und column erstellen

            try:
                result_df = pd.DataFrame(
                    columns=result.columns)  # st.session_state.dataframe_feature_names["featureName.value"].tolist())
                if "result_df" not in st.session_state:
                    st.session_state['result_df'] = result_df
                index_perturb = list()
                # dictionary mit den ausgewählten methoden für jede column
                for i in range(0, len(selected_rows)):
                    for column, method in st.session_state['settings'].items():

                        perturbedList = dict()

                        for k, v in selected_rows[i].items():
                            # TODO Hier die Umwandlung der perturbations auslagern
                            # Es muss für jede Methode eine andere möglichkeit geben
                            try:
                                if k == column:
                                    for algorithm_keys in method.keys():

                                        if algorithm_keys == 'Percentage perturbation':

                                            perturbedList[algorithm_keys] = (percentage_perturbation(method[algorithm_keys]["steps"],selected_rows[i][k][0],st.session_state.data_restriction_final[column]))


                                        elif algorithm_keys == '5% perturbation':
                                            perturbedList[algorithm_keys] = (percentage_perturbation(10, selected_rows[i][k][0],st.session_state.data_restriction_final[column]))

                                        elif algorithm_keys == '10% perturbation':
                                            perturbedList[algorithm_keys] = (percentage_perturbation(10, selected_rows[i][k][0],st.session_state.data_restriction_final[column]))

                                        elif algorithm_keys == 'Sensor Precision':
                                            perturbedList[algorithm_keys] = (
                                                sensorPrecision(method[algorithm_keys]["sensorPrecision"],
                                                                method[algorithm_keys]["steps"], selected_rows[i][k][0]))
                                        elif algorithm_keys == 'Fixed amount':
                                            perturbedList[algorithm_keys] = (
                                                fixedAmountSteps(method[algorithm_keys]["amount"],
                                                                 method[algorithm_keys]["steps"],
                                                                 selected_rows[i][k][0]))
                                        elif algorithm_keys == 'Range perturbation':
                                            perturbedList[algorithm_keys] = (
                                                perturbRange(method[algorithm_keys]["lowerBound"],
                                                             method[algorithm_keys]["upperBound"],
                                                             method[algorithm_keys]["steps"]))

                                        elif algorithm_keys == 'Perturb in order':
                                            try:
                                                perturbedList[algorithm_keys] = (
                                                    perturbInOrder(method[algorithm_keys]["steps"],
                                                                   selected_rows[i][k][0],
                                                                   st.session_state.data_restriction_final[column]))#method[algorithm_keys]["values"]

                                            except Exception as e:
                                                st.write(e)

                                        elif algorithm_keys == 'Perturb all values':
                                            perturbedList[algorithm_keys] = (
                                                perturbAllValues(  # method[algorithm_keys]["value"],
                                                    selected_rows[i][k][0],
                                                    st.session_state.data_restriction_final[column]))
                            except Exception as e:
                                st.error(e)
                            perturbed_value_list[column] = perturbedList

                    index_perturb.append(perturbed_value_list.copy())
                # TODO Delete
                st.write(perturbed_value_list)

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

                perturbated_rows_DF = pd.DataFrame(selected_rows,
                                                  columns=result.columns)  # st.session_state.dataframe_feature_names["featureName.value"].tolist())

                perturbated_rows_DF["prediction"] = result["prediction"]
                # result_df=pd.concat([result, perturbated_rows_DF])
                result_df = perturbated_rows_DF

                for x in st.session_state.perturb_mode[::-1]:
                    perturbated_rows_DF = perturbated_rows_DF.explode(x["name"])

                perturbated_rows_DF = perturbated_rows_DF.reset_index(drop=True)
                """
                2) Get new perturbed cases
                """
                st.write(perturbated_rows_DF)

                for column in result_df.columns:
                    result_df = result_df.explode(column)

                for columns in result_df:
                    if columns in st.session_state.cardinal_val.keys():
                        result_df[columns] = result_df[columns].astype(float)

            #

            except Exception as e:
                st.info(e)

            x = pd.concat([df, result_df.iloc[:, :-1]]).reset_index(drop=True)
            x = x.fillna(method='ffill')

            x_trans_df = pd.DataFrame(ct.fit_transform(x), columns=ct.get_feature_names_out()).reset_index(
                drop=True)
            #
            y_pred = pd.DataFrame(st.session_state.model.predict(x_trans_df))

            y_pred.iloc[len(df):].reset_index(drop=True)
            result_df=result_df.reset_index(drop=True)
            result_df["perturbation"] = y_pred
            """
            3) get prediction for perturbed cases
            """
            # KG: DEPLOYMENT
            # KG
            # Todo: Perturbation Assessment --> contains info which is handed over to the anaylst: testcases (which also could be in the ClassificationCase)


            st.write(result_df)

            # different_predictions = st.session_state.result_df[
            #     st.session_state.result_df['prediction'] != st.session_state.result_df['perturbation']]
            # st.write(st.session_state.result_df['perturbation'])
            #
            different_predictions = result_df[
                result_df['prediction'] != result_df['perturbation']]
            """
            4) show cases where prediction changed
            """
            st.write(different_predictions)

            # try:
            #     result_df["Case"] = result_df.index
            #     case = st.selectbox("Select case", options=[x for x in range(0, len(selected_rows))])
            #     st.write(result_df[result_df["Case"] == case])
            #
            #
            # except:
            #     pass



        with st.form("Save Perturbation Assessment to Database"):
            # KG: DEPLOYMENT
            # KG: ClassificationCase
            # KG: selected_rows are ClassificationCase Entity
            # TODO: Create Entity from selected rows, Values: PerturbedTestCase
            # Naming? Labeling?
            # Values Testcase? These are the predicted perturbed rows

            ending_time = getTimestamp()

            starting_time = getTimestamp()

            label = st.text_input("Definition of Perturbation Case",
                                  help="Insert a name for the perturbation option")
            determinationNameUUID = 'PerturbationOfClassificationCase'
            determinationName = 'PerturbationOfClassificationCase'

            name = 'PerturbationOfClassificationCase'
            rprovName = 'PerturbationOfClassificationCase'
            ending_time = getTimestamp()

            # todo ausgliedern
            # kann auch implementiert werden bei predict --> dadurch verpflichtend

            if st.form_submit_button("Save Perturbation Assessment to Database"):
                # Modeling Phase

                try:
                    uuid_DefinitionOfPerturbationOption = determinationDUA(host_upload, determinationName, label,
                                                                           starting_time, ending_time)

                    # query = (f"""PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    #     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    #     PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                    #     PREFIX prov:  <http://www.w3.org/ns/prov#>
                    #     PREFIX owl: <http://www.w3.org/2002/07/owl#>
                    #     PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    #     PREFIX instance:<http://www.semanticweb.org/dke/ontologies#>
                    #      SELECT ?featureID ?featureName ?DataUnderstandingEntityID ?DUA {{
                    #         ?featureID rdf:type rprov:Feature .
                    #         ?featureID rdfs:label ?featureName.
                    #         ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
                    #         ?DataUnderstandingEntityID rprov:toFeature ?featureID.
                    #         ?DataUnderstandingEntityID rprov:wasGeneratedByDUA ?DUA.}}""")
                    # results_update = get_connection_fuseki(host, query)
                    #
                    # result_2 = pd.json_normalize(results_update["results"]["bindings"])
                    #
                    # for key in st.session_state['settings']:
                    #     if key in result_2["featureName.value"].values:
                    #         uuid_PerturbationOption = uuid.uuid4()
                    #         st.write(key)
                    #         test = (result_2[result_2["featureName.value"] == key])
                    #         liste = (test["DataUnderstandingEntityID.value"].values).tolist()
                    #
                    #         for activitites in liste:
                    #             # TODO Check generationAlgorithm - key only for testing purposes
                    #             query = (
                    #                 f"""INSERT DATA {{<urn:uuid:{uuid_PerturbationOption}> rdf:type rprov:{name}, owl:NamedIndividual;
                    #                                   rprov:perturbedFeature <{test["featureID.value"].values[0]}>;
                    #                                   rprov:generationAlgorithm "{key}, {st.session_state['settings'][key]}";
                    #                                   rprov:modelingEntityWasDerivedFrom <{activitites}>;
                    #                                   rprov:wasGeneratedByMA  <urn:uuid:{uuid_DefinitionOfPerturbationOption}>;
                    #                                 }}""")
                    #             host_upload.setQuery(prefix + query)
                    #             host_upload.setMethod(POST)
                    #             host_upload.query()

                except Exception as e:
                    st.write(e)
                    st.error("Error: Could not create DUA")

        with st.form("Save Classification Case to Database"):
                # KG: DEPLOYMENT
                # KG: ClassificationCase
                # KG: selected_rows are ClassificationCase Entity
                # TODO: Create Entity from selected rows, Values: PerturbedTestCase
                # Naming? Labeling?
                # Values Testcase? These are the predicted perturbed rows

                ending_time = getTimestamp()

                starting_time = getTimestamp()

                label = st.text_input("Definition of Perturbation Option",
                                      help="Insert a name for the perturbation option")
                determinationNameUUID = 'DefinitionOfPerturbationOption'
                determinationName = 'DefinitionOfPerturbationOption'

                name = 'PerturbationOption'
                rprovName = 'PerturbationOption'
                ending_time = getTimestamp()

                # todo ausgliedern
                # kann auch implementiert werden bei predict --> dadurch verpflichtend

                if st.form_submit_button("Save Classification Case to Database"):
                    # Modeling Phase

                    try:
                        uuid_DefinitionOfPerturbationOption = determinationDUA(host_upload, determinationName, label,
                                                                               starting_time, ending_time)

                        query = (f"""PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                            PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                            PREFIX prov:  <http://www.w3.org/ns/prov#>
                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                            PREFIX instance:<http://www.semanticweb.org/dke/ontologies#>
                             SELECT ?featureID ?featureName ?DataUnderstandingEntityID ?DUA {{
                                ?featureID rdf:type rprov:Feature .
                                ?featureID rdfs:label ?featureName.
                                ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
                                ?DataUnderstandingEntityID rprov:toFeature ?featureID.
                                ?DataUnderstandingEntityID rprov:wasGeneratedByDUA ?DUA.}}""")
                        results_update = get_connection_fuseki(host, query)

                        result_2 = pd.json_normalize(results_update["results"]["bindings"])

                        for key in st.session_state['settings']:
                            if key in result_2["featureName.value"].values:
                                uuid_PerturbationOption = uuid.uuid4()
                                st.write(key)
                                test = (result_2[result_2["featureName.value"] == key])
                                liste = (test["DataUnderstandingEntityID.value"].values).tolist()

                                for activitites in liste:
                                    # TODO Check generationAlgorithm - key only for testing purposes
                                    query = (
                                        f"""INSERT DATA {{<urn:uuid:{uuid_PerturbationOption}> rdf:type rprov:{name}, owl:NamedIndividual;
                                                          rprov:perturbedFeature <{test["featureID.value"].values[0]}>;
                                                          rprov:generationAlgorithm "{key}, {st.session_state['settings'][key]}";
                                                          rprov:modelingEntityWasDerivedFrom <{activitites}>;
                                                          rprov:wasGeneratedByMA  <urn:uuid:{uuid_DefinitionOfPerturbationOption}>;
                                                        }}""")
                                    host_upload.setQuery(prefix + query)
                                    host_upload.setMethod(POST)
                                    host_upload.query()

                    except Exception as e:
                        st.write(e)
                        st.error("Error: Could not create DUA")


except Exception as e:
    st.warning(e)
