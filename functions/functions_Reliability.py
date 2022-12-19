from functions.functions import *
from functions.functions_DataUnderstanding import *
from functions.fuseki_connection import *





# ------------------------------------------------------------------------------------------------------------------------
def deleteTable(key):
    if st.button("Delete Table", type="primary", key=key):
        st.session_state.df_r = pd.DataFrame(
            columns=st.session_state.dataframe_feature_names["featureName.value"].tolist())

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

def defaultValuesCardinalRestriction(key):
    st.session_state[f'data_restrictions_{key}_cardinal'] = [float(st.session_state.unique_values_dict[key][0]),
                                                             float(st.session_state.unique_values_dict[key][-1])]


def defaultValuesOrdinalRestriction(key):
    st.session_state[f'data_restrictions_{key}_ordinal'] = st.session_state.unique_values_dict[key]


def defaultValuesNominalRestriction(key):
    st.session_state[f'data_restrictions_{key}_nominal'] = st.session_state.unique_values_dict[key]


def getDefault(host):
    try:
        st.session_state["unique_values_dict"] = getUniqueValuesSeq(host)
    except Exception as e:
        st.write(e)
        st.info("Dont forget to upload unique values")



def getPerturbationOptions(host):
    dictionary_DataRestriction = dict()
    query = (f"""    SELECT ?featureID ?featureName ?DataUnderstandingEntityID ?DUA {{
    ?featureID rdf:type rprov:Feature .
    ?featureID rdfs:label ?featureName.
    ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
	?DataUnderstandingEntityID rprov:perturbedFeature ?featureID.
    ?DataUnderstandingEntityID rprov:generationAlgorithm ?DUA.
    }}
    """)

    results_feature_DataRestriction = get_connection_fuseki(host, (prefix + query))
    results_feature_DataRestriction = pd.json_normalize(results_feature_DataRestriction["results"]["bindings"])

    #results_feature_DataRestriction =  results_feature_DataRestriction.groupby(["featureName.value", "DataUnderstandingEntityID.value", "DUA.value"], as_index=False)
    # # results_feature_DataRestriction = results_feature_DataRestriction.groupby(["time.value","sub.value","label.value"]).apply(lambda x: [list(x['item.value'])]).apply(pd.Series)
    #results_feature_DataRestriction.columns = ['Feature', 'DataUnderstandingEntity', 'PertubationOption']

    return results_feature_DataRestriction


# verschiedene restrictions welche eingestellt wurden
# erstmal nicht beachten, kann später eingebaut werden
def getRestriction(host):
    dictionary_DataRestriction = dict()
    query = (f"""    SELECT ?sub ?item ?label ?seq ?time WHERE {{
    ?sub rdf:type rprov:DeterminationOfDataRestriction.
    ?sub prov:endedAtTime ?time.
    ?seq rprov:wasGeneratedByDUA ?sub.
    ?seq rdfs:label ?label.
    ?seq rdf:DataRestriction ?list.
    ?list ?containerMembershipProperty ?item.
    FILTER(?containerMembershipProperty!= rdf:type)
    }}
    """)

    results_feature_DataRestriction = get_connection_fuseki(host, (prefix + query))
    results_feature_DataRestriction = pd.json_normalize(results_feature_DataRestriction["results"]["bindings"])
    results_feature_DataRestriction = \
        results_feature_DataRestriction.groupby(["time.value", "sub.value", "label.value"], as_index=False)[
            "item.value"].agg(list)
    # results_feature_DataRestriction = results_feature_DataRestriction.groupby(["time.value","sub.value","label.value"]).apply(lambda x: [list(x['item.value'])]).apply(pd.Series)
    results_feature_DataRestriction.columns = ['time', 'URN', 'Feature', 'Value']

    return results_feature_DataRestriction


def changeAlgorithm(key):
    st.session_state.default[key] = st.session_state[f"algo_{key}"]


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