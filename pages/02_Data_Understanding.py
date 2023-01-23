import statistics

import pandas as pd
from functions.functions_Reliability import *
from functions.functions_DataUnderstanding import *
from functions.fuseki_connection import *
import streamlit_nested_layout
from streamlit_sortables import sort_items

try:
    host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
    host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
except:
    st.info("Please select a database first")
    st.stop()

try:
    getAttributes(host)
except:
    st.error("Please select other Database")
    st.stop()

if st.session_state.dataframe_feature_names.empty:
    st.stop()

optionsDataUnderstanding = option_menu("Data Understanding Options", ["Scale", "Volatility", "Data Restrictions", "Feature Sensor Precision"],
                                       icons=['collection', 'arrow-down-up', 'slash-circle'],
                                       menu_icon="None", default_index=0, orientation="horizontal")
# if "first_load" not in st.session_state:
#     st.session_state.first_load = True
#     getAttributes(host)
# else:
#     st.session_state.first_load = False

# if st.session_state.first_load is False:
#     getAttributes(host)

# if not any(key.startswith('level_of_measurement_') for key in st.session_state):
#     st.session_state["dataframe_feature_names"] = get_feature_names(host)
#
# try:
#     st.session_state["level_of_measurement_dic"], st.session_state["DF_feature_scale_name"] = getFeatureScale(host)
#     for key, value in st.session_state["level_of_measurement_dic"].items():
#         st.session_state[f'level_of_measurement_{key}'] = value
# except:
#     st.session_state["DF_feature_scale_name"] = pd.DataFrame()
#     #st.session_state["level_of_measurement_dic"] = dict()
#
#
# try:
#     st.session_state["volatility_of_features_dic"], st.session_state["DF_feature_volatility_name"] = getFeatureVolatility(host)
# except:
#     st.session_state["volatility_of_features_dic"] = dict()
#
# try:
#     st.session_state["unique_values_dict"] = getUniqueValuesSeq(host)
# except Exception as e:
#     st.error("No Unique Values in database. If this is the first time a new dataset is uploaded please define a scale for each feature and upload the unique values.")
#
# # if "loaded_feature_sensor_precision_dict" not in st.session_state:
# try:
#     st.session_state["loaded_feature_sensor_precision_dict"], st.session_state[
#         "DF_feature_sensor_precision"] = getSensorPrecision(host)
# except:
#     st.session_state["loaded_feature_sensor_precision_dict"] = dict()
#     st.session_state["DF_feature_sensor_precision"] = pd.DataFrame()




# Hier kann die scale ausgewählt werden
if optionsDataUnderstanding == "Scale":

    determinationName = 'DeterminationOfScaleOfFeature'
    label = '"detScaleOfFeature"@en'
    dicName = 'level_of_measurement_dic'
    name = 'ScaleOfFeature'
    rprovName = 'scale'



    # wenn noch keine scale in fuseki bestimmt wurde, erstelle Form mit auswahl von scales
    if st.session_state["level_of_measurement_dic"] == {}:
        with st.expander("Click here to changes scale of features"):
            starting_time = getTimestamp()

            with st.form("Change level of measurement for features"):
                options = ['Ordinal', 'Cardinal', 'Nominal']

                for index, row in st.session_state.dataframe_feature_names["featureName.value"].items():
                    if (f'level_of_measurement_{row}') not in st.session_state:
                        st.session_state[f'level_of_measurement_{row}'] = "Nominal"
                    # wenn level of measurement dictionary nicht leer ist gibt es die level of measurement an
                    st.session_state.level_of_measurement_dic[row] = st.selectbox(row, options=options, index=2,key=f'level_of_measurement_{row}_widget')

                # submit selected scale of measurements
                if st.form_submit_button("Submit", type="primary"):
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
        # if st.button("Change level of measurement", type="primary"):
        #
        #     del st.session_state["level_of_measurement_dic"]
        #     deleteWasGeneratedByDUA(host_upload,st.session_state["DF_feature_scale_name"], determinationName)
        #     st.experimental_rerun()

        colored_header(
            label="Order of ordinal features",
            description="""Open the expander for the feature to change the order. 
                        """,
            color_name="red-70",
        )

        try:
            getUniqueValuesSeq(host)

        except Exception as e:
            st.error(
                "Until now, this step must still be done in one piece. If the page is changed or the browser is refreshed, errors still occur!")
            for feature, scale in st.session_state["level_of_measurement_dic"].items():
                starting_time = getTimestamp()
                #data_restrictions_dic = dict()
                data = list()
                if scale == "Cardinal":
                    st.session_state['unique_values_dict'][feature] = [
                        min(st.session_state['unique_values_dict'][feature]),
                        max(st.session_state['unique_values_dict'][feature])]
                if scale == 'Ordinal':
                    with st.expander(f"Define Order for {feature}"):
                        # wenn es noch keine session_state gibt, erstelle eine leere liste welche im anschluss mit den daten von den unique values gefüllt wird
                        # falls es eine session_state gibt, übergib die session state an die liste
                        if f'order_of_ordinal_{feature}' not in st.session_state:
                            st.session_state[f'order_of_ordinal_{feature}'] = list()
                            # st.session_state[f'data_restrictions_{feature}_ordinal'] = \
                            # st.session_state['unique_values_dict'][feature]
                            for unique_values in st.session_state.unique_values_dict[feature]:
                                dictionary_values = {'name': unique_values}
                                data.append(str(unique_values))
                                # data.append(dictionary_values)
                                st.session_state[f'order_of_ordinal_{feature}'] = data
                        else:
                            data = st.session_state[f'order_of_ordinal_{feature}']


                        st.session_state[f'order_of_ordinal_{feature}'] = sort_items(data, key = f"order_{feature}_widget")

                        st.session_state['unique_values_dict'][feature] = st.session_state[f'order_of_ordinal_{feature}']
                        # st.session_state[f'data_restrictions_{feature}_ordinal'] = st.session_state[f'order_of_ordinal_{feature}']


            if st.button("Upload unique values",help="This information is needed for further steps in the CRISP-DM model. Based on those values data restrictions can be modeled.",type="primary"):
                determinationNameUUID = 'DeterminationOfUniqueValuesOfFeature_'
                determinationName = 'DeterminationOfUniqueValuesOfFeature'
                label = '"detUniqueValuesOfFeature"@en'
                dicName = 'unique_values_of_features_dic'
                name = 'UniqueValuesOfFeature'
                rprovName = 'uniqueValues'
                try:
                    ending_time = getTimestamp()
                    uuid_determinationUniqueValues = determinationActivity(host_upload,determinationName, label, starting_time, ending_time)
                    uploadUniqueValues(host_upload,host,st.session_state["unique_values_dict"], st.session_state["level_of_measurement_dic"], uuid_determinationUniqueValues, name,
                              rprovName)
                    time = getTimestamp()
                    st.experimental_rerun()
                except Exception as e:
                    st.write(e)


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
                    if (f'volatility_of_feature_{row}') not in st.session_state:
                        st.session_state[f'volatility_of_feature_{row}'] = "Low Volatility"
                    try:
                        _index = options.index(st.session_state[f'volatility_of_feature_{row}'])
                    except:
                        _index = 1
                    st.session_state["volatility_of_features_dic"][row] = st.selectbox(row, options=options, index=2,
                                                                                       key=f'volatility_of_features_{row}')

                if st.form_submit_button("Submit", type="primary"):
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
        if st.button("Change Volatility"):
            deleteWasGeneratedByDUA(host_upload,st.session_state["DF_feature_volatility_name"])
            st.experimental_rerun()

if optionsDataUnderstanding == "Data Restrictions":

    # TODO insert option for ordinal data to be selected with slider


    st.markdown("""
    **Here you can see set the data restrictions for each feature**
    
    Based on the level of measurement different options are available.
    * Cardinal: Must be numerical
    * Ordinal: You must create an order for the features first
    * Nominal: All values are included
    """)

    getDefault(host)

    if "data_restrictions_dict" not in st.session_state:
        st.session_state["data_restrictions_dict"] = dict()



    try:
        uploaded_dataRestriction = getRestriction(host)
        data_restriction = st.selectbox("Select Data Restriction", options=uploaded_dataRestriction["DataRestrictionActivity"].unique())

        st.write(uploaded_dataRestriction.loc[uploaded_dataRestriction["DataRestrictionActivity"] == data_restriction])
        if st.button("get Restriction"):
            try:
                for key, value in st.session_state["level_of_measurement_dic"].items():
                    if value == "Cardinal":
                        defaultValuesCardinalRestriction(key)
                    if value =="Ordinal":
                        defaultValuesOrdinalRestriction(key)
                    if value =="Nominal":
                        defaultValuesNominalRestriction(key)
                st.session_state["data_restrictions_dict"] = getDataRestrictionSeq(data_restriction, host)


            except Exception as e:
                st.write(e)
                st.info("Dont forget to upload unique values")


        st.session_state["data_restriction_final"]  = st.session_state.unique_values_dict.copy()
        st.session_state.data_restriction_final.update(st.session_state.data_restrictions_dict)
    except:
        st.info("No data restrictions defined yet.")



    tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])
    starting_time = getTimestamp()

    if st.button("submit"):
        determinationNameUUID = 'DeterminationOfDataRestriction'
        determinationName = 'DeterminationOfDataRestriction'
        label = "detDataRestriction"
        name = 'DataRestriction'
        rprovName = 'DataRestriction'
        ending_time = getTimestamp()
        uuid_determinationDataRestriction = determinationActivity(host_upload, determinationName, label,
                                                             starting_time, ending_time)
        uploadDataRestrictionSeq(host_upload, host, st.session_state['data_restrictions_dict'], uuid_determinationDataRestriction, name,
                  rprovName)


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



                        # TODO change input of cardinal values to number input
                        # st.session_state[f'data_restrictions_{key}_cardinal'] = st.slider(
                        #     f"Select Range for Cardinal Value {key}",
                        #     value=st.session_state[f'data_restrictions_{key}_cardinal'],
                        #     min_value=float(
                        #         st.session_state.unique_values_dict[key][0]),
                        #     max_value=float(
                        #         st.session_state.unique_values_dict[key][-1]),
                        #     key=f'data_restrictions_{key}',
                        #     on_change=update_data_restrictions_cardinal,
                        #     step=float(step),
                        #     args=(key,))

                        with st.expander("Number input"):
                            lower = st.number_input("Input value", min_value=float(
                                st.session_state.unique_values_dict[key][0]),value =float(st.session_state[f'data_restrictions_{key}_cardinal'][0]))
                            upper = st.number_input("Input upper value",min_value=lower, max_value=float(
                                    st.session_state.unique_values_dict[key][-1]), value =float(st.session_state[f'data_restrictions_{key}_cardinal'][-1]) )

                            if lower >= upper:
                                st.error("Lower bound range must be smaller than upper bound.")
                            elif st.button("Upload", key = f"button_dataRestriction_{key}", type="primary"):
                                st.session_state[f'data_restrictions_{key}_cardinal'] = [lower,
                                                                                         upper]  # st.session_state[f'data_restrictions_{key}']
                                st.session_state['data_restrictions_dict'][key] = [lower,
                                                                                   upper]  # st.session_state[f'data_restrictions_{key}']

                            # update_data_restrictions_cardinal(key, lower, upper )
                            # st.session_state[f'data_restrictions_{key}_cardinal'] = [lower, upper]
                            # st.session_state['data_restrictions_dict'][key] = [lower, upper]

                        # TODO change input of cardinal values to number input

                        step = st.number_input("Define stepsize",min_value=0.01, max_value=float(
                                st.session_state.unique_values_dict[key][-1]), step=0.01, key =f"step_cardinal_{key}")
                        st.session_state[f'data_restrictions_{key}_cardinal'] = st.slider(
                            f"Select Range for Cardinal Value {key}",
                            value=st.session_state[f'data_restrictions_{key}_cardinal'],
                            min_value=float(
                                st.session_state.unique_values_dict[key][0]),
                            max_value=float(
                                st.session_state.unique_values_dict[key][-1]),
                            key=f'data_restrictions_{key}',
                            on_change=update_data_restrictions_cardinal,
                            step=float(step),
                            args=(key,))


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

    st.write(st.session_state["data_restrictions_dict"])

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
        st.info("Sensor precision for feature will be uploaded if bigger 0.00")
        for key, values in st.session_state.level_of_measurement_dic.items():

            if values == 'Cardinal':

                with st.expander(f"Define sensor precision for {key}"):

                    if "feature_sensor_precision_dict" not in st.session_state:
                        st.session_state[f"feature_sensor_precision_dict"] = dict()

                    if key in st.session_state["feature_sensor_precision_dict"]:
                        st.session_state[f'feature_sensor_precision_{key}'] = \
                        st.session_state["feature_sensor_precision_dict"][key]
                    else:
                        st.session_state[f'feature_sensor_precision_{key}'] = 0

                    st.session_state[f'feature_sensor_precision_{key}'] = st.number_input("Define sensor precision",
                                                                                          min_value=float(0.00),
                                                                                          max_value=float(100),
                                                                                          value=float(st.session_state[
                                                                                                          f'feature_sensor_precision_{key}']),
                                                                                          key=f'feature_sensor_precision_{key}_widget',
                                                                                          on_change=update_feature_sensor_precision,
                                                                                          args=(key,))

        st.write(st.session_state["feature_sensor_precision_dict"])

        if st.button("Submit", type="primary"):
            uuid_determinationSensorPrecision = determinationActivity(host_upload, determinationName,
                                                                 label,
                                                                 starting_time, ending_time)
            uploadDUE(host_upload, host, st.session_state["feature_sensor_precision_dict"],
                      uuid_determinationSensorPrecision, name,
                      rprovName)
            st.session_state["loaded_feature_sensor_precision_dict"] = st.session_state["feature_sensor_precision_dict"]
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
            del st.session_state["feature_sensor_precision_dict"]
            del st.session_state["loaded_feature_sensor_precision_dict"]

            st.experimental_rerun()
