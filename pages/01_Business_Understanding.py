import uuid

from SPARQLWrapper import SPARQLWrapper, POST
from functions.functions import *
from functions.functions_DataPreparation import  *

try:
    host = (f"http://localhost:3030{st.session_state.fuseki_database}/sparql")
    host_upload = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")
except:
    st.info("Please select a database first")
    st.stop()

st.markdown("## Business Understanding")
st.write("""The business understanding is the first step of the CRISP-DM process. 
In this step you will be able to choose between the different assessment approaches""")
approach = st.selectbox("Choose assessment approach", ["Perturbation_Approach"])
if st.button("Upload Assessment Approach", type="primary"):


    try:
        getApproach(host)
    except Exception as e:
        uuid_activity = uuid.uuid4()
        uuid_entity = uuid.uuid4()
        uploadApproach(host_upload, uuid_activity, uuid_entity)





