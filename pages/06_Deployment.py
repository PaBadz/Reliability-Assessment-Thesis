import distutils.command.build_ext
from streamlit_extras.colored_header import colored_header
import pandas as pd
import streamlit
from SPARQLWrapper import SPARQLWrapper
from streamlit_sortables import sort_items
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode
from functions.perturbation_algorithms_ohne_values import *
from functions.functions_Reliability import *
import regex as re
import streamlit_ext as ste
from functions.fuseki_connection import *
import streamlit_nested_layout



login()



try:
    host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
    host_upload: SPARQLWrapper = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
except:
    st.info("Please select a database first")
    st.stop()
# ------------------------------------------------------------------------------------------------------------------------

try:
    getDefault(host)
    getAttributes(host)
except Exception as e:
    st.write(e)
    st.error("Please select other dataset")
    st.stop()

# if "data_restrictions_dict" not in st.session_state:
#     st.session_state["data_restrictions_dict"] = dict()
#
# # horizontal menu
menu_perturbation = option_menu(None, ["Perturbation Option",'Perturbation Mode', "Perturbation"],
                                icons=['house', 'gear'],
                                orientation="horizontal")

try:
    savedPerturbationOptions = getPerturbationOptions(host)
except Exception as e:
    st.info("There are no Perturbation Options to select at the moment.")
    st.stop()

# options_cardinal = ['5% perturbation', '10% perturbation','Percentage perturbation',  'Sensor Precision', 'Fixed amount', 'Range perturbation']
options_ordinal = ['Perturb in order', 'Perturb all values']
options_nominal = ['Perturb all values']



if menu_perturbation == 'Perturbation Option':
    hide_table_row_index = """
                                            <style>
                                            thead tr th:first-child {display:none}
                                            tbody th {display:none}
                                            </style>
                                            """
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["Perturbation Options", "Data Restriction", "Perturbation Recommendations"])
    with t1:

        try:
            recommendations = getPerturbationRecommendations(host)
        except:
            st.info("There are no recommendations at the moment.")

        with st.expander("Show all perturbation options"):
            st.dataframe(savedPerturbationOptions[["FeatureName", "PerturbationOption", "label"]].reset_index(drop=True),use_container_width=True)



        if "perturbationOptions" not in st.session_state:

            # save the selected options in a dictionary in order to perform the perturbation
            st.session_state.perturbationOptions_settings = {}

            # save all information for the selected perturbation options in a dictionary
            st.session_state.assessmentPerturbationOptions = {} #pd.DataFrame(columns=savedPerturbationOptions.columns)
            st.session_state.df_test = pd.DataFrame()
            # save default values for each feature
            st.session_state.perturbationOptions = {}
            for columns in st.session_state.dataframe_feature_names["featureName.value"]:
                st.session_state.perturbationOptions[columns] = []
                # TODO alle werte werden gespeichert

                st.session_state.assessmentPerturbationOptions[columns] = []
                # st.session_state.perturbationOptions_settings[columns] = {}

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


                    with st.expander(label=f"Algorithms for ***{feature_names}***"):
                        with st.expander("Show all available Perturbation Options"):
                            st.dataframe(
                                savedPerturbationOptions.query('FeatureName == "%s"' % feature_names)[["FeatureName", "PerturbationOption", "label", "Settings"]],use_container_width=True)

                        settingList = {}

                        settings = {}
                        # TODO INSERT EXPANDER EXPANDER

                        with st.expander("Show past perturbation options"):
                            try:
                                if recommendations[recommendations["featureName.value"] == feature_names].empty:
                                    st.info("No recommendations available")
                                    st.markdown(":information_source: :green[This means this feature was never perturbed before].")
                                else:
                                    recommendations[recommendations["featureName.value"] == feature_names]
                            except:
                                pass

                        try:
                            if st.session_state.volatility_of_features_dic[feature_names] == 'High Volatility':
                                st.warning("Feature has high volatility!")

                            elif st.session_state.volatility_of_features_dic[feature_names] == 'Medium Volatility':
                                st.info(
                                    "Feature has medium volatility!  \nSwitch to perturbation Recommendations to see which algrorithms were used in the past.")




                        except:
                            st.info("No level of volatility determined")

                        try:
                            options = (
                                savedPerturbationOptions.loc[savedPerturbationOptions['FeatureName'] == feature_names][
                                    "label"])
                            st.session_state.perturbationOptions[feature_names] = st.multiselect(f'{feature_names}',
                                                                                                 options=options,
                                                                                                 default=
                                                                                                 st.session_state.perturbationOptions[
                                                                                                     feature_names],
                                                                                                 key=f"perturbationOption_{feature_names}",
                                                                                                 on_change=changePerturbationOption,
                                                                                                 args=(
                                                                                                     feature_names,),max_selections=1)  # ,

                            chosen_perturbationOptions_feature = (
                                savedPerturbationOptions.loc[(savedPerturbationOptions['label'].isin(
                                    st.session_state.perturbationOptions[feature_names])) & (savedPerturbationOptions[
                                                                                                 'FeatureName'] == feature_names)])
                            # st.write(chosen_perturbationOptions_feature)
                            #df_test=df_test.append(chosen_perturbationOptions_feature)
                            df_test = pd.concat([df_test, chosen_perturbationOptions_feature])
                            st.table(chosen_perturbationOptions_feature[["FeatureName", "PerturbationOption", "Settings","label"]])
                            #st.write(df_test)

                            # st.session_state.assessmentPerturbationOptions[feature_names] = chosen_perturbationOptions_feature()
                            st.session_state.assessmentPerturbationOptions[feature_names] = chosen_perturbationOptions_feature.to_dict("list")
                            #st.write(st.session_state.assessmentPerturbationOptions[feature_names])



                            for index, row in chosen_perturbationOptions_feature.iterrows():
                                keys = re.findall("'(.*?)'", row["Settings"])
                                values = re.findall(': (.*?)(?:,|})', row["Settings"])

                                # create nested dictionary with column name as key and keys as second key and values as values
                                settings = (dict(zip(keys, values)))
                                # convert values to float except if the key is step
                                for feature_name, level_of_scale in settings.items():
                                    if feature_name == "steps":
                                        settings[feature_name] = int(level_of_scale)
                                    else:
                                        settings[feature_name] = float(level_of_scale)

                                settingList[row["PerturbationOption"]] = settings


                            st.session_state.perturbationOptions_settings[feature_names] = settingList


                            # st.write(st.session_state.perturbationOptions_settings[feature_names])

                            # TODO connect to
                        except Exception as e:
                            st.write(e)
                            st.info('No Cardinal Values', icon="ℹ️")

            if level_of_scale == "Ordinal":
                with tab2:
                    with st.expander(label=f"Algorithms for ***{feature_names}***"):
                        settingList = {}

                        settings = {}

                        with st.expander("Show past perturbation options"):
                            try:
                                if recommendations[recommendations["featureName.value"] == feature_names].empty:
                                    st.info("No recommendations available")
                                    st.markdown(":information_source: :green[This means this feature was never perturbed before].")
                                else:
                                    recommendations[recommendations["featureName.value"] == feature_names]
                            except:
                                pass

                        try:
                            if st.session_state.volatility_of_features_dic[feature_names] == 'High Volatility':
                                st.warning("Feature has high volatility!")
                                st.info(
                                    "Switch to perturbation Recommendations to see which algrorithms were used in the past.")
                            elif st.session_state.volatility_of_features_dic[feature_names] == 'Medium Volatility':
                                st.info(
                                    "Feature has medium volatility!  \nSwitch to perturbation Recommendations to see which algrorithms were used in the past.")
                        except:
                            st.info("No level of volatility determined")

                        try:
                            options = (
                                savedPerturbationOptions.loc[savedPerturbationOptions['FeatureName'] == feature_names][
                                    "label"])
                            st.session_state.perturbationOptions[feature_names] = st.multiselect(f'{feature_names}',
                                                                                                 options=options,
                                                                                                 default=
                                                                                                 st.session_state.perturbationOptions[
                                                                                                     feature_names],
                                                                                                 key=f"perturbationOption_{feature_names}",
                                                                                                 on_change=changePerturbationOption,
                                                                                                 args=(
                                                                                                     feature_names,),
                                                                                                 max_selections=1)  # ,

                            chosen_perturbationOptions_feature = (
                                savedPerturbationOptions.loc[(savedPerturbationOptions['label'].isin(
                                    st.session_state.perturbationOptions[feature_names])) & (savedPerturbationOptions[
                                                                                                 'FeatureName'] == feature_names)])
                            # st.write(chosen_perturbationOptions_feature)
                            df_test = df_test.append(chosen_perturbationOptions_feature)
                            st.table(chosen_perturbationOptions_feature[["FeatureName", "PerturbationOption","Settings", "label"]])


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
                                for feature_name, level_of_scale in settings.items():
                                    if feature_name == "steps":
                                        settings[feature_name] = int(level_of_scale)


                                # if settings != {}:
                                settingList[row["PerturbationOption"]] = settings

                            st.session_state.perturbationOptions_settings[feature_names] = (settingList)

                            # st.write(st.session_state.perturbationOptions_settings[feature_names])



                        except Exception as e:
                            st.write(e)
                            st.info('No Ordinal Values', icon="ℹ️")

            if level_of_scale == "Nominal":

                with tab3:
                    with st.expander(label=f"Algorithms for ***{feature_names}***"):
                        settingList = {}

                        settings = {}
                        with st.expander("Show past perturbation options"):
                            try:
                                if recommendations[recommendations["featureName.value"] == feature_names].empty:
                                    st.info("No recommendations available")
                                    st.markdown(":information_source: :green[This means this feature was never perturbed before].")
                                else:
                                    recommendations[recommendations["featureName.value"] == feature_names]
                            except:
                                pass

                        try:

                            if st.session_state.volatility_of_features_dic[feature_names] == 'High Volatility':
                                st.warning("Feature has high volatility!")
                                st.info(
                                    "Switch to perturbation Recommendations to see which algrorithms were used in the past.")
                            elif st.session_state.volatility_of_features_dic[feature_names] == 'Medium Volatility':
                                st.info(
                                    "Feature has medium volatility!  \nSwitch to perturbation Recommendations to see which algrorithms were used in the past.")
                        except:
                            st.info("   No level of volatility determined")

                        try:
                            options = (
                            savedPerturbationOptions.loc[savedPerturbationOptions['FeatureName'] == feature_names]["label"])
                            st.session_state.perturbationOptions[feature_names] = st.multiselect(f'{feature_names}',
                                                                                           options=options, default=
                                                                                           st.session_state.perturbationOptions[
                                                                                               feature_names],
                                                                                           key=f"perturbationOption_{feature_names}",
                                                                                           on_change=changePerturbationOption,
                                                                                           args=(feature_names,),max_selections=1)

                            chosen_perturbationOptions_feature = (savedPerturbationOptions.loc[(savedPerturbationOptions['label'].isin(
                                st.session_state.perturbationOptions[feature_names])) & (
                                                                             savedPerturbationOptions[
                                                                                 'FeatureName'] == feature_names)])
                            df_test=df_test.append(chosen_perturbationOptions_feature)



                            # Display a static table
                            st.table(chosen_perturbationOptions_feature[["FeatureName", "PerturbationOption", "label"]])
                            # a = chosen_perturbationOptions_feature[["FeatureName", "PerturbationOption", "label"]].reset_index(drop=True)
                            # st.write(a,use_container_width=True)

                            st.session_state.assessmentPerturbationOptions[
                                feature_names] = chosen_perturbationOptions_feature.to_dict("list")

                            # st.write(st.session_state.assessmentPerturbationOptions[feature_names])

                            for index, row in chosen_perturbationOptions_feature.iterrows():

                                keys = re.findall("'(.*?)'", row["Settings"])
                                values = re.findall(': \[(.*?)\]', row["Settings"])


                                # create nested dictionary with column name as key and keys as second key and values as values
                                settings = (dict(zip(keys, values)))
                                # st.write("settings",settings)
                            # convert values to float except if the key is step

                                settingList[row["PerturbationOption"]] = settings
                                # st.write(settingList)

                            st.session_state.perturbationOptions_settings[feature_names] = (settingList)
                            # st.write(st.session_state.perturbationOptions_settings[feature_names])
                        except Exception as e:
                            st.error(e)
                            st.info('No Nominal Values', icon="ℹ️")

        colored_header(
            label="Show Algorithms",
            description="Define level of scale for each feature",
            color_name="red-50",
        )
        with st.expander("Show chosen Perturbation Options"):
            # delete empty dictionaries
            st.write(df_test)
            st.session_state.df_test = df_test

            for key in list(st.session_state.assessmentPerturbationOptions.keys()):
                if not st.session_state.assessmentPerturbationOptions[key]["FeatureID"]:
                    del st.session_state.assessmentPerturbationOptions[key]

            for feature in list(st.session_state.perturbationOptions_settings.keys()):
                if not st.session_state.perturbationOptions_settings[feature]:
                    del st.session_state.perturbationOptions_settings[feature]


            st.write(st.session_state.assessmentPerturbationOptions)
            st.write(st.session_state.perturbationOptions_settings)




        # Select and Deselect Data Restriction
    with t2:

        try:
            savedRestrictions = getRestriction(host)
            st.write(savedRestrictions)

            #data_restriction = st.selectbox("Select Data Restriction", options=savedRestrictions["DataRestrictionActivity"].unique())
            st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()

            #st.write(savedRestrictions.loc[savedRestrictions["DataRestrictionActivity"] == data_restriction])
            # if st.button("Get Restriction", type='primary'):

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

                data_restriction_entity = st.session_state.assessmentPerturbationOptions[feature_name]["DataUnderstandingEntity"][0]

                featureID = st.session_state.assessmentPerturbationOptions[feature_name]["FeatureID"][0]

                st.session_state["data_restrictions_dict"] = getDataRestrictionSeqDeployment(data_restriction_entity,featureID, host)

                try:
                    st.session_state.data_restriction_final.update(st.session_state.data_restrictions_dict)
                except Exception as e:
                    pass
                    # st.error(e)
                    # st.session_state["data_restrictions_dict"] = getUniqueValuesSeq(host)
                    # st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()
                    # st.session_state.data_restriction_final.update(st.session_state.data_restrictions_dict)
                    # st.write(st.session_state.data_restriction_final)





        except Exception as e:
            st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()



    with st.expander("Show Data Restriction values"):
        st.write("Data Restriction",st.session_state.data_restriction_final)

            # st.write(st.session_state["data_restrictions_dict"])

    with t3:
        # TODO recommencation system
        st.info("Not implemented yet")
        st.info("Right now it only show if a feature has a high volatility!")
        st.write(st.session_state["volatility_of_features_dic"])
        st.write(st.session_state["DF_feature_volatility_name"])

    # Define Algorithmns

if menu_perturbation == 'Perturbation Mode':
    st.write("Choose perturbation Mode")
    st.write("It does not make sense, that the user is able to select the data restriction, only for the development"
             "in the development view it is neccessary to connect the chosen data restriction with the perturbation option and not any")
    st.info("If you want to change the order of perturbation execution drag an drop accordingly")


    options = ['Full','Prioritized', 'Selected']

    feature_names = st.session_state["dataframe_feature_names"]["featureName.value"].values.tolist()

    if "pertubation_mode" not in st.session_state:
        st.session_state.pertubation_mode = "Full"

    def change(value):
        st.session_state.pertubation_mode = value




    pertubation_mode = st.radio(
        "Which Perturbation Mode",
        ('Full','Prioritized', 'Selected'),index=options.index(st.session_state.pertubation_mode), on_change=change, args=(st.session_state.pertubation_mode,))
    if pertubation_mode =="Full":
        st.session_state.perturb_mode_values = feature_names

        st.session_state.pertubation_mode = "Full"

    if pertubation_mode =="Prioritized":
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
        st.write(st.session_state.perturb_mode_values)


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
            # Not necessary
            # if st.button("Add empty row"):
            #     add_empty = ["" for a in st.session_state.df_aggrid_beginning]
            #     st.session_state.df_aggrid_beginning.loc[len(st.session_state.df_aggrid_beginning)] = add_empty

            with st.expander("Submit new Data", expanded=False):
                with st.form("Add Data"):
                    dic = dict()
                    col_cardinal, col_ordinal, col_nominal = st.columns(3, gap="medium")

                    for feature_name, level_of_scale in st.session_state.level_of_measurement_dic.items():
                        if level_of_scale == "Cardinal":

                            with col_cardinal:
                                dic[feature_name] = st.number_input(f"Select Value for {feature_name}",
                                                                    min_value=float(
                                                                        st.session_state.data_restriction_final[
                                                                            feature_name][0]),
                                                                    max_value=float(
                                                                        st.session_state.data_restriction_final[
                                                                            feature_name][-1]),
                                                                    key=f"add_data_{feature_name}")

                        if level_of_scale == "Ordinal":
                            with col_ordinal:
                                dic[feature_name] = st.selectbox(f"Select Value for {feature_name}",
                                                                 options=st.session_state.data_restriction_final[
                                                                     feature_name],
                                                                 key=f"add_data_{feature_name}")
                        if level_of_scale == "Nominal":
                            with col_nominal:
                                dic[feature_name] = st.selectbox(f"Select Value for {feature_name}",
                                                                 options=st.session_state.data_restriction_final[
                                                                     feature_name],
                                                                 key=f"add_data_{feature_name}")
                    if st.form_submit_button("Submit Data", type='primary'):
                        st.session_state.df_aggrid_beginning = st.session_state.df_aggrid_beginning.append(dic, ignore_index=True)
                        st.experimental_rerun()
                        st.success("Data added")


        with delete:
            if st.session_state.df_aggrid_beginning.shape[0] == 0:
                st.write("No data available")
            else:

                drop_index = int(st.number_input("Row to delete", (st.session_state.df_aggrid_beginning.index[0]+1),
                                                 (st.session_state.df_aggrid_beginning.index[-1]+1)))

                try:
                    if st.button(f"Delete row  {drop_index}"):
                        st.session_state.df_aggrid_beginning = st.session_state.df_aggrid_beginning.drop(drop_index-1).reset_index(drop=True)
                        # st.session_state.df_r.index += 1
                        st.experimental_rerun()
                except Exception as e:
                    st.info(e)
            deleteTable("delete_selected_rows_table")


        if st.session_state.df_aggrid_beginning.shape[0] == 0:
            st.info("Insert new data to continue")
            st.stop()
        # configue aggrid table
        gb = GridOptionsBuilder.from_dataframe(st.session_state.df_aggrid_beginning)
        gb.configure_selection(selection_mode="multiple", use_checkbox=False, rowMultiSelectWithClick=True)
        gb.configure_auto_height(autoHeight=True)

        for feature_name, value in st.session_state.data_restriction_final.items():
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

        colored_header(
            label="Show selected rows",
            description="These rows are going to be perturbed. Each one is a classification case",
            color_name="red-50",
        )

        if selected_rows_DF.shape[0] == 0:
            st.info("Select rows to continue")
            st.stop()

        st.dataframe(selected_rows_DF, use_container_width=True)
        with st.expander("Show Perturbation options"):

            st.write(st.session_state.perturbationOptions_settings)
        with st.expander("Insert label for Perturbation cases"):
            label_list = []
            for i in range(0,len(selected_rows)):
                label_case = st.text_input(f"Label for Case {i+1}", help="Insert a name for the perturbation Assessment", key =f"label_{i}")
                label_list.append(label_case)

            st.write(label_list)

        checkbox_upload =  st.checkbox("Upload")

        if st.button("Predict", type="primary"):

            def uploadPerturbationMode():
                st.session_state.pertubation_mode = "Full"
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

                x_trans_df = pd.DataFrame(ct.fit_transform(x), columns=ct.get_feature_names_out()).reset_index(
                    drop=True)

                y_pred = pd.DataFrame(st.session_state.model.predict(x_trans_df))


                # TODO divide selected rows in order to have seperated dataframes for each row, Idee: Result DF / len(selected_rows_DF)
                # dadurch könnten die Selected rows getrennt werden

                result = selected_rows_DF
                # reset index for y_pred in order to be able to insert it to result
                result["prediction"] = y_pred.iloc[len(df):].reset_index(drop=True)

                with st.expander("1: get prediction for selected rows"):
                    st.write(result)


                # change values in selected rows to list in order to extend the list with perturbated values
                # this is done because we need to explode it later
                for row in selected_rows:
                    for feature, value in row.items():
                        if feature != "_selectedRowNodeInfo":
                            if st.session_state.level_of_measurement_dic[feature] != 'Cardinal':
                                row[feature] = [value]
                            else:
                                row[feature] = [float(value)]

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
                                                                            st.session_state.data_restriction_final[
                                                                                column]))


                                            elif algorithm_keys == '5% perturbation':
                                                try:
                                                    perturbedList[algorithm_keys] = (
                                                        percentage_perturbation(5, selected_rows[i][k][0],
                                                                                st.session_state.data_restriction_final[
                                                                                    column]))
                                                except Exception as e:
                                                    st.error(f"ERROR! Please change! {e}")

                                            elif algorithm_keys == '10% perturbation':
                                                perturbedList[algorithm_keys] = (
                                                    percentage_perturbation(10, selected_rows[i][k][0],
                                                                            st.session_state.data_restriction_final[
                                                                                column]))

                                            elif algorithm_keys == 'Sensor Precision':
                                                perturbedList[algorithm_keys] = (
                                                    sensorPrecision(method[algorithm_keys]["sensorPrecision"],
                                                                    method[algorithm_keys]["steps"],
                                                                    selected_rows[i][k][0],
                                                                    st.session_state.data_restriction_final[column]))
                                            elif algorithm_keys == 'Fixed amount':
                                                perturbedList[algorithm_keys] = (
                                                    fixedAmountSteps(method[algorithm_keys]["amount"],
                                                                     method[algorithm_keys]["steps"],
                                                                     selected_rows[i][k][0],
                                                                     st.session_state.data_restriction_final[column]))
                                            elif algorithm_keys == 'Range perturbation':
                                                perturbedList[algorithm_keys] = (
                                                    perturbRange(method[algorithm_keys]["lowerBound"],
                                                                 method[algorithm_keys]["upperBound"],
                                                                 method[algorithm_keys]["steps"]))

                                            elif algorithm_keys == "Bin perturbation":
                                                try:
                                                    for j in range(len(st.session_state.loaded_bin_dict[k])-1):
                                                        if float(st.session_state.loaded_bin_dict[k][j]) <= float(selected_rows[i][k][0]) <= float(st.session_state.loaded_bin_dict[k][j + 1]):
                                                            new_list = [float(st.session_state.loaded_bin_dict[k][j]), float(st.session_state.loaded_bin_dict[k][j + 1])]
                                                            break

                                                    perturbedList[algorithm_keys] = (
                                                        perturbRange(new_list[0],
                                                                     new_list[1],
                                                                     method[algorithm_keys]["steps"]))
                                                except Exception as e:
                                                    st.error(e)
                                                    pass


                                            elif algorithm_keys == 'Perturb in order':
                                                try:
                                                    perturbedList[algorithm_keys] = (
                                                        perturbInOrder(method[algorithm_keys]["steps"],
                                                                       selected_rows[i][k][0],
                                                                       st.session_state.data_restriction_final[
                                                                           column]))  # method[algorithm_keys]["values"]



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

                    except Exception as e:
                        st.write(e)
                    # index perturb contains the different perturbation values for each case
                    index_perturb.append(perturbed_value_list.copy())



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

                result_df=result_df.drop_duplicates(keep='first')


                for columns in result_df:
                    if st.session_state.level_of_measurement_dic[features] == 'Cardinal':
                        result_df[columns] = result_df[columns].astype(float)

                result_df["Case"] = result_df.index
                with st.expander("2: Get new perturbed cases"):
                    st.write(result_df)

            #

            except Exception as e:
                st.info(e)

            try:

                x = pd.concat([df, result_df.iloc[:, :-1]]).reset_index(drop=True)
                x = x.fillna(method='ffill')

                x_trans_df = pd.DataFrame(ct.fit_transform(x), columns=ct.get_feature_names_out()).reset_index(
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
                                                         uuid_DefinitionOfPerturbationOption,st.session_state.perturbationOptions_settings, st.session_state.assessmentPerturbationOptions)
                            uuid_ClassificationCase = uuid.uuid4()

                            rows = selected_rows_DF.iloc[i].to_dict()
                            uploadClassificationCase(host_upload, uuid_ClassificationCase, label_list[i],
                                                     uuid_PerturbationAssessment,
                                                     rows)
                        except Exception as e:
                            st.error(e)


                    with st.expander(f"Get prediction for perturbed **case: {i+1} {label_list[i]}**"):
                        df = df.drop(columns = ["Case"])
                        st.write(df.style.apply(lambda x: ["background-color: #FF4B4B"
                                                                              if (v != x.iloc[0])
                                                                              else "" for i, v in enumerate(x)],
                                                                   axis=0))

                        different_pred = df.iloc[:1]
                        different_pred2 = df[df['prediction'] != df['perturbation']]
                        # shows the first original prediction
                        different_pred3 = pd.concat([different_pred,different_pred2]).reset_index(drop=True)

                        ste.download_button(f'Download CSV file for Case {i + 1}: {label_list[i]}',
                                            df.to_csv(index=False),
                                            f"{label_list[i]}_{uuid_PerturbationAssessment}.csv")

                        if different_pred2.empty:
                            st.info(f"No prediction with perturbated values changed for case {i+1} {label_list[i]}")
                        else:
                            with st.expander("4: show cases where prediction changed"):
                                st.dataframe(different_pred3.style.apply(lambda x: ["background-color: #FF4B4B"
                                                                              if (v != x.iloc[0])
                                                                              else "" for i, v in enumerate(x)],
                                                                   axis=0))








            except Exception as e:
                st.info(e)

            # try:
            #     result_df["Case"] = result_df.index
            #     case = st.selectbox("Select case", options=[x for x in range(0, len(selected_rows))])
            #     st.write(result_df[result_df["Case"] == case])
            #
            #
            # except:
            #     pass

            # with st.form("ClassificationCase"):
            #     # KG: DEPLOYMENT
            #     # KG: ClassificationCase
            #     # KG: selected_rows are ClassificationCase Entity
            #     amount_selected_rows = len(data["selected_rows"])
            #     counter = 0
            #     if amount_selected_rows > 0:
            #         for i in range(0, amount_selected_rows):
            #             st.text_input(f"Name of the {i + 1}. Classification Case", key=f"classification_case_{i}")
            #         counter += 1
            #
            #     query = """ <http://www.semanticweb.org/dke/ontologies/2021/6/25_7437>
            #                 rdf:type              rprov:ClassificationCase , owl:NamedIndividual ;
            #                 rdfs:label            "CaseY"@en ;
            #                 rprov:values          <http://www.semanticweb.org/dke/ontologies/2021/6/25_9096> , <http://www.semanticweb.org/dke/ontologies/2021/6/25_7585> ;
            #                 rprov:wasAssignedToDeploymentEntity <http://www.semanticweb.org/dke/ontologies/2021/6/25_7487> ;
            #                 prov:generatedAtTime  "0000-00-00T00:00:00Z" ."""

        # try:
        # if result_df is not None:

            # with st.form("Save Perturbation Assessment to Database"):
            #     # KG: DEPLOYMENT
            #     # KG: ClassificationCase
            #     # KG: selected_rows are ClassificationCase Entity
            #     # TODO: Create Entity from selected rows, Values: PerturbedTestCase
            #
            #     ending_time = getTimestamp()
            #     starting_time = getTimestamp()
            #
            #     label = st.text_input("Definition of Perturbation Case",
            #                           help="Insert a name for the perturbation Assessment")
            #     determinationNameUUID = 'PerturbationOfClassificationCase'
            #     determinationName = 'PerturbationOfClassificationCase'
            #
            #     name = 'PerturbationOfClassificationCase'
            #     rprovName = 'PerturbationOfClassificationCase'
            #     ending_time = getTimestamp()
            #
            #     # todo mehr als eine selected row
            #     # kann auch implementiert werden bei predict --> dadurch verpflichtend
            #
            #     def uploadPerturbationAssessment(uuid_PerturbationAssessment, label, uuid_DefinitionOfPerturbationOption):
            #         for key in st.session_state.perturbationOptions_settings.keys():
            #            for perturbationOption in st.session_state.assessmentPerturbationOptions[key]["DataUnderstandingEntity"].values():
            #            #for perturbationOption in st.session_state.assessmentPerturbationOptions[key]["DataUnderstandingEntity"].values():
            #                query = (f"""INSERT DATA {{<urn:uuid:{uuid_PerturbationAssessment}> rdf:type rprov:PerturbationAssessment, owl:NamedIndividual;
            #                             rdfs:label "{label}"@en ;
            #                             rprov:deploymentEntityWasDerivedFrom <{perturbationOption}>;
            #                             rprov:perturbedTestCase "Saved as csv with name: ";
            #                             rprov:wasGeneratedByDA  <urn:uuid:{uuid_DefinitionOfPerturbationOption}>;
            #                                         }}""")
            #                host_upload.setQuery(prefix + query)
            #                host_upload.setMethod(POST)
            #                host_upload.query()
            #
            #
            #     def uploadClassificationCase(uuid_ClassificationCase, label, uuid_PerturbationAssessment, rows):
            #         query = (f"""INSERT DATA {{<urn:uuid:{uuid_ClassificationCase}> rdf:type rprov:PerturbationAssessment, owl:NamedIndividual;
            #                                         rdfs:label "{label}"@en ;
            #                                         rprov:values "{rows}"@en;
            #                                         rprov:wasAssignedToDeploymentEntity <{uuid_PerturbationAssessment}>;
            #                                                     }}""")
            #
            #         st.write(query)
            #         host_upload.setQuery(prefix + query)
            #         host_upload.setMethod(POST)
            #         host_upload.query()
            #
            #     if st.form_submit_button("Save Perturbation Assessment to Database"):
            #         st.write("ff")
            #         st.stop()
            #
            #
            #         # Modeling Phase
            #
            #         # generate uuid for deployment activity
            #         uuid_DefinitionOfPerturbationOption = determinationActivity(host_upload, determinationName, label,
            #                                                               starting_time, ending_time)
            #         uuid_PerturbationAssessment = uuid.uuid4()
            #         uploadPerturbationAssessment(uuid_PerturbationAssessment, label, uuid_DefinitionOfPerturbationOption)
            #         uuid_ClassificationCase = uuid.uuid4()
            #         rows = selected_rows_DF.to_dict()
            #         uploadClassificationCase(uuid_ClassificationCase, label,uuid_PerturbationAssessment, rows)
        # except:
        #     pass




except Exception as e:
    st.warning(e)
