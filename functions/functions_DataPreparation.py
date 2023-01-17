import streamlit as st
def update_missing_values(key):
    st.write(st.session_state[f'missingValues_{key}_widget'])
    st.session_state[f'missingValues_{key}'] = st.session_state[f'missingValues_{key}_widget']
    # if st.session_state[f'missingValues_{key}'] == "":
    #     del st.session_state['missingValues_of_features_dic'][key]
    # else:
    st.session_state['missingValues_of_features_dic'][key] = st.session_state[f'missingValues_{key}_widget']
