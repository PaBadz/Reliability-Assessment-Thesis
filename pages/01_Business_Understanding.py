import uuid

from SPARQLWrapper import SPARQLWrapper, POST
from functions.functions import *
from functions.functions_DataPreparation import *


login()
if st.session_state.username == "user":
    page = st.button("Deployment")
    if page:
        switch_page("Deployment")
    st.stop()

try:
    host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
    host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
except:
    st.info("Please select a database first")
    st.stop()

st.markdown("## Business Understanding")
st.write("""The business understanding is the first step of the CRISP-DM process. 
In this step you will be able to choose between the different assessment approaches""")
st.info("As of right now, perturbation approach is the only approach implemented. Therefore no need to choose.")


