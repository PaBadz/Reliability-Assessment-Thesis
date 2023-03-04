from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET
import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
# from functions.functions_Reliability import *




# Fuseki Data
host_dataset_first_initialize = "http://localhost:3030/$/datasets"

prefix = """PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
            PREFIX prov:  <http://www.w3.org/ns/prov#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX instance:<http://www.semanticweb.org/dke/ontologies#>"""

def set_database():
    keep = ["fuseki_database", "name_fuseki_database", "fueski_dataset_options", "name", "authentication_status", "username"]
    for key in st.session_state.keys():
        if key in keep:
            pass
        else:
            del st.session_state[key]

    st.session_state.fuseki_database = st.session_state.name_fuseki_database

def get_connection_fuseki(host, query):
    sparql = SPARQLWrapper(host)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setMethod(GET)
    return sparql.query().convert()

def get_dataset():
    try:
        host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
        host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
        if st.session_state.fuseki_database == "None":
            st.error("Select dataset")
            st.stop()
    except:
        st.stop()
    return host, host_upload

def login():
    try:
        if st.session_state["authentication_status"] == False:
            st.error('Username/password is incorrect')
            st.stop()
        elif st.session_state["authentication_status"] == None:
            st.warning('Please enter your username and password')
            st.stop()
    except:
        st.stop()


    if st.session_state.username == "analyst" or st.session_state.username=="user":
        st.warning("Please switch to Deployment Page")
        st.stop()



def login_analyst():
    try:
        if st.session_state["authentication_status"] == False:
            st.error('Username/password is incorrect')
            st.stop()
        elif st.session_state["authentication_status"] == None:
            st.warning('Please enter your username and password')
            st.stop()
    except:
        st.stop()



def getTimestamp():
    timestamp = datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
    return timestamp



def determinationActivity(sparqlupdate, determinationName, label, ending_time):
    uuid_Determination = uuid.uuid4()
    query = (f"""INSERT DATA {{<urn:uuid:{uuid_Determination}> rdf:type rprov:{determinationName}, owl:NamedIndividual;
                rdfs:label '{label}';
                prov:endedAtTime    '{ending_time}'^^xsd:dateTime.
                }}""")
    sparqlupdate.setQuery(prefix+query)
    sparqlupdate.setMethod(POST)
    sparqlupdate.query()
    return uuid_Determination


def uploadDUE_scale(sparqlupdate,host,dic , uuid_DeterminationOfScaleOfFeature, name, rprovName):
    time = getTimestamp()
    with st.spinner("Uploading..."):
        for key, value in dic.items():
            uuid_ScaleOfFeature = uuid.uuid4()
            query = (f"""PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                        PREFIx rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    SELECT ?subject WHERE {{?subject rdf:type rprov:Feature. ?subject rdfs:label '{key}'}}""")
            results_update = get_connection_fuseki(host, query)

            result_2 = pd.json_normalize(results_update["results"]["bindings"])


            query = (f"""INSERT DATA {{<urn:uuid:{uuid_ScaleOfFeature}> rdf:type rprov:{name}, owl:NamedIndividual;
                          rprov:{rprovName} rprov:{value};
                          rdfs:label "{rprovName} {key}"@en;
                          rprov:toFeature <{result_2["subject.value"][0]}>;
                          rprov:wasGeneratedByDUA  <urn:uuid:{uuid_DeterminationOfScaleOfFeature}>;
                          prov:generatedAtTime '{time}'^^xsd:dateTime.

                        }}""")
            sparqlupdate.setQuery(prefix+query)
            sparqlupdate.setMethod(POST)
            sparqlupdate.query()
    #st.experimental_rerun()

def uploadDUE_scale_JSON(sparqlupdate,host,dic , uuid_DeterminationOfScaleOfFeature, name, rprovName):
    time = getTimestamp()
    with st.spinner("Uploading..."):
        for key, value in dic.items():
            uuid_ScaleOfFeature = uuid.uuid4()
            query = (f"""PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                        PREFIx rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    SELECT ?subject WHERE {{?subject rdf:type rprov:Feature. ?subject rdfs:label '{key}'}}""")
            results_update = get_connection_fuseki(host, query)

            result_2 = pd.json_normalize(results_update["results"]["bindings"])


            query = (f"""INSERT DATA {{<urn:uuid:{uuid_ScaleOfFeature}> rdf:type rprov:ScaleOfFeature, owl:NamedIndividual;
                          rprov:{rprovName} rprov:{value["levelOfScale"]};
                          rdfs:label "{rprovName} {key}"@en;
                          rprov:toFeature <{result_2["subject.value"][0]}>;
                          rprov:wasGeneratedByDUA  <urn:uuid:{uuid_DeterminationOfScaleOfFeature}>;
                          prov:generatedAtTime '{time}'^^xsd:dateTime.
                        }}""")
            sparqlupdate.setQuery(prefix+query)
            sparqlupdate.setMethod(POST)
            sparqlupdate.query()



            determinationNameUUID = 'DeterminationOfUniqueValuesOfFeature_'
            determinationName = 'DeterminationOfUniqueValuesOfFeature'
            label = 'detUniqueValuesOfFeature@en'
            dicName = 'unique_values_of_features_dic'
            name = 'UniqueValuesOfFeature'
            rprovName = 'uniqueValues'
            try:
                ending_time = getTimestamp()
                uuid_determinationUniqueValues = determinationActivity(sparqlupdate,determinationName, label, time, time)

                uuid_UniqueValues_entity = uuid.uuid4()
                uuid_UniqueValues_seq = uuid.uuid4()

                query = (f"""INSERT DATA {{<urn:uuid:{uuid_UniqueValues_entity}> rdf:type rprov:UniqueValuesOfFeature, owl:NamedIndividual;
                                              rprov:uniqueValues <urn:uuid:{uuid_UniqueValues_seq}>;
                                              rdfs:label "uniqueValues {key}";
                                              rprov:toFeature <{result_2["subject.value"][0]}>;
                                              rprov:wasGeneratedByDUA  <urn:uuid:{uuid_determinationUniqueValues}>;
                                              prov:generatedAtTime '{ending_time}'^^xsd:dateTime;
                                            }}""")
                sparqlupdate.setQuery(prefix + query)
                sparqlupdate.setMethod(POST)
                sparqlupdate.query()

                if dic[key]["levelOfScale"] == "Nominal":
                    i = 0
                    for values in dic[key]["uniqueValues"]:

                        query = (f"""INSERT DATA {{<urn:uuid:{uuid_UniqueValues_seq}> rdf:type rdf:Bag, owl:NamedIndividual;
                                                          rdf:_{i}  '{values}';}}""")
                        sparqlupdate.setQuery(prefix + query)
                        sparqlupdate.setMethod(POST)
                        sparqlupdate.query()
                        i = i + 1
                else:
                    i = 0
                    for values in dic[key]["uniqueValues"]:

                        query = (f"""INSERT DATA {{<urn:uuid:{uuid_UniqueValues_seq}> rdf:type rdf:Seq, owl:NamedIndividual;
                                                          rdf:_{i}  '{values}';}}""")
                        sparqlupdate.setQuery(prefix + query)
                        sparqlupdate.setMethod(POST)
                        sparqlupdate.query()
                        i = i + 1
            except Exception as e:
                st.error(e)






def uploadDUE(sparqlupdate,host,dic , uuid_DeterminationOfScaleOfFeature, name, rprovName):
    time = getTimestamp()
    with st.spinner("Uploading..."):
        for key, value in dic.items():
            uuid_ScaleOfFeature = uuid.uuid4()
            query = (f"""PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                        PREFIx rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    SELECT ?subject WHERE {{?subject rdf:type rprov:Feature. ?subject rdfs:label '{key}'}}""")
            results_update = get_connection_fuseki(host, query)

            result_2 = pd.json_normalize(results_update["results"]["bindings"])

            query = (f"""INSERT DATA {{<urn:uuid:{uuid_ScaleOfFeature}> rdf:type rprov:{name}, owl:NamedIndividual;
                          rprov:{rprovName} '{value}';
                          rdfs:label "{rprovName} {key}"@en;
                          rprov:toFeature <{result_2["subject.value"][0]}>;
                          rprov:wasGeneratedByDUA  <urn:uuid:{uuid_DeterminationOfScaleOfFeature}>;
                          prov:generatedAtTime '{time}'^^xsd:dateTime.
                        }}""")
            sparqlupdate.setQuery(prefix+query)
            sparqlupdate.setMethod(POST)
            sparqlupdate.query()
    st.experimental_rerun()

def uploadMissingValues(sparqlupdate,host,dic , uuid_DeterminationOfScaleOfFeature, name):
    time = getTimestamp()
    with st.spinner("Uploading..."):
        for key, value in dic.items():
            uuid_ScaleOfFeature = uuid.uuid4()
            query = (f"""PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                        PREFIx rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    SELECT ?subject WHERE {{?subject rdf:type rprov:Feature. ?subject rdfs:label '{key}'}}""")
            results_update = get_connection_fuseki(host, query)

            result_2 = pd.json_normalize(results_update["results"]["bindings"])

            query = (f"""INSERT DATA {{<urn:uuid:{uuid_ScaleOfFeature}> rdf:type rprov:{name}, owl:NamedIndividual;
                          rdfs:label "missing values {key}"@en;
                          rdfs:comment "{value}";
                          rprov:toFeature <{result_2["subject.value"][0]}>;
                          rprov:wasGeneratedByDPA  <urn:uuid:{uuid_DeterminationOfScaleOfFeature}>;
                          prov:generatedAtTime '{time}'^^xsd:dateTime;
                        }}""")
            sparqlupdate.setQuery(prefix+query)
            sparqlupdate.setMethod(POST)
            sparqlupdate.query()




def deleteWasGeneratedByDPA(sparqlupdate,df):  # panda df
    time = getTimestamp()
    query = (f"""
            INSERT {{?DPA prov:invalidatedAtTime '{time}'^^xsd:dateTime;}}
            WHERE  {{?DPA rprov:wasGeneratedByDPA <{df["DPA.value"][0]}>}}""")


    sparqlupdate.setQuery(prefix+query)
    sparqlupdate.setMethod(POST)
    sparqlupdate.query()

def deleteWasGeneratedByDUA(sparqlupdate,df):
    time = getTimestamp()
    query = (f"""    
            INSERT {{?DUE prov:invalidatedAtTime '{time}'^^xsd:dateTime;}}
            WHERE {{?DUE rprov:wasGeneratedByDUA <{df["DUA.value"][0]}>}}""")



    sparqlupdate.setQuery(prefix+query)
    sparqlupdate.setMethod(POST)
    sparqlupdate.query()


def upload_features(sparqlupdate, uuid_Feature, features, uuid_determinationFeature):
    query = (f"""INSERT DATA {{<urn:uuid:{uuid_Feature}> rdf:type rprov:Feature, owl:NamedIndividual;
                                        rdfs:label '{features}';
                                        rprov:wasGeneratedByDUA <urn:uuid:{uuid_determinationFeature}>;
                                        }}""")

    sparqlupdate.setQuery(prefix + query)
    sparqlupdate.setMethod(POST)
    sparqlupdate.query()
    return True

def get_feature_names(host):
    query = (f"""
    SELECT ?featureID ?featureName WHERE {{
      ?featureID rdf:type rprov:Feature .
      ?featureID rdfs:label ?featureName.
    }}
    """)
    try:
        result_feature_names = get_connection_fuseki(host, (prefix + query))
        result_feature_names = pd.json_normalize(result_feature_names["results"]["bindings"])
        return result_feature_names
    except:
        return st.warning("Please select dataset")


# Unique Values

def uploadUniqueValues(sparqlupdate,host,dic, level_measurement, uuid_DeterminationUniqueValues, name, rprovName):
    time = getTimestamp()
    with st.spinner("Uploading unique values..."):
        for key, value in dic.items():
            uuid_UniqueValues_entity = uuid.uuid4()
            uuid_UniqueValues_seq = uuid.uuid4()

            query = (f"""PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                        PREFIx rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    SELECT ?subject WHERE {{?subject rdf:type rprov:Feature. ?subject rdfs:label '{key}'}}""")
            results_update = get_connection_fuseki(host, query)

            result_2 = pd.json_normalize(results_update["results"]["bindings"])

            query = (f"""INSERT DATA {{<urn:uuid:{uuid_UniqueValues_entity}> rdf:type rprov:{name}, owl:NamedIndividual;
                              rprov:{rprovName} <urn:uuid:{uuid_UniqueValues_seq}>;
                              rdfs:label "{rprovName} {key}";
                              rprov:toFeature <{result_2["subject.value"][0]}>;
                              rprov:wasGeneratedByDUA  <urn:uuid:{uuid_DeterminationUniqueValues}>;
                              prov:generatedAtTime '{time}'^^xsd:dateTime;
                            }}""")
            sparqlupdate.setQuery(prefix+query)
            sparqlupdate.setMethod(POST)
            sparqlupdate.query()

            if level_measurement[key] == "Nominal":
                i = 0
                for values in value:
                    query = (f"""INSERT DATA {{<urn:uuid:{uuid_UniqueValues_seq}> rdf:type rdf:Bag, owl:NamedIndividual;
                                          rdf:_{i}  '{values}';}}""")
                    sparqlupdate.setQuery(prefix + query)
                    sparqlupdate.setMethod(POST)
                    sparqlupdate.query()
                    i = i + 1
            else:
                i = 0
                for values in value:
                    query = (f"""INSERT DATA {{<urn:uuid:{uuid_UniqueValues_seq}> rdf:type rdf:Seq, owl:NamedIndividual;
                                          rdf:_{i}  '{values}';}}""")
                    sparqlupdate.setQuery(prefix + query)
                    sparqlupdate.setMethod(POST)
                    sparqlupdate.query()
                    i = i + 1
    st.success("Upload successful")
#
# def getUniqueValues(host):
#     dictionary_uniqueValues = dict()
#     query = (f"""    SELECT ?featureID ?featureName ?DataUnderstandingEntityID (GROUP_CONCAT(?uniqueValues; SEPARATOR=", ") AS ?uniqueValuesList) ?DUA {{
#     ?featureID rdf:type rprov:Feature .
#     ?featureID rdfs:label ?featureName.
#     ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
#     ?DataUnderstandingEntityID rprov:uniqueValues ?uniqueValues.
# 	?DataUnderstandingEntityID rprov:toFeature ?featureID.
#     ?DataUnderstandingEntityID rprov:wasGeneratedByDUA ?DUA.
#     ?DataUnderstandingEntityID rprov:isValid true.}}
#     GROUP BY ?featureID ?featureName ?DataUnderstandingEntityID ?DUA
#     """)
#
#     results_feature_uniqueValues = get_connection_fuseki(host, (prefix+query))
#     results_feature_uniqueValues = pd.json_normalize(results_feature_uniqueValues["results"]["bindings"])
#     uniqueValuesList = (results_feature_uniqueValues["uniqueValuesList.value"].tolist())
#
#
#     for _index, row in results_feature_uniqueValues.iterrows():
#
#         dictionary_uniqueValues[row["featureName.value"]] = uniqueValuesList[_index]#row["uniqueValuesList.value"]
#
#     if not dictionary_uniqueValues:
#         raise ValueError("No unique values found")
#     return dictionary_uniqueValues, results_feature_uniqueValues

def getUniqueValuesSeq(host):
    dictionary_uniqueValues = dict()
    query = (f"""    SELECT ?label ?containerMembershipProperty ?item WHERE {{
    ?sub rprov:uniqueValues ?container.
    ?container ?containerMembershipProperty ?item.
    ?sub rprov:toFeature ?feature.
    ?feature rdfs:label ?label.
    FILTER(?containerMembershipProperty!= rdf:type)
  }}
    """)


    results_feature_uniqueValues = get_connection_fuseki(host, (prefix+query))
    results_feature_uniqueValues = pd.json_normalize(results_feature_uniqueValues["results"]["bindings"])
    results_feature_uniqueValues= results_feature_uniqueValues.groupby("label.value")["item.value"].apply(list)

    for _index, row in results_feature_uniqueValues.items():
        dictionary_uniqueValues[_index] = row

    return dictionary_uniqueValues


# Approach
def getApproach(host):
    query = (f"""SELECT ?rprov ?DataUnderstandingEntityID ?BUA WHERE{{
                            ?DataUnderstandingEntityID rdf:type ?rprov.
                            ?DataUnderstandingEntityID rprov:wasGeneratedByBUA ?BUA.

                            FILTER(?rprov!=owl:NamedIndividual).
                            FILTER(?rprov!=owl:Class).
                           FILTER NOT EXISTS{{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}}
                        }}""")
    results_approach = get_connection_fuseki(host, (prefix + query))
    results_approach = pd.json_normalize(results_approach["results"]["bindings"])

    return results_approach["DataUnderstandingEntityID.value"][0]


def uploadApproach(sparqlupdate, uuid_activity, uuid_entity):
    time = getTimestamp()
    query = (f"""
                          INSERT DATA {{<urn:uuid:{uuid_activity}> rdf:type rprov:ChoiceOfAssessmentApproach, owl:NamedIndividual;
                          rdfs:label "choiceOfAssessment"@en;
                          prov:endedAtTime '{time}'^^xsd:dateTime.}}""")

    sparqlupdate.setQuery(prefix + query)
    sparqlupdate.setMethod(POST)
    sparqlupdate.query()

    query = (f"""PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                          PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                          PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                          PREFIX prov:  <http://www.w3.org/ns/prov#>
                          PREFIX owl: <http://www.w3.org/2002/07/owl#>
                          PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                          PREFIX instance:<http://www.semanticweb.org/dke/ontologies#> 
                          INSERT DATA {{<urn:uuid:{uuid_entity}> rdf:type rprov:PerturbationApproach, owl:NamedIndividual;
                          rprov:wasGeneratedByBUA <urn:uuid:{uuid_activity}>;
                          prov:generatedAtTime '{time}'^^xsd:dateTime.}}""")
    #rprov:isValid true;
    sparqlupdate.setQuery(prefix + query)
    sparqlupdate.setMethod(POST)
    sparqlupdate.query()



# Scale
def getFeatureScale(host):
    """
    :rtype: object
    """
    dictionary_scales = dict()
    query = (f"""
    SELECT ?featureID ?featureName ?DataUnderstandingEntityID ?scale ?DUA {{
    ?featureID rdf:type rprov:Feature .
    ?featureID rdfs:label ?featureName.
    ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
    ?DataUnderstandingEntityID rprov:scale ?scale.
	?DataUnderstandingEntityID rprov:toFeature ?featureID.
  	?DataUnderstandingEntityID rprov:wasGeneratedByDUA ?DUA.
   FILTER NOT EXISTS{{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}}

    }}""")
    results_feature_scale = get_connection_fuseki(host, (prefix + query))

    results_feature_scale = pd.json_normalize(results_feature_scale["results"]["bindings"])

    for _index, row in results_feature_scale.iterrows():
        result_scale = row["scale.value"].partition("#")[2]
        dictionary_scales[row["featureName.value"]] = result_scale

    return dictionary_scales, results_feature_scale

# Volatility
def getFeatureVolatility(host):
    dictionary_volatility = dict()
    query = (f"""
    SELECT ?featureID ?featureName ?DataUnderstandingEntityID ?volatility ?DUA WHERE{{
    ?featureID rdf:type rprov:Feature .
    ?featureID rdfs:label ?featureName.
    ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
    ?DataUnderstandingEntityID rprov:volatilityLevel ?volatility.
	?DataUnderstandingEntityID rprov:toFeature ?featureID.
    ?DataUnderstandingEntityID rprov:wasGeneratedByDUA ?DUA.
    
    FILTER NOT EXISTS{{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}}
  	
    }}""")
    results_feature_volatility = get_connection_fuseki(host, (prefix+query))
    results_feature_volatility = pd.json_normalize(results_feature_volatility["results"]["bindings"])

    for _index, row in results_feature_volatility.iterrows():
        dictionary_volatility[row["featureName.value"]] = row["volatility.value"]

    if dictionary_volatility == {}:
        return Exception
    else:
        return dictionary_volatility, results_feature_volatility

def getFeatureVolatilityDeployment(volatility,feature,host):
    query = (f"""
    SELECT ?volatilityEntity ?feature ?label ?volatilityLevel WHERE {{
    <{volatility}> rprov:modelingEntityWasDerivedFrom ?volatilityEntity.
    ?volatilityEntity rdf:type rprov:VolatilityOfFeature.
        ?volatilityEntity rprov:volatilityLevel ?volatilityLevel.
    ?volatilityEntity rprov:toFeature <{feature}>.
    ?volatilityEntity rprov:toFeature ?feature.
    ?feature rdfs:label ?label.
}}
    """)

    try:
        results_feature_volatility = get_connection_fuseki(host, (prefix+query))

        results_feature_volatility = pd.json_normalize(results_feature_volatility["results"]["bindings"])

        return results_feature_volatility
    except Exception as e:
        st.write(e)
        return


# Sensor
def getSensorPrecision(host):
    dictionary_SensorPrecision = dict()
    query = (f"""
    SELECT ?featureID ?featureName ?DataUnderstandingEntityID ?SensorPrecisionLevel ?DUA {{
    ?featureID rdf:type rprov:Feature .
    ?featureID rdfs:label ?featureName.
    ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
    ?DataUnderstandingEntityID rprov:SensorPrecisionLevel ?SensorPrecisionLevel.
	?DataUnderstandingEntityID rprov:toFeature ?featureID.
  	?DataUnderstandingEntityID rprov:wasGeneratedByDUA ?DUA.
    FILTER NOT EXISTS{{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}}
    }}""")
    results_feature_sensor = get_connection_fuseki(host, (prefix+query))
    results_feature_sensor = pd.json_normalize(results_feature_sensor["results"]["bindings"])



    for _index, row in results_feature_sensor.iterrows():
        dictionary_SensorPrecision[row["featureName.value"]] = float(row["SensorPrecisionLevel.value"])

    results_feature_sensor = results_feature_sensor[["featureID.value", "featureName.value", "DataUnderstandingEntityID.value", "SensorPrecisionLevel.value", "DUA.value"]]



    return dictionary_SensorPrecision, results_feature_sensor



# Missing Values
def getMissingValues(host):
    dictionary_MissingValues = dict()
    query = (f"""
    SELECT ?featureID ?featureName ?DataPreparationEntityID ?MissingValues ?DPA {{
    ?featureID rdf:type rprov:Feature .
    ?featureID rdfs:label ?featureName.
    ?DataPreparationEntityID rdf:type owl:NamedIndividual.
    ?DataPreparationEntityID rdfs:comment ?MissingValues.
	?DataPreparationEntityID rprov:toFeature ?featureID.
  	?DataPreparationEntityID rprov:wasGeneratedByDPA ?DPA.
    FILTER NOT EXISTS{{?DataPreparationEntityID prov:invalidatedAtTime ?time}}
    }}""")
    results_feature_MissingValues = get_connection_fuseki(host, (prefix+query))
    results_feature_MissingValues = pd.json_normalize(results_feature_MissingValues["results"]["bindings"])

    for _index, row in results_feature_MissingValues.iterrows():
        dictionary_MissingValues[row["featureName.value"]] = row["MissingValues.value"]

    return dictionary_MissingValues, results_feature_MissingValues

def getMissingValuesDeployment(missingValue,feature,host):
    query = (f"""
    SELECT ?missingValueEntity ?feature ?label ?MissingValues WHERE {{
    <{missingValue}> rprov:modelingEntityWasDerivedFrom ?missingValueEntity.
    ?missingValueEntity rdf:type rprov:HandlingOfMissingValues.
    ?missingValueEntity rdfs:comment ?MissingValues.
    ?missingValueEntity rprov:toFeature <{feature}>.
    ?missingValueEntity rprov:toFeature ?feature.
    ?feature rdfs:label ?label.
}}
    """)

    try:
        results_feature_volatility = get_connection_fuseki(host, (prefix+query))

        results_feature_volatility = pd.json_normalize(results_feature_volatility["results"]["bindings"])

        return results_feature_volatility
    except Exception as e:
        st.write(e)
        return







# Binning
def uploadBinValues(sparqlupdate,host,dic, uuid_Determination, rprovName):
    time = getTimestamp()
    with st.spinner("Uploading bin values..."):
        for key, value in dic.items():
            uuid_BinEntity = uuid.uuid4()
            uuid_SeqBinEntityValues = uuid.uuid4()

            query = (f"""PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                        PREFIx rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    SELECT ?subject WHERE {{?subject rdf:type rprov:Feature. ?subject rdfs:label '{key}'}}""")
            results_update = get_connection_fuseki(host, query)

            result_2 = pd.json_normalize(results_update["results"]["bindings"])

            #sparqlupdate = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")

            query = (f"""INSERT DATA {{<urn:uuid:{uuid_BinEntity}> rdf:type rprov:{rprovName}, owl:NamedIndividual;
                              rprov:{rprovName} <urn:uuid:{uuid_SeqBinEntityValues}>;
                              rdfs:label "{rprovName} {key}";
                              rprov:toFeature <{result_2["subject.value"][0]}>;
                              rprov:wasGeneratedByDPA  <urn:uuid:{uuid_Determination}>;
                              prov:generatedAtTime '{time}'^^xsd:dateTime.
                            }}""")
            sparqlupdate.setQuery(prefix+query)
            sparqlupdate.setMethod(POST)
            sparqlupdate.query()


            i = 0
            for values in value:
                query = (f"""INSERT DATA {{<urn:uuid:{uuid_SeqBinEntityValues}> rdf:type rdf:Seq, owl:NamedIndividual;
                                      rdf:_{i}  '{values}';}}""")
                sparqlupdate.setQuery(prefix + query)
                sparqlupdate.setMethod(POST)
                sparqlupdate.query()
                i = i + 1
    st.success("Upload successful")

def getBinValuesSeq(host):
    dictionary_BinValues = dict()
    query = (f"""      SELECT ?DPA ?DPE ?feature ?label ?containerMembershipProperty ?item WHERE {{
    ?DPE rprov:RangeOfBinnedFeature ?container.
    ?DPE rprov:wasGeneratedByDPA ?DPA.
    ?container ?containerMembershipProperty ?item.
    ?DPE rprov:toFeature ?feature.
    ?feature rdfs:label ?label.
    FILTER(?containerMembershipProperty!= rdf:type).
    FILTER NOT EXISTS{{?DPE prov:invalidatedAtTime ?time}}.
    }}
    """)


    results_feature_BinValues = get_connection_fuseki(host, (prefix+query))
    results_feature_BinValues = pd.json_normalize(results_feature_BinValues["results"]["bindings"])
    results_feature_BinValues_grouped= results_feature_BinValues.groupby(["label.value"])["item.value"].apply(list)

    for _index, row in results_feature_BinValues_grouped.items():
        dictionary_BinValues[_index] = row

    return dictionary_BinValues, results_feature_BinValues



def getBinsDeployment(bin,feature,host):
    query = (f"""
    SELECT ?binEntity ?feature ?label ?MissingValues ?seq ?item WHERE {{
    <{bin}> rprov:modelingEntityWasDerivedFrom ?binEntity.
    ?binEntity rdf:type rprov:RangeOfBinnedFeature.
    ?binEntity rprov:RangeOfBinnedFeature ?seq.
    ?seq a rdf:Seq .
    ?seq ?containerMembershipProperty ?item.
    ?binEntity rprov:toFeature <{feature}>.
    ?binEntity rprov:toFeature ?feature.
    ?feature rdfs:label ?label.
    FILTER(?containerMembershipProperty!= rdf:type)
}}
    """)

    try:
        results_feature_volatility = get_connection_fuseki(host, (prefix+query))

        results_feature_volatility = pd.json_normalize(results_feature_volatility["results"]["bindings"])

        return results_feature_volatility
    except Exception as e:
        st.write(e)
        return


def uploadPerturbationAssessment(host_upload,uuid_PerturbationAssessment, label,
                                 uuid_DefinitionOfPerturbationOption,perturbationOptions_settings,assessmentPerturbationOptions, pertMode, pertModeValues):
    time = getTimestamp()
    for key in perturbationOptions_settings.keys():
        for perturbationOption in assessmentPerturbationOptions[key][
            "PerturbationOptionID"]:

            if pertMode =="Prioritized":
                query = (f"""INSERT DATA {{<urn:uuid:{uuid_PerturbationAssessment}> rdf:type rprov:PerturbationAssessment, owl:NamedIndividual;
                            rdfs:label "{label}"@en ;
                            rprov:deploymentEntityWasDerivedFrom <{perturbationOption}>;
                            rprov:perturbedTestCase "Saved as csv with name: {label}_{uuid_PerturbationAssessment}";
                            rprov:wasGeneratedByDA  <urn:uuid:{uuid_DefinitionOfPerturbationOption}>;
                            rprov:pertModeValue "{pertMode}: {pertModeValues}";
                            prov:generatedAtTime '{time}'^^xsd:dateTime.
                                        }}""")
            else:
                query = (f"""INSERT DATA {{<urn:uuid:{uuid_PerturbationAssessment}> rdf:type rprov:PerturbationAssessment, owl:NamedIndividual;
                            rdfs:label "{label}"@en ;
                            rprov:deploymentEntityWasDerivedFrom <{perturbationOption}>;
                            rprov:perturbedTestCase "Saved as csv with name: {label}_{uuid_PerturbationAssessment}";
                            rprov:wasGeneratedByDA  <urn:uuid:{uuid_DefinitionOfPerturbationOption}>;
                            rprov:pertModeValue "{pertMode}";
                            prov:generatedAtTime '{time}'^^xsd:dateTime.
                                        }}""")
            host_upload.setQuery(prefix + query)
            host_upload.setMethod(POST)
            host_upload.query()


#
def uploadClassificationCase(host_upload,uuid_ClassificationCase, label, uuid_PerturbationAssessment,
                             rows):
    time = getTimestamp()
    query = (f"""INSERT DATA {{<urn:uuid:{uuid_ClassificationCase}> rdf:type rprov:ClassificationCase, owl:NamedIndividual;
                                    rdfs:label "{label}"@en ;
                                    rprov:values "{rows}"@en;
                                    rprov:wasAssignedToDeploymentEntity <urn:uuid:{uuid_PerturbationAssessment}>;
                                    prov:endedAtTime '{time}'^^xsd:dateTime.
                                                }}""")

    host_upload.setQuery(prefix + query)
    host_upload.setMethod(POST)
    host_upload.query()




def uploadDataRestrictionSeq(sparqlupdate,host,dic , uuid_DeterminationOfScaleOfFeature, name, rprovName):
    time = getTimestamp()
    for key, value in dic.items():
        uuid_DataRestrictionEntity = uuid.uuid4()
        uuid_DataRestrictionSeq = uuid.uuid4()

        query = (f"""PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                    PREFIx rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT ?subject WHERE {{?subject rdf:type rprov:Feature. ?subject rdfs:label '{key}'}}""")
        results_update = get_connection_fuseki(host, query)

        result_2 = pd.json_normalize(results_update["results"]["bindings"])

        query = (f"""INSERT DATA {{<urn:uuid:{uuid_DataRestrictionEntity}> rdf:type rprov:{name}, owl:NamedIndividual;
                          rprov:{rprovName} <urn:uuid:{uuid_DataRestrictionSeq}>;
                          rdfs:label "{rprovName} {key}";
                          rprov:toFeature <{result_2["subject.value"][0]}>;
                          rprov:wasGeneratedByDUA  <urn:uuid:{uuid_DeterminationOfScaleOfFeature}>;
                          prov:generatedAtTime '{time}'^^xsd:dateTime;
                        }}""")
        try:
            sparqlupdate.setQuery(prefix+query)
            sparqlupdate.setMethod(POST)
            sparqlupdate.query()
        except Exception as e:
            st.error(e)
        i = 0
        for values in value:
            query = (f"""INSERT DATA {{<urn:uuid:{uuid_DataRestrictionSeq}> rdf:type rdf:Seq, owl:NamedIndividual;
                                  rdf:_{i}  '{values}';}}""")
            sparqlupdate.setQuery(prefix + query)
            sparqlupdate.setMethod(POST)
            sparqlupdate.query()
            i = i + 1

def uploadDR(host_upload, host):
    determinationNameUUID = 'DeterminationOfDataRestriction'
    determinationName = 'DeterminationOfDataRestriction'
    label = "detDataRestriction"
    name = 'DataRestriction'
    rprovName = 'restriction'
    ending_time = getTimestamp()
    uuid_determinationDataRestriction = determinationActivity(host_upload, determinationName, label,
                                                              ending_time)
    uploadDataRestrictionSeq(host_upload, host, st.session_state['data_restrictions_dict'],
                             uuid_determinationDataRestriction, name,
                             rprovName)


def getDataRestrictionSeq(data_restriction,host):
    dictionary_DataRestriction = dict()
    query = (f"""    SELECT ?DUA ?label ?containerMembershipProperty ?item WHERE {{
    ?DUA rprov:restriction ?container.
    ?DUA rprov:wasGeneratedByDUA <{data_restriction}>.
    ?container a rdf:Seq .
    ?container ?containerMembershipProperty ?item.
    ?DUA rprov:toFeature ?feature.
    ?feature rdfs:label ?label.
    FILTER(?containerMembershipProperty!= rdf:type).
    FILTER NOT EXISTS{{?container prov:invalidatedAtTime ?time}}
    }}
    """)

    results_feature_DataRestriction = get_connection_fuseki(host, (prefix+query))
    results_feature_DataRestriction = pd.json_normalize(results_feature_DataRestriction["results"]["bindings"])
    results_feature_DataRestriction_grouped= results_feature_DataRestriction.groupby("label.value")["item.value"].apply(list)

    for _index, row in results_feature_DataRestriction_grouped.items():
        dictionary_DataRestriction[_index] = row

    return dictionary_DataRestriction


def getDataRestrictionSeqDeployment(data_restriction,feature,host):
    dictionary_DataRestriction = dict()
    query = (f"""

    SELECT ?dataRestrictionEntity ?feature ?label ?seq ?item WHERE {{
    <{data_restriction}> rprov:modelingEntityWasDerivedFrom ?dataRestrictionEntity.
    ?dataRestrictionEntity rdf:type rprov:DataRestriction.
    ?dataRestrictionEntity rprov:restriction ?seq.
    ?seq a rdf:Seq .
    ?seq ?containerMembershipProperty ?item.
    ?dataRestrictionEntity rprov:toFeature <{feature}>.
    ?dataRestrictionEntity rprov:toFeature ?feature.
    ?feature rdfs:label ?label.
    FILTER(?containerMembershipProperty!= rdf:type)}}
    """)


    try:
        results_feature_DataRestriction = get_connection_fuseki(host, (prefix+query))

        results_feature_DataRestriction = pd.json_normalize(results_feature_DataRestriction["results"]["bindings"])

        results_feature_DataRestriction= results_feature_DataRestriction.groupby("label.value")["item.value"].apply(list)

        for _index, row in results_feature_DataRestriction.items():
            dictionary_DataRestriction[_index] = row

        return dictionary_DataRestriction
    except:
        return



def getAttributes(host):

    if not any(key.startswith('level_of_measurement_') for key in st.session_state):
        st.session_state["dataframe_feature_names"] = get_feature_names(host)
    if st.session_state["dataframe_feature_names"].empty:
        st.warning("No features defined. If this is the first time a new dataset is uploaded please define features, a scale for each feature and upload the unique values.")

    try:
        st.session_state["level_of_measurement_dic"], st.session_state["DF_feature_scale_name"] = getFeatureScale(host)
        if st.session_state["level_of_measurement_dic"] == {}:
            st.warning(
                "No feature scales determined. If this is the first time a new dataset is uploaded please define scale for each feature and upload the unique values.")
        else:
            for key, value in st.session_state["level_of_measurement_dic"].items():
                st.session_state[f'level_of_measurement_{key}'] = value
    except Exception as e:
        pass
        # st.session_state["DF_feature_scale_name"] = pd.DataFrame()
        # st.session_state["level_of_measurement_dic"] = dict()

    try:
        st.session_state["unique_values_dict"] = getUniqueValuesSeq(host)
    except Exception as e:
        st.warning("No Unique Values in database. If this is the first time a new dataset is uploaded please upload the unique values.")
        st.session_state["unique_values_dict"] = {}

    try:
        st.session_state["volatility_of_features_dic"], st.session_state[
            "DF_feature_volatility_name"] = getFeatureVolatility(host)
    except Exception as e:
        st.warning("No volatility level determined")
        st.session_state["volatility_of_features_dic"] = dict()


    try:
        st.session_state["loaded_feature_sensor_precision_dict"], st.session_state[
            "DF_feature_sensor_precision"] = getSensorPrecision(host)
    except Exception as e:
        st.warning("No sensor precision determined")
        st.session_state["loaded_feature_sensor_precision_dict"] = dict()
        st.session_state["DF_feature_sensor_precision"] = pd.DataFrame()


    try:
        st.session_state["loaded_missingValues_of_features_dic"], st.session_state[
        "DF_feature_missing_values_dic"] = getMissingValues(host)
        if st.session_state["loaded_missingValues_of_features_dic"] == {}:
            st.warning("No missing values determined")
    except:
        pass

    try:
        st.session_state["loaded_bin_dict"], st.session_state["DF_bin_dict"] = getBinValuesSeq(host)
    except Exception as e:
        st.warning("No bins determined")
        st.session_state["loaded_bin_dict"] = dict()


def getAttributesDeployment(host):

    if not any(key.startswith('level_of_measurement_') for key in st.session_state):
        st.session_state["dataframe_feature_names"] = get_feature_names(host)
    if st.session_state["dataframe_feature_names"].empty:
        st.warning("No features defined. If this is the first time a new dataset is uploaded please define features, a scale for each feature and upload the unique values.")

    try:
        st.session_state["level_of_measurement_dic"], st.session_state["DF_feature_scale_name"] = getFeatureScale(host)
        if st.session_state["level_of_measurement_dic"] == {}:
            st.warning(
                "No feature scales determined. If this is the first time a new dataset is uploaded please define scale for each feature and upload the unique values.")
        else:
            for key, value in st.session_state["level_of_measurement_dic"].items():
                st.session_state[f'level_of_measurement_{key}'] = value
    except Exception as e:
        pass


    try:
        st.session_state["unique_values_dict"] = getUniqueValuesSeq(host)
    except Exception as e:
        st.warning("No Unique Values in database. If this is the first time a new dataset is uploaded please upload the unique values.")
        st.session_state["unique_values_dict"] = {}

    try:
        st.session_state["volatility_of_features_dic"], st.session_state[
            "DF_feature_volatility_name"] = getFeatureVolatility(host)
    except Exception as e:
        st.session_state["volatility_of_features_dic"] = dict()


    try:
        st.session_state["loaded_feature_sensor_precision_dict"], st.session_state[
            "DF_feature_sensor_precision"] = getSensorPrecision(host)
    except Exception as e:
        st.session_state["loaded_feature_sensor_precision_dict"] = dict()
        st.session_state["DF_feature_sensor_precision"] = pd.DataFrame()

    try:
        st.session_state["loaded_missingValues_of_features_dic"], st.session_state[
        "DF_feature_missing_values_dic"] = getMissingValues(host)
    except:
        pass

    try:
        st.session_state["loaded_bin_dict"], st.session_state["DF_bin_dict"] = getBinValuesSeq(host)
    except Exception as e:
        st.session_state["loaded_bin_dict"] = dict()

def getAttributesDataUnderstanding(host):

    if not any(key.startswith('level_of_measurement_') for key in st.session_state):
        st.session_state["dataframe_feature_names"] = get_feature_names(host)
    if st.session_state["dataframe_feature_names"].empty:
        st.warning("No features defined. If this is the first time a new dataset is uploaded please define features, a scale for each feature and upload the unique values.")

    try:
        st.session_state["level_of_measurement_dic"], st.session_state["DF_feature_scale_name"] = getFeatureScale(host)
        if st.session_state["level_of_measurement_dic"] == {}:
            st.warning(
                "No feature scales determined. If this is the first time a new dataset is uploaded please define scale for each feature and upload the unique values.")
        else:
            for key, value in st.session_state["level_of_measurement_dic"].items():
                st.session_state[f'level_of_measurement_{key}'] = value
    except Exception as e:
        pass


    try:
        st.session_state["unique_values_dict"] = getUniqueValuesSeq(host)
    except Exception as e:
        st.warning("No Unique Values in database. If this is the first time a new dataset is uploaded please upload the unique values.")
        st.session_state["unique_values_dict"] = {}

    try:
        st.session_state["volatility_of_features_dic"], st.session_state[
            "DF_feature_volatility_name"] = getFeatureVolatility(host)
    except Exception as e:
        st.warning("No volatility level determined")
        st.session_state["volatility_of_features_dic"] = dict()


    try:
        st.session_state["loaded_feature_sensor_precision_dict"], st.session_state[
            "DF_feature_sensor_precision"] = getSensorPrecision(host)
    except Exception as e:
        st.warning("No sensor precision determined")
        st.session_state["loaded_feature_sensor_precision_dict"] = dict()
        st.session_state["DF_feature_sensor_precision"] = pd.DataFrame()




def getAttributesDataPreparation(host):

    if not any(key.startswith('level_of_measurement_') for key in st.session_state):
        st.session_state["dataframe_feature_names"] = get_feature_names(host)
    if st.session_state["dataframe_feature_names"].empty:
        st.warning("No features defined. If this is the first time a new dataset is uploaded please define features, a scale for each feature and upload the unique values.")

    try:
        st.session_state["level_of_measurement_dic"], st.session_state["DF_feature_scale_name"] = getFeatureScale(host)
        if st.session_state["level_of_measurement_dic"] == {}:
            st.warning(
                "No feature scales determined. If this is the first time a new dataset is uploaded please define scale for each feature and upload the unique values.")
        else:
            for key, value in st.session_state["level_of_measurement_dic"].items():
                st.session_state[f'level_of_measurement_{key}'] = value

    except Exception as e:
        pass

    try:
        st.session_state["unique_values_dict"] = getUniqueValuesSeq(host)
    except Exception as e:
        st.warning("No Unique Values in database. If this is the first time a new dataset is uploaded please upload the unique values.")
        st.session_state["unique_values_dict"] = {}

    try:
        st.session_state["loaded_missingValues_of_features_dic"], st.session_state[
        "DF_feature_missing_values_dic"] = getMissingValues(host)
        if st.session_state["loaded_missingValues_of_features_dic"] == {}:
            st.warning("No missing values determined")
    except:
        pass

    try:
        st.session_state["loaded_bin_dict"], st.session_state["DF_bin_dict"] = getBinValuesSeq(host)
    except Exception as e:
        st.warning("No bins determined")
        st.session_state["loaded_bin_dict"] = dict()
