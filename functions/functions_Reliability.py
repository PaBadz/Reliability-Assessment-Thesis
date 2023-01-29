import pandas as pd
import streamlit as st
from functions.fuseki_connection import getUniqueValuesSeq, get_connection_fuseki, prefix





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

@st.cache(suppress_st_warning=True)
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
    query = (f"""    SELECT ?featureID ?featureName ?DataUnderstandingEntityID ?DUA ?values ?label{{
    ?featureID rdf:type rprov:Feature .
    ?featureID rdfs:label ?featureName.
    ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
	?DataUnderstandingEntityID rprov:perturbedFeature ?featureID.
    ?DataUnderstandingEntityID rprov:generationAlgorithm ?DUA.
    ?DataUnderstandingEntityID rprov:values ?values.
    ?DataUnderstandingEntityID rdfs:label ?label.
    }}
    """)

    results_feature_PerturbationOption = get_connection_fuseki(host, (prefix + query))
    results_feature_PerturbationOption = pd.json_normalize(results_feature_PerturbationOption["results"]["bindings"])


    results_feature_PerturbationOption = results_feature_PerturbationOption[["featureID.value","featureName.value","DataUnderstandingEntityID.value","DUA.value", "values.value", "label.value"]]
    results_feature_PerturbationOption.columns = ['FeatureID','FeatureName', 'DataUnderstandingEntity', 'PerturbationOption', "Settings","label"]

    return results_feature_PerturbationOption



# changed DeterminationOfDataRestriction to DataRestriction
def getRestriction(host):
    dictionary_DataRestriction = dict()
    query = (f"""SELECT ?sub ?seq?item ?label ?featureName ?seq ?containerMembershipProperty ?comment WHERE {{
    ?sub rdf:type rprov:DeterminationOfDataRestriction.
    ?seq rprov:wasGeneratedByDUA ?sub.
    ?seq rdfs:label ?label.
    ?seq rdfs:comment ?comment.
    ?seq rprov:toFeature ?feature.
    ?feature rdfs:label ?featureName.
    ?seq rprov:restriction ?list.
    ?list ?containerMembershipProperty ?item.
    FILTER(?containerMembershipProperty!= rdf:type)
    }}
    """)

    results_feature_DataRestriction = get_connection_fuseki(host, (prefix + query))
    results_feature_DataRestriction = pd.json_normalize(results_feature_DataRestriction["results"]["bindings"])
    results_feature_DataRestriction = \
        results_feature_DataRestriction.groupby(["sub.value","seq.value", "label.value", "featureName.value", "comment.value"], as_index=False)[
            "item.value"].agg(list)
    # results_feature_DataRestriction = results_feature_DataRestriction.groupby(["time.value","sub.value","label.value"]).apply(lambda x: [list(x['item.value'])]).apply(pd.Series)
    results_feature_DataRestriction.columns = ['DataRestrictionActivity', 'DataRestrictionEntity', 'Label', 'Feature', 'Comment', "Value"]

    return results_feature_DataRestriction


def changeAlgorithm(key):
    st.session_state.default[key] = st.session_state[f"algo_{key}"]

def changePerturbationOption(column):
    st.session_state.perturbationOptions[column] = st.session_state[f"perturbationOption_{column}"]






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