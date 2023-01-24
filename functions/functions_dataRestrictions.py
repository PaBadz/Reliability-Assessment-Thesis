from functions.fuseki_connection import *


#
# def uploadDataRestrictionSeq(sparqlupdate,host,dic , uuid_DeterminationOfScaleOfFeature, name, rprovName, comment_data_restriction):
#     time = getTimestamp()
#     for key, value in dic.items():
#         uuid_ScaleOfFeature = uuid.uuid4()
#         uuid_DataRestriction = uuid.uuid4()
#
#         query = (f"""PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
#                     PREFIx rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#                     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#                 SELECT ?subject WHERE {{?subject rdf:type rprov:Feature. ?subject rdfs:label '{key}'}}""")
#         results_update = get_connection_fuseki(host, query)
#
#         result_2 = pd.json_normalize(results_update["results"]["bindings"])
#
#         query = (f"""INSERT DATA {{<urn:uuid:{uuid_ScaleOfFeature}> rdf:type rprov:{name}, owl:NamedIndividual;
#                           rprov:{rprovName} <urn:uuid:{uuid_DataRestriction}>;
#                           rdfs:label "{rprovName} {key}";
#                           rprov:toFeature <{result_2["subject.value"][0]}>;
#                           rprov:wasGeneratedByDUA  <urn:uuid:{uuid_DeterminationOfScaleOfFeature}>;
#                           prov:generatedAtTime '{time}'^^xsd:dateTime;
#                           rdfs:comment '{comment_data_restriction}';
#                         }}""")
#         try:
#             sparqlupdate.setQuery(prefix+query)
#             sparqlupdate.setMethod(POST)
#             sparqlupdate.query()
#         except Exception as e:
#             st.error(e)
#         i = 0
#         for values in value:
#             query = (f"""INSERT DATA {{<urn:uuid:{uuid_DataRestriction}> rdf:type rdf:Seq, owl:NamedIndividual;
#                                   rdf:_{i}  '{values}';}}""")
#             sparqlupdate.setQuery(prefix + query)
#             sparqlupdate.setMethod(POST)
#             sparqlupdate.query()
#             i = i + 1
#
# def uploadDR(starting_time, host_upload, host, comment_data_restriction):
#     determinationNameUUID = 'DeterminationOfDataRestriction'
#     determinationName = 'DeterminationOfDataRestriction'
#     label = "detDataRestriction"
#     name = 'DataRestriction'
#     rprovName = 'DataRestriction'
#     ending_time = getTimestamp()
#     uuid_determinationDataRestriction = determinationActivity(host_upload, determinationName, label,
#                                                               starting_time, ending_time)
#     uploadDataRestrictionSeq(host_upload, host, st.session_state['data_restrictions_dict'],
#                              uuid_determinationDataRestriction, name,
#                              rprovName, comment_data_restriction)
#
# def getDataRestrictionSeq(data_restriction,host):
#     dictionary_DataRestriction = dict()
#     query = (f"""    SELECT ?label ?containerMembershipProperty ?item WHERE {{
#     ?sub rprov:DataRestriction ?container.
#     ?sub rprov:wasGeneratedByDUA <{data_restriction}>.
#     ?container a rdf:Seq .
#     ?container ?containerMembershipProperty ?item.
#     ?sub rprov:toFeature ?feature.
#     ?feature rdfs:label ?label.
#     FILTER(?containerMembershipProperty!= rdf:type)}}
#     """)
#
#     results_feature_DataRestriction = get_connection_fuseki(host, (prefix+query))
#     results_feature_DataRestriction = pd.json_normalize(results_feature_DataRestriction["results"]["bindings"])
#     results_feature_DataRestriction= results_feature_DataRestriction.groupby("label.value")["item.value"].apply(list)
#
#     for _index, row in results_feature_DataRestriction.items():
#         dictionary_DataRestriction[_index] = row
#
#     return dictionary_DataRestriction
#
#
# def getDataRestrictionSeqDeployment(data_restriction,feature,host):
#     dictionary_DataRestriction = dict()
#     query = (f"""
#
#     SELECT ?dataRestrictionEntity ?feature ?label ?seq ?item WHERE {{
#     <{data_restriction}> rprov:modelingEntityWasDerivedFrom ?dataRestrictionEntity.
#     ?dataRestrictionEntity rdf:type rprov:DataRestriction.
#     ?dataRestrictionEntity rprov:DataRestriction ?seq.
#     ?seq a rdf:Seq .
#     ?seq ?containerMembershipProperty ?item.
#     ?dataRestrictionEntity rprov:toFeature <{feature}>.
#     ?dataRestrictionEntity rprov:toFeature ?feature.
#     ?feature rdfs:label ?label.
#     FILTER(?containerMembershipProperty!= rdf:type)}}
#     """)
#
#
#     try:
#         results_feature_DataRestriction = get_connection_fuseki(host, (prefix+query))
#
#         results_feature_DataRestriction = pd.json_normalize(results_feature_DataRestriction["results"]["bindings"])
#
#         results_feature_DataRestriction= results_feature_DataRestriction.groupby("label.value")["item.value"].apply(list)
#
#         for _index, row in results_feature_DataRestriction.items():
#             dictionary_DataRestriction[_index] = row
#
#         return dictionary_DataRestriction
#     except:
#         return