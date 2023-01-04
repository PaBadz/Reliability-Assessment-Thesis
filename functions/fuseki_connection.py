from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET
import streamlit as st
import uuid
import pandas as pd
from datetime import datetime


# sparqlupdate = SPARQLWrapper(f"http://localhost:3030/a/update")
host = "http://localhost:3030/$/datasets"
#sparqlupdate = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")



prefix = """PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
            PREFIX prov:  <http://www.w3.org/ns/prov#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX instance:<http://www.semanticweb.org/dke/ontologies#>"""


def getTimestamp():
    timestamp = datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
    return timestamp


def get_connection_fuseki(host, query):
    sparql = SPARQLWrapper(host)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setMethod(GET)
    return sparql.query().convert()


def get_connection_fuseki_update(host, query):
    sparql = SPARQLWrapper(host)
    sparql.setQuery(query)
    sparql.setMethod(POST)
    return sparql.query().convert()


def get_feature_names(host):
    query = (f"""
    SELECT ?featureID ?featureName WHERE {{
      ?featureID rdf:type rprov:Feature .
      ?featureID rdfs:label ?featureName.
    }}
    """)

    result_feature_names = get_connection_fuseki(host, (prefix + query))
    result_feature_names = pd.json_normalize(result_feature_names["results"]["bindings"])
    return result_feature_names


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
    }}""")
    results_feature_scale = get_connection_fuseki(host, (prefix + query))

    results_feature_scale = pd.json_normalize(results_feature_scale["results"]["bindings"])
    # results_feature_scale.set_index("featureID.value", inplace=True)
    # feature_names_scale = dataframe_names.merge(results_feature_scale, how='left', left_on="featureID.value",
    #                                             right_index=True)

    for _index, row in results_feature_scale.iterrows():
        dictionary_scales[row["featureName.value"]] = row["scale.value"]

    return dictionary_scales, results_feature_scale


def getFeatureVolatility(host):
    dictionary_volatility = dict()
    query = (f"""
    SELECT ?featureID ?featureName ?DataUnderstandingEntityID ?volatility ?DUA {{
    ?featureID rdf:type rprov:Feature .
    ?featureID rdfs:label ?featureName.
    ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
    ?DataUnderstandingEntityID rprov:volatilityLevel ?volatility.
	?DataUnderstandingEntityID rprov:toFeature ?featureID.
  	?DataUnderstandingEntityID rprov:wasGeneratedByDUA ?DUA.
    }}""")
    results_feature_volatility = get_connection_fuseki(host, (prefix+query))
    results_feature_volatility = pd.json_normalize(results_feature_volatility["results"]["bindings"])

    for _index, row in results_feature_volatility.iterrows():
        dictionary_volatility[row["featureName.value"]] = row["volatility.value"]

    return dictionary_volatility, results_feature_volatility


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
    }}""")
    results_feature_volatility = get_connection_fuseki(host, (prefix+query))
    results_feature_volatility = pd.json_normalize(results_feature_volatility["results"]["bindings"])

    for _index, row in results_feature_volatility.iterrows():
        dictionary_SensorPrecision[row["featureName.value"]] = float(row["SensorPrecisionLevel.value"])

    return dictionary_SensorPrecision, results_feature_volatility


def getUniqueValues(host):
    dictionary_uniqueValues = dict()
    query = (f"""    SELECT ?featureID ?featureName ?DataUnderstandingEntityID (GROUP_CONCAT(?uniqueValues; SEPARATOR=", ") AS ?uniqueValuesList) ?DUA {{
    ?featureID rdf:type rprov:Feature .
    ?featureID rdfs:label ?featureName.
    ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
    ?DataUnderstandingEntityID rprov:uniqueValues ?uniqueValues.
	?DataUnderstandingEntityID rprov:toFeature ?featureID.
    ?DataUnderstandingEntityID rprov:wasGeneratedByDUA ?DUA.}}
    GROUP BY ?featureID ?featureName ?DataUnderstandingEntityID ?DUA
    """)

    results_feature_uniqueValues = get_connection_fuseki(host, (prefix+query))
    results_feature_uniqueValues = pd.json_normalize(results_feature_uniqueValues["results"]["bindings"])
    uniqueValuesList = (results_feature_uniqueValues["uniqueValuesList.value"].tolist())


    for _index, row in results_feature_uniqueValues.iterrows():

        dictionary_uniqueValues[row["featureName.value"]] = uniqueValuesList[_index]#row["uniqueValuesList.value"]

    if not dictionary_uniqueValues:
        raise ValueError("No unique values found")
    return dictionary_uniqueValues, results_feature_uniqueValues

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


def getDataRestrictionSeq(data_restriction,host):
    dictionary_DataRestriction = dict()
    query = (f"""    SELECT ?label ?containerMembershipProperty ?item WHERE {{
    ?sub rdf:DataRestriction ?container.
    ?sub rprov:wasGeneratedByDUA <{data_restriction}>.
    ?container a rdf:Seq .
    ?container ?containerMembershipProperty ?item.
    ?sub rprov:toFeature ?feature.
    ?feature rdfs:label ?label.
    FILTER(?containerMembershipProperty!= rdf:type)}}
    """)


    results_feature_DataRestriction = get_connection_fuseki(host, (prefix+query))
    results_feature_DataRestriction = pd.json_normalize(results_feature_DataRestriction["results"]["bindings"])
    results_feature_DataRestriction= results_feature_DataRestriction.groupby("label.value")["item.value"].apply(list)

    for _index, row in results_feature_DataRestriction.items():
        dictionary_DataRestriction[_index] = row

    return dictionary_DataRestriction




def determinationDUA(sparqlupdate, determinationName, label, starting_time, ending_time):
    uuid_Determination = uuid.uuid4()

    #sparqlupdate = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
    query = (f"""INSERT DATA {{<urn:uuid:{uuid_Determination}> rdf:type rprov:{determinationName}, owl:NamedIndividual;
                rdfs:label '{label}';
                prov:endedAtTime    '{ending_time}'^^xsd:dateTime;;
                prov:startedAtTime  '{starting_time}'^^xsd:dateTime;.}}""")
    sparqlupdate.setQuery(prefix+query)
    sparqlupdate.setMethod(POST)
    sparqlupdate.query()
    return uuid_Determination


def uploadDUE(sparqlupdate,host,dic , uuid_DeterminationOfScaleOfFeature, name, rprovName):
    for key, value in dic.items():
        uuid_ScaleOfFeature = uuid.uuid4()
        query = (f"""PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                    PREFIx rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT ?subject WHERE {{?subject rdf:type rprov:Feature. ?subject rdfs:label '{key}'}}""")
        results_update = get_connection_fuseki(host, query)

        result_2 = pd.json_normalize(results_update["results"]["bindings"])

        query = (f"""INSERT DATA {{<urn:uuid:{uuid_ScaleOfFeature}> rdf:type rprov:{name}, owl:NamedIndividual;
                      rprov:{rprovName} "{value}";
                      rdfs:label "{rprovName} {key}";
                      rprov:toFeature <{result_2["subject.value"][0]}>;
                      rprov:wasGeneratedByDUA  <urn:uuid:{uuid_DeterminationOfScaleOfFeature}>;
                    }}""")
        sparqlupdate.setQuery(prefix+query)
        sparqlupdate.setMethod(POST)
        sparqlupdate.query()


def uploadUniqueValues(sparqlupdate,host,dic, level_measurement, uuid_DeterminationOfScaleOfFeature, name, rprovName):
    with st.spinner("Uploading unique values..."):
        for key, value in dic.items():
            uuid_ScaleOfFeature = uuid.uuid4()
            uuid_UniqueValues = uuid.uuid4()

            query = (f"""PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                        PREFIx rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    SELECT ?subject WHERE {{?subject rdf:type rprov:Feature. ?subject rdfs:label '{key}'}}""")
            results_update = get_connection_fuseki(host, query)

            result_2 = pd.json_normalize(results_update["results"]["bindings"])

            #sparqlupdate = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")

            query = (f"""INSERT DATA {{<urn:uuid:{uuid_ScaleOfFeature}> rdf:type rprov:{name}, owl:NamedIndividual;
                              rprov:{rprovName} <urn:uuid:{uuid_UniqueValues}>;
                              rdfs:label "{rprovName} {key}";
                              rprov:toFeature <{result_2["subject.value"][0]}>;
                              rprov:wasGeneratedByDUA  <urn:uuid:{uuid_DeterminationOfScaleOfFeature}>;
                            }}""")
            sparqlupdate.setQuery(prefix+query)
            sparqlupdate.setMethod(POST)
            sparqlupdate.query()

            if level_measurement[key] == "Nominal":
                i = 0
                for values in value:
                    query = (f"""INSERT DATA {{<urn:uuid:{uuid_UniqueValues}> rdf:type rdf:Bag, owl:NamedIndividual;
                                          rdf:_{i}  '{values}';}}""")
                    sparqlupdate.setQuery(prefix + query)
                    sparqlupdate.setMethod(POST)
                    sparqlupdate.query()
                    i = i + 1
            else:
                i = 0
                for values in value:
                    query = (f"""INSERT DATA {{<urn:uuid:{uuid_UniqueValues}> rdf:type rdf:Seq, owl:NamedIndividual;
                                          rdf:_{i}  '{values}';}}""")
                    sparqlupdate.setQuery(prefix + query)
                    sparqlupdate.setMethod(POST)
                    sparqlupdate.query()
                    i = i + 1
    st.success("Upload successful")





def uploadDataRestrictionSeq(sparqlupdate,host,dic , uuid_DeterminationOfScaleOfFeature, name, rprovName):
    for key, value in dic.items():
        uuid_ScaleOfFeature = uuid.uuid4()
        uuid_DataRestriction = uuid.uuid4()

        query = (f"""PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                    PREFIx rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT ?subject WHERE {{?subject rdf:type rprov:Feature. ?subject rdfs:label '{key}'}}""")
        results_update = get_connection_fuseki(host, query)

        result_2 = pd.json_normalize(results_update["results"]["bindings"])

        query = (f"""INSERT DATA {{<urn:uuid:{uuid_ScaleOfFeature}> rdf:type rprov:{name}, owl:NamedIndividual;
                          rdf:{rprovName} <urn:uuid:{uuid_DataRestriction}>;
                          rdfs:label "{rprovName} {key}";
                          rprov:toFeature <{result_2["subject.value"][0]}>;
                          rprov:wasGeneratedByDUA  <urn:uuid:{uuid_DeterminationOfScaleOfFeature}>;
                        }}""")
        sparqlupdate.setQuery(prefix+query)
        sparqlupdate.setMethod(POST)
        sparqlupdate.query()

        i = 0
        for values in value:
            query = (f"""INSERT DATA {{<urn:uuid:{uuid_DataRestriction}> rdf:type rdf:Seq, owl:NamedIndividual;
                                  rdf:_{i}  '{values}';}}""")
            sparqlupdate.setQuery(prefix + query)
            sparqlupdate.setMethod(POST)
            sparqlupdate.query()
            i = i + 1


def deleteWasGeneratedByDUA(sparqlupdate,df, activity):  # panda df
    st.write("-----")

    query = (f"""
            DELETE {{?object ?property ?value.
            ?object ?property ?value.}}
            WHERE{{?object ?property ?value; rprov:wasGeneratedByDUA <{df["DUA.value"][0]}>}}""")

    sparqlupdate.setQuery(prefix+query)
    sparqlupdate.setMethod(POST)
    sparqlupdate.query()

    query = (f"""
            DELETE {{?object ?property ?value.
            ?object ?property ?value.}}
            WHERE{{?object ?property ?value; rdf:type  rprov:{activity}}}""")

    sparqlupdate.setQuery(prefix+query)
    sparqlupdate.setMethod(POST)
    sparqlupdate.query()

def getAttributes(host):

    if not any(key.startswith('level_of_measurement_') for key in st.session_state):
        st.session_state["dataframe_feature_names"] = get_feature_names(host)

    try:
        st.session_state["level_of_measurement_dic"], st.session_state["DF_feature_scale_name"] = getFeatureScale(host)
        for key, value in st.session_state["level_of_measurement_dic"].items():
            st.session_state[f'level_of_measurement_{key}'] = value
    except:
        st.session_state["DF_feature_scale_name"] = pd.DataFrame()
        # st.session_state["level_of_measurement_dic"] = dict()

    try:
        st.session_state["volatility_of_features_dic"], st.session_state[
            "DF_feature_volatility_name"] = getFeatureVolatility(host)
    except:
        st.session_state["volatility_of_features_dic"] = dict()

    try:
        st.session_state["unique_values_dict"] = getUniqueValuesSeq(host)
    except Exception as e:
        st.error(
            "No Unique Values in database. If this is the first time a new dataset is uploaded please define a scale for each feature and upload the unique values.")
    if "loaded_feature_sensor_precision_dict" not in st.session_state:
        st.session_state["loaded_feature_sensor_precision_dict"], st.session_state[
            "DF_feature_sensor_precision_dict"] = getSensorPrecision(host)