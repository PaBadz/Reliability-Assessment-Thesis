import streamlit as st

color_map = {
    "Red": "#FF4B4B",
    "Orange": "#ffa500",
    "Green": "#43cd80",
    "Blue": "#5f9ea0"
}

def get_perturbation_level(col_name, value):
    plevel = {}
    try:
        if col_name == "prediction":
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
