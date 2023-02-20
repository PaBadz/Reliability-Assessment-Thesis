import pandas as pd
import streamlit as st
from functions.fuseki_connection import getUniqueValuesSeq, get_connection_fuseki, prefix, \
    getDataRestrictionSeqDeployment


# ------------------------------------------------------------------------------------------------------------------------
def deleteTable(key):
    if st.button("Delete Table", type="primary", key=key):
        st.session_state.df_aggrid_beginning = pd.DataFrame(
            columns=st.session_state.dataframe_feature_names["featureName.value"].tolist())

# def update_steps(key, method):
#     st.session_state[f"steps_{key}_{method}"] = st.session_state[
#         f"assignedPerturbationLevel_widget_{key}_{method}"]

def update_perturbation_level(key, method):
    st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.session_state[
        f"assignedPerturbationLevel_widget_{key}_{method}"]


def update_value_perturbate(key, method):
    st.session_state[f"value_perturbate{key}_{method}"] = st.session_state[
        f"value_perturbation_widget_{key}_{method}"]


def update_additional_value(key, method):
    st.session_state[f"additional_value_{key}_{method}"] = st.session_state[
        f"additional_value_widget_{key}_{method}"]


def upper_lower_bound(key, method):
    st.session_state[f"additional_value_{key}_{method}_bound"] = st.session_state[
        f"additional_value_widget_{key}_{method}"]

def defaultValuesCardinalRestriction(key):
    st.session_state[f'data_restrictions_{key}_cardinal'] = [float(st.session_state.unique_values_dict[key][0]),
                                                             float(st.session_state.unique_values_dict[key][-1])]


def defaultValuesOrdinalRestriction(key):
    st.session_state[f'data_restrictions_{key}_ordinal'] = st.session_state.unique_values_dict[key]


def defaultValuesNominalRestriction(key):
    st.session_state[f'data_restrictions_{key}_nominal'] = st.session_state.unique_values_dict[key]

@st.cache_data()
def getDefault(host):
    st.session_state["unique_values_dict"] = getUniqueValuesSeq(host)



def getPerturbationRecommendations(host):
    query = (f"""
            SELECT ?featureID ?featureName ?DataUnderstandingEntityID ?DUA ?values ?label ?PerturbationAssessment{{
            ?featureID rdf:type rprov:Feature .
            ?featureID rdfs:label ?featureName.
            ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
	?DataUnderstandingEntityID rprov:perturbedFeature ?featureID.
    ?DataUnderstandingEntityID rprov:generationAlgorithm ?DUA.
    ?DataUnderstandingEntityID rprov:values ?values.
    ?DataUnderstandingEntityID rdfs:label ?label.
            ?PerturbationAssessment rprov:deploymentEntityWasDerivedFrom ?DataUnderstandingEntityID.
            }}""")

    results_feature_recommendation = get_connection_fuseki(host, (prefix + query))
    results_feature_recommendation = pd.json_normalize(results_feature_recommendation["results"]["bindings"])
    results_feature_recommendation = results_feature_recommendation.groupby(['featureName.value', 'DataUnderstandingEntityID.value','label.value'])['DataUnderstandingEntityID.type'].count().reset_index()

    return results_feature_recommendation


def getPerturbationOptions(host):
    # query = (f"""    SELECT ?featureID ?featureName ?PerturbationOptionID ?DUA ?values ?label{{
    # ?featureID rdf:type rprov:Feature .
    # ?featureID rdfs:label ?featureName.
    # ?PerturbationOptionID rdf:type owl:NamedIndividual.
	# ?PerturbationOptionID rprov:perturbedFeature ?featureID.
    # ?PerturbationOptionID rprov:generationAlgorithm ?DUA.
    # ?PerturbationOptionID rprov:values ?values.
    # ?PerturbationOptionID rdfs:label ?label.
    # }}
    # """)
    query = (f"""    SELECT ?featureID ?featureName ?PerturbationOptionID ?generationAlgo ?values ?label ?DataRestrictionEntities ?MA {{
?featureID rdf:type rprov:Feature .
?featureID rdfs:label ?featureName .
?PerturbationOptionID rdf:type owl:NamedIndividual .
?PerturbationOptionID rprov:perturbedFeature ?featureID .
?PerturbationOptionID rprov:generationAlgorithm ?generationAlgo .
?PerturbationOptionID rprov:values ?values .
?PerturbationOptionID rdfs:label ?label .
?PerturbationOptionID rprov:wasGeneratedByMA ?MA
OPTIONAL {{
?PerturbationOptionID rprov:modelingEntityWasDerivedFrom ?DataRestrictionEntities .
?DataRestrictionEntities rdf:type rprov:DataRestriction .
}}
}}
    """)

    results_feature_PerturbationOption = get_connection_fuseki(host, (prefix + query))
    results_feature_PerturbationOption = pd.json_normalize(results_feature_PerturbationOption["results"]["bindings"])



    try:
        results_feature_PerturbationOption = results_feature_PerturbationOption[["featureID.value","featureName.value","PerturbationOptionID.value","generationAlgo.value", "values.value", "label.value", "DataRestrictionEntities.value", "MA.value"]]
        results_feature_PerturbationOption.columns = ['FeatureID','FeatureName', 'PerturbationOptionID', 'PerturbationOption', "Settings","label" ,"DataRestrictionEntities", "ModelingActivity"]
    except:
        results_feature_PerturbationOption = results_feature_PerturbationOption[
            ["featureID.value", "featureName.value", "PerturbationOptionID.value", "generationAlgo.value",
             "values.value", "label.value", "MA.value"]]
        results_feature_PerturbationOption.columns = ['FeatureID', 'FeatureName', 'PerturbationOptionID',
                                                      'PerturbationOption', "Settings", "label",
                                                      "ModelingActivity"]



    return results_feature_PerturbationOption



# changed DeterminationOfDataRestriction to DataRestriction
def getRestriction(host):
    dictionary_DataRestriction = dict()
    query = (f"""SELECT ?sub ?seq?item ?label ?featureName ?seq ?containerMembershipProperty WHERE {{
    ?sub rdf:type rprov:DeterminationOfDataRestriction.
    ?seq rprov:wasGeneratedByDUA ?sub.
    ?seq rdfs:label ?label.
    ?seq rprov:toFeature ?feature.
    ?feature rdfs:label ?featureName.
    ?seq rprov:restriction ?list.
    ?list ?containerMembershipProperty ?item.
    FILTER(?containerMembershipProperty!= rdf:type).
    FILTER NOT EXISTS{{?seq prov:invalidatedAtTime ?time}}
    }}
    """)

    results_feature_DataRestriction = get_connection_fuseki(host, (prefix + query))
    results_feature_DataRestriction = pd.json_normalize(results_feature_DataRestriction["results"]["bindings"])
    if not results_feature_DataRestriction.empty:

        results_feature_DataRestriction = \
            results_feature_DataRestriction.groupby(["sub.value","seq.value", "label.value", "featureName.value", ], as_index=False)[
                "item.value"].agg(list)
        # results_feature_DataRestriction = results_feature_DataRestriction.groupby(["time.value","sub.value","label.value"]).apply(lambda x: [list(x['item.value'])]).apply(pd.Series)
        results_feature_DataRestriction.columns = ['DUA.value', 'DataRestrictionEntity', 'Label', 'Feature', "Value"]

    return results_feature_DataRestriction


def changeAlgorithm(key):
    st.session_state.default[key] = st.session_state[f"algo_{key}"]

def changePerturbationOption(feature_name):
    st.session_state.perturbationOptions[feature_name] = st.session_state[f"perturbationOption_{feature_name}"]







def update_steps(key, method):
    st.session_state[f"steps_{key}_{method}"] = st.session_state[
        f"steps_widget_{key}_{method}"]


def update_value_perturbate(key, method):
    st.session_state[f"value_perturbate{key}_{method}"] = st.session_state[
        f"value_perturbation_widget_{key}_{method}"]


def update_additional_value(key, method):
    st.session_state[f"additional_value_{key}_{method}"] = st.session_state[
        f"additional_value_widget_{key}_{method}"]


def upper_lower_bound(key, method):
    st.session_state[f"additional_value_{key}_{method}_bound"] = st.session_state[
        f"additional_value_widget_{key}_{method}"]