import pandas as pd
import streamlit as st
from SPARQLWrapper import SPARQLWrapper
from streamlit_extras.colored_header import colored_header
from streamlit_option_menu import option_menu
from streamlit_sortables import sort_items
import time
import streamlit_nested_layout

from functions.functions import switch_page
from functions.functions_DataUnderstanding import update_feature_sensor_precision, defaultValuesCardinal, \
    update_data_restrictions_cardinal, defaultValuesOrdinal, update_data_restrictions_ordinal, defaultValuesNominal, \
    update_data_restrictions_nominal
from functions.functions_Reliability import defaultValuesCardinalRestriction, defaultValuesOrdinalRestriction, \
    defaultValuesNominalRestriction, getRestriction
from functions.functions_Reliability import getDefault
from streamlit_extras.no_default_selectbox import selectbox
from functions.fuseki_connection import login, getAttributes, getTimestamp, determinationActivity, uploadDUE, \
    deleteWasGeneratedByDUA, getUniqueValuesSeq, uploadDR, getSensorPrecision, uploadUniqueValues, \
    getDataRestrictionSeq, getAttributesDataUnderstanding, get_feature_names

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
    host = f"http://localhost:3030{st.session_state.fuseki_database}/sparql"
    host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
except Exception as e:
    st.info(e,"Please select a database first")
    st.stop()


try:
    st.session_state.dataframe_feature_names = get_feature_names(host)
except Exception as e:
    st.error(e)

if st.session_state.dataframe_feature_names.empty:
    st.stop()


optionsDataUnderstanding = option_menu("Data Understanding Options", ["Scale", "Volatility", "Data Restrictions", "Feature Sensor Precision"],
                                       icons=['collection', 'arrow-down-up', 'slash-circle'],
                                       menu_icon="None", default_index=0, orientation="horizontal")

with st.expander("Show information"):
    try:
        getAttributesDataUnderstanding(host)
    except Exception as e:
        pass
    try:
        uploaded_DataRestriction = getRestriction(host)
    except:
        st.warning("No Data Restrictions determined")

    try:
        getDefault(host)
    except:
        pass


# Hier kann die scale ausgewählt werden
if optionsDataUnderstanding == "Scale":


    determinationName = 'DeterminationOfScaleOfFeature'
    label = '"detScaleOfFeature"@en'
    dicName = 'level_of_measurement_dic'
    name = 'ScaleOfFeature'
    rprovName = 'scale'



    # wenn noch keine scale in fuseki bestimmt wurde, erstelle Form mit auswahl von scales
    if st.session_state["level_of_measurement_dic"] == {}:
        st.warning("Please insert level of scale for each feature! This is an important step and cannot be changed afterwards.")
        with st.expander("Click here to changes scale of features"):
            st.markdown(
                     """
                     - **Cardinal**: only minimum and maximum values are saved. **:red[Must be numerical]**
                     - **Ordinal**: the order of all values are saved, order can be arranged in the next step
                     - **Nominal**: all values are saved with no further ordering"""
                     )
            starting_time = getTimestamp()

            with st.form("Change level of measurement for features"):
                options = ['Cardinal', 'Ordinal', 'Nominal']

                for index, row in st.session_state.dataframe_feature_names["featureName.value"].items():
                    if f'level_of_measurement_{row}' not in st.session_state:
                        st.session_state[f'level_of_measurement_{row}'] = ' '
                    # wenn level of measurement dictionary nicht leer ist gibt es die level of measurement an
                    #st.session_state.level_of_measurement_dic[row] = st.selectbox(f"**{row}**", options=options, index=0,key=f'level_of_measurement_{row}_widget',format_func=lambda x: 'Select an option' if x == '' else x)



                    st.session_state.level_of_measurement_dic[row] = selectbox(f"**{row}**", options=options,key=f'level_of_measurement_{row}_widget')



                # submit selected scale of measurements
                if st.form_submit_button("Submit", type="primary"):

                    if None in st.session_state.level_of_measurement_dic.values():
                        st.error("Please select a level of measurement for all features")
                        st.stop()
                    ending_time = getTimestamp()
                    uuid_determinationScale = determinationActivity(host_upload, determinationName, label,
                                                               starting_time, ending_time)
                    uploadDUE(host_upload,host,st.session_state["level_of_measurement_dic"], uuid_determinationScale, name,
                              rprovName)
                    st.experimental_rerun()

    else:
        colored_header(
            label="Scale of features",
            description="Define level of scale for each feature",
            color_name="red-70",
        )

        with st.expander("Show level of measurement for features"):
            st.write(st.session_state.level_of_measurement_dic)

            if st.session_state.unique_values_dict == {}:
                if st.button("Change level of measurement", type="primary"):

                    del st.session_state["level_of_measurement_dic"]
                    deleteWasGeneratedByDUA(host_upload,st.session_state["DF_feature_scale_name"])
                    st.experimental_rerun()
                st.error(
                    "Please define order of ordinal features and upload!")
                st.warning(
                    "If these steps are not completed at the beginning, this will result in errors and the app will not run properly.!")
        colored_header(
            label="Order of ordinal features",
            description="""Open the expander for the feature to change the order and upload unique values afterwards!
                        """,
            color_name="red-70",
        )

        try:
            getUniqueValuesSeq(host)

        except Exception as e:
            for feature, scale in st.session_state["level_of_measurement_dic"].items():
                starting_time = getTimestamp()
                #data_restrictions_dic = dict()
                data = list()
                if scale == "Cardinal":
                    st.session_state['first_unique_values_dict'][feature] = [
                        min(st.session_state['first_unique_values_dict'][feature]),
                        max(st.session_state['first_unique_values_dict'][feature])]
                if scale == 'Ordinal':
                    with st.expander(f"Define Order for {feature}"):
                        # wenn es noch keine session_state gibt, erstelle eine leere liste welche im anschluss mit den daten von den unique values gefüllt wird
                        # falls es eine session_state gibt, übergib die session state an die liste
                        if f'order_of_ordinal_{feature}' not in st.session_state:
                            st.session_state[f'order_of_ordinal_{feature}'] = list()
                            # st.session_state[f'data_restrictions_{feature}_ordinal'] = \
                            # st.session_state['unique_values_dict'][feature]
                            for unique_values in st.session_state.first_unique_values_dict[feature]:
                                dictionary_values = {'name': unique_values}
                                data.append(str(unique_values))
                                st.session_state[f'order_of_ordinal_{feature}'] = data
                        else:
                            data = st.session_state[f'order_of_ordinal_{feature}']


                        st.session_state[f'order_of_ordinal_{feature}'] = sort_items(data, key = f"order_{feature}_widget")

                        st.session_state['first_unique_values_dict'][feature] = st.session_state[f'order_of_ordinal_{feature}']
                        # st.session_state[f'data_restrictions_{feature}_ordinal'] = st.session_state[f'order_of_ordinal_{feature}']


            if st.button("Upload values",help="All values must be uploaded for further processing.",type="primary"):
                st.info("This process may take a while")
                determinationNameUUID = 'DeterminationOfUniqueValuesOfFeature_'
                determinationName = 'DeterminationOfUniqueValuesOfFeature'
                label = '"detUniqueValuesOfFeature"@en'
                dicName = 'unique_values_of_features_dic'
                name = 'UniqueValuesOfFeature'
                rprovName = 'uniqueValues'
                try:
                    ending_time = getTimestamp()
                    uuid_determinationUniqueValues = determinationActivity(host_upload,determinationName, label, starting_time, ending_time)
                    uploadUniqueValues(host_upload,host,st.session_state["first_unique_values_dict"], st.session_state["level_of_measurement_dic"], uuid_determinationUniqueValues, name,
                              rprovName)
                    time = getTimestamp()
                    st.experimental_rerun()
                except Exception as e:
                    st.write(e)
        if st.session_state.unique_values_dict != {}:
            st.success("Unique values uploaded")
            if st.button("Show ordered unique values"):
                st.write(st.session_state['unique_values_dict'])






if optionsDataUnderstanding == "Volatility":

    determinationNameUUID = 'DeterminationOfVolatilityOfFeature_'
    determinationName = 'DeterminationOfVolatilityOfFeature'
    label = "detVolatilityOfFeature"
    dicName = 'volatility_of_features_dic'
    name = 'VolatilityOfFeature'
    rprovName = 'volatilityLevel'



    if st.session_state["volatility_of_features_dic"] == {}:
        st.markdown("""
        **So far no levels are set for the individual features**

        If you want to change the volatility click on the expander below.
        """)

        with st.expander("Click here to changes volatility of features"):
            starting_time = getTimestamp()
            options = ['High Volatility', 'Medium Volatility', 'Low Volatility']
            with st.form("Change level of volatility for features"):

                for index, row in st.session_state.dataframe_feature_names["featureName.value"].items():
                    st.session_state["volatility_of_features_dic"][row] = selectbox(row, options=options, key=f'volatility_of_features_{row}')

                if st.form_submit_button("Submit", type="primary"):
                    if None in st.session_state["volatility_of_features_dic"].values():
                        st.error("Please select a volatility level for all features")
                        st.stop()
                    ending_time = getTimestamp()
                    uuid_determinationVolatility = determinationActivity(host_upload, determinationName, label,starting_time, ending_time)
                    uploadDUE(host_upload,host,st.session_state["volatility_of_features_dic"], uuid_determinationVolatility, name,
                              rprovName)


    else:
        st.markdown("""
        **Here you can see which volatility levels are chosen for each feature**

        If you want to change the volatility levels click on the button below.
        """)
        st.write(st.session_state["volatility_of_features_dic"])
        if st.button("Change Volatility",on_click=deleteWasGeneratedByDUA,args=(host_upload,st.session_state["DF_feature_volatility_name"])):
            pass
if optionsDataUnderstanding == "Data Restrictions":

    # TODO insert option for ordinal data to be selected with slider


    st.markdown("""
    **Here you can see set the data restrictions for each feature**
    
    Based on the level of measurement different options are available.
    * Cardinal: Must be numerical
    * Ordinal: You must create an order for the features first
    * Nominal: All values are included
    """)

    if "data_restrictions_dict" not in st.session_state:
        st.session_state["data_restrictions_dict"] = dict()


    # try:
    #     uploaded_DataRestriction = getRestriction(host)
    #     data_restriction = st.selectbox("Select Data Restriction",
    #                                     options=uploaded_DataRestriction["Comment"].unique())
    #
    #     data_restriction_activity = uploaded_DataRestriction.loc[
    #         uploaded_DataRestriction["Comment"] == data_restriction]
    #     st.dataframe(data_restriction_activity[["Label", "Feature", "Comment", "Value"]].reset_index(drop=True), use_container_width=True)
    #     if st.button("Select Restriction", type="primary"):
    #         try:
    #             for key, value in st.session_state["level_of_measurement_dic"].items():
    #                 if value == "Cardinal":
    #                     defaultValuesCardinalRestriction(key)
    #                 if value == "Ordinal":
    #                     defaultValuesOrdinalRestriction(key)
    #                 if value == "Nominal":
    #                     defaultValuesNominalRestriction(key)
    #             st.session_state["data_restrictions_dict"] = getDataRestrictionSeq(
    #                 data_restriction_activity["DataRestrictionActivity"][0], host)
    #
    #
    #
    #
    #         except Exception as e:
    #             st.write(e)
    #             st.info("Dont forget to upload unique values")
    #
    #     if st.button("Deselect Restriction"):
    #         try:
    #             st.session_state["data_restrictions_dict"] = getUniqueValuesSeq(host)
    #             st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()
    #             st.session_state.data_restriction_final.update(st.session_state.data_restrictions_dict)
    #             st.session_state["flag_data_restriction"] = False
    #             st.session_state.data_restriction_URN = pd.DataFrame(columns=uploaded_DataRestriction.columns)
    #             # st.experimental_rerun()
    #         except Exception as e:
    #             st.write(e)
    #             st.write("Didnt work")
    #
    #     st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()
    #     st.session_state.data_restriction_final.update(st.session_state.data_restrictions_dict)
    #
    # except:
    #     st.info("Define Data Restriction.")
    #

    try:
        if "data_restriction_URN" not in st.session_state:
            st.session_state.data_restriction_URN = pd.DataFrame(columns=uploaded_DataRestriction.columns)
        if st.session_state.data_restriction_URN.empty:
            st.error("No Data Restriction selected selected")
        else:
            st.success("Data Restriction option selected")
        data_restriction = st.selectbox("Select Data Restriction",
                                        options=uploaded_DataRestriction["Comment"].unique())

        data_restriction_activity = uploaded_DataRestriction.loc[
            uploaded_DataRestriction["Comment"] == data_restriction]
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
                st.session_state["data_restrictions_dict"] = getDataRestrictionSeq(
                    data_restriction_activity["DataRestrictionActivity"][0], host)

                st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()

                st.session_state.data_restriction_final.update(st.session_state.data_restrictions_dict)
                st.experimental_rerun()






            except Exception as e:
                st.write(e)
                st.info("Dont forget to upload unique values")

        if st.button("Deselect Restriction"):
            try:

                st.session_state["data_restrictions_dict"] = dict()
                # st.session_state["data_restrictions_dict"] = getUniqueValuesSeq(host)
                st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()
                # st.session_state.data_restriction_final.update(st.session_state.data_restrictions_dict)
                # st.session_state["flag_data_restriction"] = False
                st.session_state.data_restriction_URN = pd.DataFrame(columns=uploaded_DataRestriction.columns)
                st.experimental_rerun()
            except Exception as e:
                st.write(e)
                st.write("Didnt work")


    except Exception as e:
        st.info("No Data Restrictions defined")
    starting_time = getTimestamp()


    placeholder = st.empty()

    tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])
    for key, values in st.session_state.level_of_measurement_dic.items():
        data_restrictions_dic = dict()
        data = list()
        if values == 'Cardinal':
            with tab1:
                with st.expander(f"Define Data Restrictions for ***{key}***"):
                    col1, col2, col3 = st.columns([0.05, 10, 0.5])
                    with col2:



                        # mit is digit prüfen ob int oder float
                        if f'data_restrictions_{key}_cardinal' not in st.session_state:
                            defaultValuesCardinal(key)


                        if key in st.session_state.data_restrictions_dict.keys():
                            st.session_state[f'data_restrictions_{key}_cardinal'] = [float(s) for s in st.session_state.data_restrictions_dict[key]]



                        if st.button(f"Default Values for {key}", key=f'defaultValuesCardinal_{key}', type="secondary"):
                            defaultValuesCardinal(key)




                        try:
                            lower = round(st.number_input("Input value", min_value=float(
                                st.session_state.unique_values_dict[key][0]),key=f"lower_{key}",value =float(st.session_state[f'data_restrictions_{key}_cardinal'][0])),2)
                            upper = round(st.number_input("Input upper value",key=f"upper_{key}",min_value=lower, max_value=float(
                                    st.session_state.unique_values_dict[key][-1]), value =float(st.session_state[f'data_restrictions_{key}_cardinal'][-1]) ),2)
                            if st.button("OK",key=f"data_restriction_ok_widget_{key}"):
                                if st.session_state[f"lower_{key}"] >= st.session_state[f"upper_{key}"]:
                                    st.error("Lower bound range must be smaller than upper bound.")
                                else:

                                    st.session_state[f'data_restrictions_{key}'] = [lower,
                                                                                             upper]
                                    st.session_state[f'data_restrictions_{key}_cardinal'] = [lower,
                                                                                             upper]  # st.session_state[f'data_restrictions_{key}']
                                    st.session_state['data_restrictions_dict'][key] = [lower,
                                                                                upper]  # st.session_state[f'data_restrictions_{key}']
                                    update_data_restrictions_cardinal(key)
                        except Exception as e:
                            st.write(e)
                            st.error("Lower bound range must be smaller than upper bound.")

        if values == 'Ordinal':
            with tab2:
                with st.expander(f"Define Data Restrictions for ***{key}***"):
                    col1, col2, col3 = st.columns([0.05, 10, 0.5])
                    with col2:

                        if f'data_restrictions_{key}_ordinal' not in st.session_state:
                            defaultValuesOrdinal(key)

                        if key in st.session_state.data_restrictions_dict.keys():
                            st.session_state[f'data_restrictions_{key}_ordinal'] = [s for s in
                                                                                     st.session_state.data_restrictions_dict[
                                                                                         key]]

                        if st.button(f"Default Values for {key}", key=f'defaultValuesOrdinal_{key}'):
                            defaultValuesOrdinal(key)
                        st.session_state[f'data_restrictions_{key}_ordinal'] = st.multiselect(
                            f"Select Values for Ordinal Value {key}",
                            options=st.session_state[f'data_restrictions_{key}_ordinal'],
                            default=st.session_state[f'data_restrictions_{key}_ordinal'],
                            key=f'data_restrictions_{key}',
                            on_change=update_data_restrictions_ordinal,
                            args=(key,))
                        st.markdown("""---""")

        if values == 'Nominal':
            with tab3:
                with st.expander(f"Define Data Restrictions for ***{key}***"):
                    col1, col2, col3 = st.columns([0.05, 10, 0.5])
                    with col2:

                        if f'data_restrictions_{key}_nominal' not in st.session_state:
                            defaultValuesNominal(key)
                        if st.button(f"Default Values for {key}", key=f'defaultValuesNominal_{key}'):
                            defaultValuesNominal(key)
                        st.session_state[f'data_restrictions_{key}_nominal'] = st.multiselect(
                            f"Select Values for Nominal Value {key}",
                            options=st.session_state.unique_values_dict[key],
                            default=st.session_state[f'data_restrictions_{key}_nominal'],
                            key=f'data_restrictions_{key}',
                            on_change=update_data_restrictions_nominal,
                            args=(key,))
                        st.markdown("""---""")




    is_unique = False

    if st.session_state['data_restrictions_dict'] == {}:
     st.stop()
    else:
        st.write("-------------")
        with st.expander("Defined Data Restriction"):
            st.write(st.session_state['data_restrictions_dict'])
        with placeholder.container():

            with st.form("Insert label for the defined Data Restriction"):
                st.info("This label will be shown for the defined Data Restrictions. If a label is used more than once it might lead to problems.")
                comment_data_restriction = st.text_input("Insert label for the defined Data Restrictions",
                                                  help="Name your Data Restrictions in order to find it easier later.")

                if st.form_submit_button("Upload Data Restrictions", type="primary", help="Upload the defined Data Restrictions."):
                    uploadDR(starting_time, host_upload, host, comment_data_restriction)


                    dr_success = st.success("Data Restriction uploaded")
                    time.sleep(2)
                    dr_success.empty()
                    st.experimental_rerun()




if optionsDataUnderstanding == "Feature Sensor Precision":
    # TODO insert DeterminationOfSensorPrecisionOfFeature_ to fuseki general graph
    determinationNameUUID = 'DeterminationOfSensorPrecisionOfFeature_'
    determinationName = 'DeterminationOfSensorPrecisionOfFeature'
    label = '"detSensorPrecisionOfFeature"@en'
    dicName = 'SensorPrecision_of_features_dic'
    name = 'SensorPrecisionOfFeature'
    rprovName = 'SensorPrecisionLevel'
    ending_time = getTimestamp()

    starting_time = getTimestamp()






    if st.session_state["loaded_feature_sensor_precision_dict"] == {}:
        st.markdown("""
        **So far no levels are set for the individual features**

        If you want to change the volatility click on the expander below.
        """)

        # TODO muss noch in fuseki gespeichert werden

        for key, values in st.session_state.level_of_measurement_dic.items():

            if values == 'Cardinal':

                with st.expander(f"Define sensor precision for {key} in percent", help="the measured value is correct within the defined percentage range"):

                    if "feature_sensor_precision_dict" not in st.session_state:
                        st.session_state[f"feature_sensor_precision_dict"] = dict()

                    if key in st.session_state["feature_sensor_precision_dict"]:
                        st.session_state[f'feature_sensor_precision_{key}'] = \
                        st.session_state["feature_sensor_precision_dict"][key]
                    else:
                        st.session_state[f'feature_sensor_precision_{key}'] = 0

                    st.session_state[f'feature_sensor_precision_{key}'] = round(st.number_input("Define sensor precision",
                                                                                          min_value=float(0.00),
                                                                                          max_value=float(100),
                                                                                          value=float(st.session_state[
                                                                                                          f'feature_sensor_precision_{key}']),
                                                                                          key=f'feature_sensor_precision_{key}_widget',
                                                                                          on_change=update_feature_sensor_precision,
                                                                                          args=(key,)),2)
        try:
            st.info("Sensor precision for feature will be uploaded if bigger 0.00")
        except:
            st.info("No Cardinal values determined in this dataset")
        if st.button("Submit", type="primary"):
            uuid_determinationSensorPrecision = determinationActivity(host_upload, determinationName,
                                                                 label,
                                                                 starting_time, ending_time)
            uploadDUE(host_upload, host, st.session_state["feature_sensor_precision_dict"],
                      uuid_determinationSensorPrecision, name,
                      rprovName)
            st.session_state["loaded_feature_sensor_precision_dict"] = st.session_state["feature_sensor_precision_dict"]
            Sensor_success = st.success("Sensor Precision uploaded")
            time.sleep(2)
            Sensor_success.empty()
            st.experimental_rerun()


    else:
        st.markdown("""
        **Here you can see which sensor precisions are chosen for each feature**

        If you want to change the sensor precisions click on the button below.
        """)
        st.write(st.session_state["loaded_feature_sensor_precision_dict"])
        st.write(st.session_state["DF_feature_sensor_precision"])

        if st.button("Change Sensor Precision"):


            st.session_state["loaded_feature_sensor_precision_dict"], st.session_state["DF_feature_sensor_precision"] = getSensorPrecision(host)

            deleteWasGeneratedByDUA(host_upload,st.session_state["DF_feature_sensor_precision"])

            del st.session_state["loaded_feature_sensor_precision_dict"]

            st.experimental_rerun()
