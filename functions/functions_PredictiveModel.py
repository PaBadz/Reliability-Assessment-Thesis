from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode,ColumnsAutoSizeMode
from streamlit_option_menu import option_menu
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.impute import  SimpleImputer
from sklearn.compose import ColumnTransformer, make_column_selector
import pandas as pd
import streamlit as st
import json
import numpy as np
from streamlit_option_menu import option_menu
import pandas as pd
import streamlit as st
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier


def add_parameter_ui(clf_name):
    params = dict()
    if clf_name == 'SVM':
        C = st.sidebar.slider('C', 0.01, 10.0)
        params['C'] = C
    elif clf_name == 'KNN':
        K = st.sidebar.slider('K', 1, 15)
        params['K'] = K
    else:
        max_depth = st.sidebar.slider('max_depth', 2, 15)
        params['max_depth'] = max_depth
        n_estimators = st.sidebar.slider('n_estimators', 1, 100)
        params['n_estimators'] = n_estimators
    return params

def get_classifier(clf_name, params):
    clf = None
    if clf_name == 'SVM':
        clf = SVC(C=params['C'])
    elif clf_name == 'KNN':
        clf = KNeighborsClassifier(n_neighbors=params['K'])
    else:
        clf = clf = RandomForestClassifier(n_estimators=params['n_estimators'],
            max_depth=params['max_depth'], random_state=1234)
    return clf


# def switch_page(page_name: str):
#     from streamlit.runtime.scriptrunner import RerunData, RerunException
#     from streamlit.source_util import get_pages
#
#     def standardize_name(name: str) -> str:
#         return name.lower().replace("_", " ")
#
#     page_name = standardize_name(page_name)
#
#     pages = get_pages("../Home.py")
#
#     for page_hash, config in pages.items():
#         if standardize_name(config["page_name"]) == page_name:
#             raise RerunException(
#                 RerunData(
#                     page_script_hash=page_hash,
#                     page_name=page_name,
#                 )
#             )
#     page_names = [standardize_name(config["page_name"]) for config in pages.values()]
#
#     raise ValueError(f"Could not find page {page_name}. Must be one of {page_names}")
#
#
#

