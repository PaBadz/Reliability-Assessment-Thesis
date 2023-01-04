import uuid

from SPARQLWrapper import SPARQLWrapper, POST
from functions.functions import *

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
    sparqlupdate = SPARQLWrapper(f"http://localhost:3030{st.session_state.fuseki_database}/update")

    uuid_activity = uuid.uuid4()
    query = (f"""PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                          PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                          PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                          PREFIX prov:  <http://www.w3.org/ns/prov#>
                          PREFIX owl: <http://www.w3.org/2002/07/owl#>
                          PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                          PREFIX instance:<http://www.semanticweb.org/dke/ontologies#> 
                          INSERT DATA {{<http://www.semanticweb.org/dke/ontologies#/ChoiceOfAssessmentApproach{uuid_activity}> rdf:type rprov:ChoiceOfAssessmentApproach, owl:NamedIndividual;
                          rdfs:label "choiceOfAssessment"@en;
                          prov:endedAtTime    "0000-00-00T00:00:00Z";
                          prov:startedAtTime  "0000-00-00T00:00:00Z".}}""")
                            # prov:value '{approach}'^^xsd:string;

    sparqlupdate.setQuery(query)
    sparqlupdate.setMethod(POST)
    sparqlupdate.query()
    uuid_entity = uuid.uuid4()
    query = (f"""PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                          PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                          PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
                          PREFIX prov:  <http://www.w3.org/ns/prov#>
                          PREFIX owl: <http://www.w3.org/2002/07/owl#>
                          PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                          PREFIX instance:<http://www.semanticweb.org/dke/ontologies#> 
                          INSERT DATA {{<http://www.semanticweb.org/dke/ontologies#/{approach}{uuid_entity}> rdf:type rprov:PerturbationApproach, owl:NamedIndividual;
                          rdfs:label "pertApproach" @en;
                          prov:value '{approach}'^^xsd:string;
                          rprov: wasGeneratedByBUA <http://www.semanticweb.org/dke/ontologies#/ChoiceOfAssessmentApproach{uuid_activity};
                          prov:endedAtTime    "0000-00-00T00:00:00Z";
                          prov:startedAtTime  "0000-00-00T00:00:00Z".}}""")
                        # rdfs:label '{approach}'^^xsd:string;#
    sparqlupdate.setQuery(query)
    sparqlupdate.setMethod(POST)
    sparqlupdate.query()




want_to_contribute = st.button("Data Understanding")
if want_to_contribute:
    switch_page("Data Understanding")

want_to_contribute = st.button("Data Preparation")
if want_to_contribute:
    switch_page("Data Preparation")