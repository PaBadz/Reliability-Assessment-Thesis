import time

import pandas as pd
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
from streamlit_sortables import sort_items

from functions.functions_DataUnderstanding import update_feature_sensor_precision, defaultValuesCardinal, \
    update_data_restrictions_cardinal, defaultValuesOrdinal, update_data_restrictions_ordinal, defaultValuesNominal, \
    update_data_restrictions_nominal
from functions.functions_Reliability import defaultValuesCardinalRestriction, defaultValuesOrdinalRestriction, \
    defaultValuesNominalRestriction, getRestriction
from functions.functions_Reliability import getDefault
from functions.fuseki_connection import login, getTimestamp, determinationActivity, uploadDUE, \
    deleteWasGeneratedByDUA, getUniqueValuesSeq, uploadDR, getSensorPrecision, uploadUniqueValues, \
    getDataRestrictionSeq, getAttributesDataUnderstanding, get_feature_names, get_dataset, uploadDUE_scale

login()
host, host_upload = get_dataset()

try:
    st.session_state.dataframe_feature_names = get_feature_names(host)
except Exception as e:
    st.error(e)

if st.session_state.dataframe_feature_names.empty:
    try:
        getUniqueValuesSeq(host)

    except Exception as e:
        st.error("Please upload dataset in Home")
        if st.button("Home"):
            switch_page("Home")
        if "first_unique_values_dict" not in st.session_state:
            st.error("No unique values available, please upload dataset again.")
        st.stop()
    st.stop()


optionsDataUnderstanding = option_menu("Data Understanding Options",
                                       ["Scale", "Volatility", "Data Restrictions", "Feature Sensor Precision"],
                                       icons=['collection', 'arrow-down-up', 'slash-circle', 'broadcast'],
                                       menu_icon="None", default_index=0, orientation="horizontal")

with st.expander("Show information"):
    try:
        getAttributesDataUnderstanding(host)
    except Exception as e:
        pass
    try:
        # TODO include data restriction in getAttributes
        uploaded_DataRestriction = getRestriction(host)
        st.session_state["data_restrictions_dict"] = getDataRestrictionSeq(
            uploaded_DataRestriction["DUA.value"][0], host)
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
        st.warning(
            "Please insert level of scale for each feature! This is an important step and cannot be changed after uploading unique values.")
        with st.expander("Click here to changes scale of features"):
            st.markdown(
                """
                - **Cardinal**: only minimum and maximum values are saved. **:red[Must be numerical]**
                - **Ordinal**: ordered values, which can be arranged in the next step
                - **Nominal**: all values are saved with no further ordering"""
            )

            with st.form("Change level of measurement for features"):
                options = ['Cardinal', 'Ordinal', 'Nominal']

                for index, row in st.session_state.dataframe_feature_names["featureName.value"].items():
                    if f'level_of_measurement_{row}' not in st.session_state:
                        st.session_state[f'level_of_measurement_{row}'] = ' '
                    # wenn level of measurement dictionary nicht leer ist gibt es die level of measurement an

                    st.session_state.level_of_measurement_dic[row] = selectbox(f"**{row}**", options=options,
                                                                               key=f'level_of_measurement_{row}_widget')

                st.session_state.level_of_measurement_dic

                # submit selected scale of measurements
                if st.form_submit_button("Submit", type="primary"):

                    if None in st.session_state.level_of_measurement_dic.values():
                        st.error("Please select a level of measurement for all features")
                        st.stop()
                    ending_time = getTimestamp()
                    uuid_determinationScale = determinationActivity(host_upload, determinationName, label,
                                                                    ending_time)
                    uploadDUE_scale(host_upload, host, st.session_state["level_of_measurement_dic"], uuid_determinationScale,
                              name,
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
                    deleteWasGeneratedByDUA(host_upload, st.session_state["DF_feature_scale_name"])
                    st.experimental_rerun()
                st.error(
                    "Please define order of ordinal features and upload!")
                st.warning(
                    "If these steps are not completed at the beginning, this will result in errors and the app will not run properly.!")
        colored_header(
            label="Unique feature values",
            description="""Open the expander for the feature to change the order and upload unique values afterwards!
                        """,
            color_name="red-70",
        )

        try:

            getUniqueValuesSeq(host)




        except Exception as e:
            if "first_unique_values_dict" not in st.session_state:
                st.error("No unique values available, please upload dataset again.")
                st.stop()



            for feature, scale in st.session_state["level_of_measurement_dic"].items():
                # data_restrictions_dic = dict()
                data = list()
                if scale == "Cardinal":



                    try:
                        float(min(st.session_state['first_unique_values_dict'][feature]))
                    except:
                        st.error(f"Feature {feature} is not numerical. Please change!")
                        st.stop()
                    st.session_state['first_unique_values_dict'][feature] = [
                        min(st.session_state['first_unique_values_dict'][feature]),
                        max(st.session_state['first_unique_values_dict'][feature])]
                if scale == 'Ordinal':
                    with st.expander(f"Define Order for {feature}"):
                        # wenn es noch keine session_state gibt, erstelle eine leere liste welche im anschluss mit den daten von den unique values gefüllt wird
                        # falls es eine session_state gibt, übergib die session state an die liste
                        if f'order_of_ordinal_{feature}' not in st.session_state:
                            st.session_state[f'order_of_ordinal_{feature}'] = list()
                            for unique_values in st.session_state.first_unique_values_dict[feature]:
                                dictionary_values = {'name': unique_values}
                                data.append(str(unique_values))
                                st.session_state[f'order_of_ordinal_{feature}'] = data
                        else:
                            data = st.session_state[f'order_of_ordinal_{feature}']

                        st.session_state[f'order_of_ordinal_{feature}'] = sort_items(data,
                                                                                     key=f"order_{feature}_widget")

                        st.session_state['first_unique_values_dict'][feature] = st.session_state[
                            f'order_of_ordinal_{feature}']
            st.error("Please define order of ordinal features and upload!")
            if st.button("Upload values", help="All values must be uploaded for further processing.", type="primary"):
                determinationNameUUID = 'DeterminationOfUniqueValuesOfFeature_'
                determinationName = 'DeterminationOfUniqueValuesOfFeature'
                label = '"detUniqueValuesOfFeature"@en'
                dicName = 'unique_values_of_features_dic'
                name = 'UniqueValuesOfFeature'
                rprovName = 'uniqueValues'
                try:
                    ending_time = getTimestamp()
                    uuid_determinationUniqueValues = determinationActivity(host_upload, determinationName, label, ending_time)
                    uploadUniqueValues(host_upload, host, st.session_state["first_unique_values_dict"],
                                       st.session_state["level_of_measurement_dic"], uuid_determinationUniqueValues,
                                       name,
                                       rprovName)
                    time = getTimestamp()

                except Exception as e:
                    st.write(e)
                st.experimental_rerun()
        if st.session_state.unique_values_dict != {}:
            st.success("Unique values uploaded")
            with st.expander("Show ordered unique values"):
                st.write(st.session_state['unique_values_dict'])

if optionsDataUnderstanding == "Volatility":

    try:
        getUniqueValuesSeq(host)

    except Exception as e:
        st.error("Please upload feature values in Data Understanding Step")
        st.stop()

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
            options = ['High Volatility', 'Medium Volatility', 'Low Volatility']
            with st.form("Change level of volatility for features"):

                for index, row in st.session_state.dataframe_feature_names["featureName.value"].items():
                    st.session_state["volatility_of_features_dic"][row] = selectbox(row, options=options,
                                                                                    key=f'volatility_of_features_{row}')

                if st.form_submit_button("Submit", type="primary"):
                    if None in st.session_state["volatility_of_features_dic"].values():
                        st.error("Please select a volatility level for all features")
                        st.stop()
                    ending_time = getTimestamp()
                    uuid_determinationVolatility = determinationActivity(host_upload, determinationName, label,
                                                                          ending_time)
                    uploadDUE(host_upload, host, st.session_state["volatility_of_features_dic"],
                              uuid_determinationVolatility, name,
                              rprovName)


    else:
        st.markdown("**Here you can see the Volatility  for each feature**")
        with st.expander("Show Volatility"):
            st.write(st.session_state["volatility_of_features_dic"])
        if st.button("Delete Volatility", on_click=deleteWasGeneratedByDUA,
                     args=(host_upload, st.session_state["DF_feature_volatility_name"]),
                     help="Old values will be invalid and new volatility levels can be created"):
            pass
if optionsDataUnderstanding == "Data Restrictions":
    try:
        getUniqueValuesSeq(host)

    except Exception as e:
        st.error("Please upload feature values in Data Understanding Step")
        st.stop()

    uploaded_DataRestriction = getRestriction(host)
    if "data_restrictions_dict" not in st.session_state:
        st.session_state.data_restrictions_dict = dict()
    if st.session_state['data_restrictions_dict'] is None:
        st.session_state['data_restrictions_dict'] = dict()
    if uploaded_DataRestriction.empty:
        st.markdown("""
        **Here you can set the Data Restrictions for each feature**
        """)
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

                            try:
                                if key in st.session_state.data_restrictions_dict.keys():
                                    st.session_state[f'data_restrictions_{key}_cardinal'] = [float(s) for s in
                                                                                             st.session_state.data_restrictions_dict[
                                                                                                 key]]
                            except:
                                pass

                            if st.button(f"Default Values for {key}", key=f'defaultValuesCardinal_{key}',
                                         type="secondary"):
                                defaultValuesCardinal(key)

                            try:
                                lower = round(st.number_input("Input lower value", min_value=float(
                                    st.session_state.unique_values_dict[key][0]), key=f"lower_{key}", value=float(
                                    st.session_state[f'data_restrictions_{key}_cardinal'][0])), 2)
                                upper = round(st.number_input("Input upper value", key=f"upper_{key}", min_value=lower,
                                                              max_value=float(
                                                                  st.session_state.unique_values_dict[key][-1]),
                                                              value=float(
                                                                  st.session_state[f'data_restrictions_{key}_cardinal'][
                                                                      -1])), 2)
                                if st.button("Ok", key=f"data_restriction_ok_widget_{key}", type="primary"):
                                    if st.session_state[f"lower_{key}"] >= st.session_state[f"upper_{key}"]:
                                        st.error("Lower bound range must be smaller than upper bound.")
                                    else:

                                        st.session_state[f'data_restrictions_{key}'] = [lower,
                                                                                        upper]
                                        st.session_state[f'data_restrictions_{key}_cardinal'] = [lower,
                                                                                                 upper]
                                        st.session_state['data_restrictions_dict'][key] = [lower,
                                                                                           upper]
                                        update_data_restrictions_cardinal(key)
                                        st.success(f"Data Restriction for {key} saved, please upload when finished.")
                            except Exception as e:
                                st.write(e)
                                st.error("Lower bound range must be smaller than upper bound.")

            if values == 'Ordinal':
                with tab2:
                    with st.expander(f"Define Data Restrictions for ***{key}***"):

                        if f'data_restrictions_{key}_ordinal' not in st.session_state:
                            defaultValuesOrdinal(key)
                        try:
                            if key in st.session_state.data_restrictions_dict.keys():
                                st.session_state[f'data_restrictions_{key}_ordinal'] = [s for s in
                                                                                        st.session_state.data_restrictions_dict[
                                                                                            key]]
                        except:
                            pass

                        if st.button(f"Default Values for {key}", key=f'defaultValuesOrdinal_{key}'):
                            defaultValuesOrdinal(key)
                        st.session_state[f'data_restrictions_{key}_ordinal'] = st.multiselect(
                            f"Select Values for Ordinal Value {key}",
                            options=st.session_state.unique_values_dict[key],
                            default=st.session_state[f'data_restrictions_{key}_ordinal'],
                            key=f'data_restrictions_{key}',
                            on_change=update_data_restrictions_ordinal,
                            args=(key,))
                        st.markdown("""---""")

            if values == 'Nominal':
                with tab3:
                    with st.expander(f"Define Data Restrictions for ***{key}***"):

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

        # TODO insert option for ordinal data to be selected with slider
        if st.session_state['data_restrictions_dict'] == {}:
            st.stop()
        else:
            st.write("-------------")
            with st.expander("Defined Data Restriction"):
                st.write(st.session_state['data_restrictions_dict'])
            if st.button("Upload Data Restrictions", type="primary", help="Upload the defined Data Restrictions."):

                uploadDR(host_upload, host)

                dr_success = st.success("Data Restriction uploaded")
                dr_success.empty()
                st.experimental_rerun()

    else:
        st.markdown("""
        **Here you can see the Data Restrictions for each feature**
        """)

        for key, value in st.session_state["level_of_measurement_dic"].items():
            if value == "Cardinal":
                defaultValuesCardinalRestriction(key)
            if value == "Ordinal":
                defaultValuesOrdinalRestriction(key)
            if value == "Nominal":
                defaultValuesNominalRestriction(key)


        st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()

        st.session_state.data_restriction_final.update(st.session_state.data_restrictions_dict)

        with st.expander("Show Data Restriction"):
            st.write(st.session_state.data_restrictions_dict)

        if st.button("Delete Data Restriction",
                     help="Delete Data Restriction in order to create a new Data Restriction"):
            deleteWasGeneratedByDUA(host_upload, uploaded_DataRestriction)
            del st.session_state["data_restrictions_dict"]
            del st.session_state.data_restriction_final
            st.session_state.data_restriction_final = st.session_state.unique_values_dict.copy()
            uploaded_DataRestriction = pd.DataFrame()
            st.experimental_rerun()



if optionsDataUnderstanding == "Feature Sensor Precision":
    try:
        getUniqueValuesSeq(host)

    except Exception as e:
        st.error("Please upload feature values in Data Understanding Step")
        st.stop()
    # TODO insert DeterminationOfSensorPrecisionOfFeature_ to fuseki general graph
    determinationNameUUID = 'DeterminationOfSensorPrecisionOfFeature_'
    determinationName = 'DeterminationOfSensorPrecisionOfFeature'
    label = '"detSensorPrecisionOfFeature"@en'
    dicName = 'SensorPrecision_of_features_dic'
    name = 'SensorPrecisionOfFeature'
    rprovName = 'SensorPrecisionLevel'
    ending_time = getTimestamp()

    if st.session_state["loaded_feature_sensor_precision_dict"] == {}:
        st.markdown("""
        **Here you can set the Sensor Precision for each feature**
        """)

        # TODO muss noch in fuseki gespeichert werden

        for key, values in st.session_state.level_of_measurement_dic.items():

            if values == 'Cardinal':

                with st.expander(f"Define sensor precision for {key} in percent"):

                    if "feature_sensor_precision_dict" not in st.session_state:
                        st.session_state[f"feature_sensor_precision_dict"] = dict()

                    if key in st.session_state["feature_sensor_precision_dict"]:
                        st.session_state[f'feature_sensor_precision_{key}'] = \
                            st.session_state["feature_sensor_precision_dict"][key]
                    else:
                        st.session_state[f'feature_sensor_precision_{key}'] = 0

                    st.session_state[f'feature_sensor_precision_{key}'] = round(
                        st.number_input("Define sensor precision",
                                        min_value=float(0.00),
                                        max_value=float(100),
                                        value=float(st.session_state[
                                                        f'feature_sensor_precision_{key}']),
                                        key=f'feature_sensor_precision_{key}_widget',
                                        on_change=update_feature_sensor_precision,
                                        args=(key,),
                                        help="the measured value is correct within the defined percentage range"), 2)
        st.write("----------------------")
        if st.session_state["feature_sensor_precision_dict"] != {}:
            with st.expander("Show Feature Sensor Precision"):
                st.session_state["feature_sensor_precision_dict"]

            if st.button("Upload Feature Sensor Precision", type="primary"):
                uuid_determinationSensorPrecision = determinationActivity(host_upload, determinationName,
                                                                          label,
                                                                          ending_time)
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
        **Here you can see the Sensor Precision for each feature**
        """)
        with st.expander("Show Feature Sensor Precision"):
            st.write(st.session_state["loaded_feature_sensor_precision_dict"])

        if st.button("Delete Sensor Precision"):
            st.session_state["loaded_feature_sensor_precision_dict"], st.session_state[
                "DF_feature_sensor_precision"] = getSensorPrecision(host)

            deleteWasGeneratedByDUA(host_upload, st.session_state["DF_feature_sensor_precision"])

            del st.session_state["loaded_feature_sensor_precision_dict"]

            st.experimental_rerun()
