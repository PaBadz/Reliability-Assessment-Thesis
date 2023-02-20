import streamlit as st

from functions.fuseki_connection import getDataRestrictionSeqDeployment

color_map = {
    "Red": "#FF4B4B",
    "Orange": "#ffa500",
    "Green": "#43cd80",
    "Blue": "#5f9ea0"
}

def get_perturbation_level(col_name, value):
    plevel = {}
    try:
        if col_name == "perturbation":
            return "Blue"

        for key, value in st.session_state.perturbationOptions_settings.items():
            plevel[key] = next(iter(value.items()))[1]['PerturbationLevel']


        level = plevel.get(col_name, None)
        if level:
            return level

        if value in plevel[col_name].values():
            return plevel[col_name]
        return None
    except:
        pass



def updateDataRestrictionDeployment(feature_name, host):
    try:
        data_restriction_entity = \
            st.session_state.assessmentPerturbationOptions[feature_name]["PerturbationOptionID"][0]

        featureID = st.session_state.assessmentPerturbationOptions[feature_name]["FeatureID"][0]

        st.session_state["data_restriction_deployment"] = getDataRestrictionSeqDeployment(data_restriction_entity,
                                                                                          featureID, host)
    except Exception as e:
        pass

    try:
        st.session_state.data_restriction_final_deployment.update(st.session_state.data_restriction_deployment)
    except Exception as e:
        pass