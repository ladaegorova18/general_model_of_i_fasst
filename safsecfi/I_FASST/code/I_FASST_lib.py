# Copyright (c) 2024 Robert Bosch GmbH
# SPDX-License-Identifier: MIT

import timeit
start = timeit.default_timer()
import io
import os
import time
import json
import textwrap
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from lxml import etree
import itertools
from itertools import product
from tabulate import tabulate

######################################Configurable inputs#####################################
#Path to input files
dirname = os.path.dirname(__file__)

INPUT_FILE_IDX = 2
zero_paths_counter = 0
more_than_zero_paths_counter = 0

#output files with date and time stamp
timestr = time.strftime("%Y%m%d-%H%M%S")
interaction_sequences_txt = "interaction_sequences_output" + timestr + ".txt"
output_nx_name = "nx_graph" + timestr + ".png"

#path to store output files
output_file_nxdraw = os.path.join(dirname, '..', 'build', output_nx_name)
interaction_sequences = os.path.join(dirname, '..', 'build', interaction_sequences_txt)

file_path_inputfile1 = os.path.join(dirname, '..', 'data', 'inputfile1.xml')
file_path_inputfile2 = os.path.join(dirname, '..', 'data', 'inputfile2.xml')
#Parsing input xml using etree parser of lxml
tree_inputfile1 = etree.parse(file_path_inputfile1) #Parse input file 1
root_inputfile1 = tree_inputfile1.getroot() #Get the root element of the xmi

tree_inputfile2 = etree.parse(file_path_inputfile2) #Parse input file 2
root_inputfile2 = tree_inputfile2.getroot() #Get the root element of the xmi

# tree_inputfile3 = etree.parse(file_path_inputfile3)
# root_inputfile3 = tree_inputfile3.getroot()

# tree_inputfile4 = etree.parse(file_path_inputfile4)
# root_inputfile4 = tree_inputfile4.getroot()

# tree_inputfile5 = etree.parse(file_path_inputfile5)
# root_inputfile5 = tree_inputfile5.getroot()

# tree_inputfile6 = etree.parse(file_path_inputfile6)
# root_inputfile6 = tree_inputfile6.getroot()

# tree_inputfile7 = etree.parse(file_path_inputfile7)
# root_inputfile7 = tree_inputfile7.getroot()

#Define namespace
ns = {
    'uml':'http://schema.omg.org/spec/UML/2.1',
    'xmi':'http://schema.omg.org/spec/XMI/2.1',
    'SysML':'http://www.omg.org/spec/SysML/20120322/SysML',
    'sysml':'http://www.omg.org/spec/SysML/20080501/SysML-profile'
    }
##############################################################################################


def get_iterator( path, var_select_etree):
    "get iterator based on input i.e. 1 for input file 1, 2 for input file 2 or 3 for input file 3"
    if var_select_etree == 1:
        element_object = root_inputfile1.iterfind(path=path, namespaces=ns) #Iterator from parsed input file 1
    elif var_select_etree == 2:
        element_object = root_inputfile2.iterfind(path=path, namespaces=ns) #Iterator from parsed input file 2
    # elif var_select_etree == 3:
    #     element_object = root_inputfile3.iterfind(path=path, namespaces=ns) #Iterator from parsed input file 3
    # elif var_select_etree == 4:
    #     element_object = root_inputfile4.iterfind(path=path, namespaces=ns) #Iterator from parsed input file 4
    # elif var_select_etree == 5:
    #     element_object = root_inputfile5.iterfind(path=path, namespaces=ns) #Iterator from parsed input file 5
    # elif var_select_etree == 6:
    #     element_object = root_inputfile6.iterfind(path=path, namespaces=ns) #Iterator from parsed input file 6
    # elif var_select_etree == 7:
    #     element_object = root_inputfile7.iterfind(path=path, namespaces=ns) #Iterator from parsed input file 7
    # else:
    #     print("Invalid iterator type entered!")
        #assert "Invalid selection of parsed lxml etree"
    return element_object

def get_values_from_dict(FeID_compID_dict):
    components_set = set()
    for feature in FeID_compID_dict:
        for component_id in FeID_compID_dict[feature]:
            components_set.add(component_id)
    return components_set

def get_commonelementIDsset(secComponentID_set, safComponentID_set):
    # safComponentID_set.add("EAID_9989F016_048C_1FF7_A482_3F6F1CDCAC69") # for debug
    common_set = safComponentID_set.intersection(secComponentID_set)
    return common_set

def get_uniqueelementIDsset(sf_set, secsafComponentID_set):
    subtract_set = sf_set.difference(secsafComponentID_set)
    return subtract_set    

def get_iterator_attributes( element):
    "Get id, name and type attributes from the iteratable element/object"
    id = element.get('{http://schema.omg.org/spec/XMI/2.1}id')
    name = element.get('name')
    type = element.get('{http://schema.omg.org/spec/XMI/2.1}type')
    return id, name, type

def has_ancestor(element):
    # if the element has an ancestor with a specific id
    parents = element.xpath("ancestor::*[tag='{}']".format('ownedAttribute'), namespaces=ns)

    return parents

def search_allocatedUMLelement_byID(element_id):
# Search for a lifeline
    
    path_search_by_id = ".//packagedElement[@xmi:id='{}']".format(element_id)
    id_iterator = get_iterator(path_search_by_id, INPUT_FILE_IDX)
    element = None
    for temp_element in id_iterator:
        element = temp_element

    classifier_id = element_id
    type = element.get('{http://schema.omg.org/spec/XMI/2.1}type')
    if type == 'uml:InstanceSpecification':
        classifier_id = element.get('classifier')
        path_search_by_id = ".//packagedElement[@xmi:id='{}']".format(classifier_id)
        id_iterator = get_iterator(path_search_by_id, INPUT_FILE_IDX)
        element = None
        for temp_element in id_iterator:
            element = temp_element

    # parent = has_ancestor(element)

    "Get id, name and type attributes from the iteratable element/object"
    id = element.get('{http://schema.omg.org/spec/XMI/2.1}id')
    name = element.get('name')
    return id, name, type, classifier_id

def query_twodicts_by_key(msg_src, mappedLLOccurSpecID_LLID_dict, mappedLLID_classifierID_dict):
    msg_srcClassifierID = None
    if msg_src in mappedLLOccurSpecID_LLID_dict:
        covered = mappedLLOccurSpecID_LLID_dict[msg_src]
        if covered in mappedLLID_classifierID_dict:
            msg_srcClassifierID = mappedLLID_classifierID_dict[covered]

    return msg_srcClassifierID

def get_interfacebyID(feature, element):
    # We don't have interfaces so far in our diagram so this method is not relevant to us 
    return None, None, None, None

def get_listnames_from_listIDs_fromdictwithmissingkeys(relCompID_list, nodeID_name_labeldict):
    relCompNames_list = []
    for compId in relCompID_list:
        if compId in nodeID_name_labeldict:
            relCompNames_list.append(nodeID_name_labeldict[compId])
    return relCompNames_list

def create_multidi_graph(node_set, edge_list):
    graph = nx.MultiDiGraph()
    graph.add_nodes_from(node_set)
    graph.add_edges_from(edge_list)        
    pos = nx.circular_layout(graph)
    plt.figure(figsize=(50,50))
    # nx.draw(graph, pos, labels = node_label_dict, with_labels = True)
    # plt.title(graph_title)
    # plt.savefig(output_file_nxdraw)
    return graph

def create_table_for_interactingfeatures(listoflistnames):
    table = [["Names"]]
    for row in listoflistnames:
        table.append(row)

    print(tabulate(table, tablefmt="grid"))


def get_type_by_id( element_id, iterator_type):
    "Get xmi_type corresponding to xmi_id by searching for the element of this ID in a particular input file"
    type = None
    name = None
    id = None
    classifier_id = None
    path_search_by_id = ".//packagedElement[@xmi:id='{}']".format(element_id)
    id_iterator = get_iterator(path_search_by_id, iterator_type)
    path_search_by_idref = ".//element[@xmi:idref='{}']".format(element_id)
    idref_iterator = get_iterator(path_search_by_idref, iterator_type)
    for element in id_iterator:
        id, name, type = get_iterator_attributes(element)
    if id == None: #if a packaged element having this ID wasn't found
        for element in idref_iterator: #iterate into elements with id as idref
            id, name, type = get_iterator_attributes(element)
    if type == "uml:InstanceSpecification": #if the element is an instance of a class or component, then get the id of the class or component.
        classifier_id = element.get('classifier')
    return name, type, classifier_id

def supplier_typeNone_handler( element):
    "handler to find element if supplier_type is None/not found"
    iterator_type = None
    stereotype = None
    #Configure the xml input files in which the search is to be performed
    for i,v in enumerate([3,4,5,6,7]): #[3,4,5,6,7] refers to the xml input files in which the search will be performed.
        name, type, c_id = get_type_by_id(element, v) #c_id refers to the classifier id corresponding to the input element_id; ignore c_id in this case
        #print("Debug!...element_id: ", element, " name: ", name, " type: ", type)
        if type != None and element != None:
            #print("\nDebug!...supplier_id: ", element, " name: ", name, " type: ", type, " iterator_type: ", v)
            if type == "uml:Component":
                stereotype = get_stereotype_by_path_andID(element, v)
            iterator_type = v
            break
    return name, type, id, stereotype, iterator_type

def get_stereotype_path( element):
    "Get the stereotype path by passing the xmi element ID"
    #Configure component_stereotype_path and composition_stereotype_path
    component_stereotype_path = ".//thecustomprofile:COMPONENT__Software_Component[@base_Component='{}']".format(element)
    # component_stereotype_path = ".//thecustomprofile:COMPONENT__Software_Component[@base_Component='{}']".format(element)
    composition_stereotype_path = ".//thecustomprofile:COMPONENT__Software_Composition[@base_Component='{}']".format(element)
    # composition_stereotype_path = ".//{xmi}:COMPONENT__Software_Composition[@base_Component='{}']".format(element)
    return component_stereotype_path, composition_stereotype_path

def get_stereotype_from_stereotype_iterator( iterator):
    "get the stereotype by iterating through the iterator"
    stereotype = None
    for element in iterator:
        stereotype = element.get('__EAStereoName')
    return stereotype

def get_stereotype_by_path_andID( element_id, iterator_type):
    "Get stereotype (__EAStereoName) corresponding to xmi_id and search_path for the provided iterator, i.e. the input file in which the search is to be performed"
    stereotype = None
    component_stereotype_path, composition_stereotype_path = get_stereotype_path(element_id)
    component_stereotype_iterator = get_iterator(component_stereotype_path, iterator_type)
    stereotype = get_stereotype_from_stereotype_iterator(component_stereotype_iterator)
    if stereotype == None:
        composition_stereotype_iterator = get_iterator(composition_stereotype_path, iterator_type)
        stereotype = get_stereotype_from_stereotype_iterator(composition_stereotype_iterator) 
    return stereotype

def get_classifier_details_from_itsID( classifier_id, iterator_type):
    "Search classifier details using its ID to obtain its name, type, and stereotype"
    classifier_stereotype = None
    classifier_name, classifier_type, id = get_type_by_id(classifier_id, iterator_type) #the output "id" here refers to a dummy variable (classifier id) and this variable will not be used in the if condition below
    if classifier_type == "uml:Component":
        classifier_stereotype = get_stereotype_by_path_andID(classifier_id, iterator_type)
    return classifier_name, classifier_type, classifier_stereotype

def get_activity_list( element, iterator_type):
    "Get activity(ies) for each feature package ID"
    activity_search_path = ".//packagedElement[@xmi:id='{}'][@xmi:type='uml:Package']/.//*[@xmi:type='uml:Activity']".format(element)
    action_search_path = ".//packagedElement[@xmi:id='{}'][@xmi:type='uml:Package']/.//*[@xmi:type='uml:Action']".format(element)
    activity_iterator = get_iterator(activity_search_path, iterator_type)
    action_iterator = get_iterator(action_search_path, iterator_type)
    activity_id_list = []
    activity_dict = {}
    for object in activity_iterator:
        activity_id, activity_name, activity_type = get_iterator_attributes(object)
        activity_id_list.append(activity_id)
        activity_dict.update({activity_id:activity_name})
    for object in action_iterator:
        action_id, action_name, action_type = get_iterator_attributes(object)
        activity_id_list.append(action_id)
        activity_dict.update({action_id:action_name})
    return activity_id_list, activity_dict

def get_supplierIDs_per_activity( activity, iterator_type):
    "Get all instance specification of allocated components for each activity; info: no repetition of components expected here"
    abstraction_search_path = ".//packagedElement[@xmi:type='uml:Dependency'][@supplier='{}']".format(activity)
    # abstraction_search_path = ".//packagedElement[@xmi:type='uml:Dependency'][@client='{}']".format(activity)
    realization_search_path = ".//packagedElement[@xmi:type='uml:Realization'][@supplier='{}']".format(activity)
    # realization_search_path = ".//packagedElement[@xmi:type='uml:Realization'][@client='{}']".format(activity)
    
    abstraction_iterator = get_iterator(abstraction_search_path, iterator_type)
    realization_iterator= get_iterator(realization_search_path, iterator_type)
    abstraction_supplier_ids_list = []
    for element in abstraction_iterator:
        abstraction_supplier_id = element.get('client')
        # abstraction_supplier_id = element.get('supplier')
        abstraction_supplier_ids_list.append(abstraction_supplier_id)
    for element in realization_iterator:
        abstraction_supplier_id = element.get('client')
        # abstraction_supplier_id = element.get('supplier')
        abstraction_supplier_ids_list.append(abstraction_supplier_id)
    return abstraction_supplier_ids_list

def get_supplierIDs_set_per_feature( feature_id, feature_id_name_dict, iterator_type):
    "Get a set of supplier IDs for a feature"
    activity_list = []
    feature_supplierIDs_set = set()
    featureID_activityID_dict = {}
    activity_id_list, activity_dict = get_activity_list(feature_id, iterator_type) #get all activities for a feature
    featureID_activityID_dict.update({feature_id:activity_id_list})
    activity_supplierID_dict = {} #{activity_id:[list of supplier IDs]} can be used later for behavioral analysis
    activity_list = [value for value in activity_dict.values()]
    #print("Debug! Feature: ", feature_id_name_dict[feature_id], " len(activity_id_list): ", len(activity_id_list), " activities: ", activity_list)
    for list_element in activity_id_list: #for each activity
        activity_supplierIDs_list = get_supplierIDs_per_activity(list_element, iterator_type) #get supplier_ids_list for each activity
        activity_supplierID_dict.update({list_element:activity_supplierIDs_list})
        feature_supplierIDs_set.update(activity_supplierIDs_list) #append the obtained supplier_ids_list to a supplier_ids_set
    #print("\nfeature: ", feature_id, " feature_name: ", feature_id_name_dict[feature_id], " feature_activity_dict: ", activity_dict, " activity_supplierID_dict", activity_supplierID_dict)
    return set(activity_id_list), feature_supplierIDs_set, activity_supplierID_dict, activity_dict, featureID_activityID_dict    

def get_activity_component_mapping( activityID_supplierID_dict, supplierID_componentID_dict):
    "Input 1 {activityID:[supplier ID1, supplier ID2,..]}  Input 2 {supplierID1:componentID1, supplierID2:componentID2,..} Expected output {activityID:[componentID1, componentID2,..]}"
    QD = QueryDataStruct()
    activityID_componentsID_dict = {}
    for k,v in activityID_supplierID_dict.items():
        componentsID_peractivity_list = []
        for j,l in enumerate(v):
            if l in supplierID_componentID_dict.keys():
                value = QD.query_dict_by_key(supplierID_componentID_dict, l)
                componentsID_peractivity_list.append(value)
            else:
                continue
        if len(componentsID_peractivity_list) != 0:
            activityID_componentsID_dict.update({k:componentsID_peractivity_list})
    return activityID_componentsID_dict

def get_component_from_interfaceID( interface_id, iterator_type, pI_rI_selection_flag):
    "Get the component which has the given provided or required interface ID; the function returns pI (provided interface) when flag is 0 and rI (required interface) when flag is 1"
    if pI_rI_selection_flag == 0: #select provided interface
        search_path = ".//packagedElement[@xmi:type='uml:Component']/provided[@xmi:id = '{}']/..".format(interface_id)
    elif pI_rI_selection_flag == 1: #select required interface
        search_path = ".//packagedElement[@xmi:type='uml:Component']/required[@xmi:id = '{}']/..".format(interface_id)
    else:
        print("Invalid flag!")
    iterator = get_iterator(search_path, iterator_type) #search in the specified input file
    component_id = None
    component_name = None
    component_type = None
    for element in iterator:
        component_id, component_name, component_type = get_iterator_attributes(element)
    return component_id, component_name, component_type

def get_supplier_structEleIDs_set( supplier_IDs_set):
    "Get sructural element IDs set (e.g. set of components, compositions, class etc.) from the set of supplier IDs; this function may need to be modified based on the modeling sytle used for the software architecture model"
    feature_struct_element_ID_set = set() #set of components that corresponds to set of input supplier IDs (instance specification, component,...)
    component_set = set()
    componentID_name_dict = {}
    componentID_type_dict = {}
    
    supplierID_type_dict = {} #dict {suplier id:type}
    classifierID_type_dict = {} #dict {component:type} of components traced by their corresponding instance specification
    classifierID_name_dict = {}
    supplierID_to_classifierID_dict = {} #dict {supplier ID: classifier ID} of key as supplier ID (here instance specification) and its corresponding component as value
    non_classifierID_type_dict = {} #dict of components not traced by their corresponding instance specification
    non_classifierID_name_dict = {}
    requirementID_type_dict = {} #ID {requirement:type} will be derived from SW requirements package
    requirementID_name_dict = {} #dict {re_ID:req_name}
    unknown_non_classifierID_type_dict = {} #dict {supplier_id:its_type}, collect suppliers whos type could not found in the input xmi files
    classifierID_stereotype_dict = {}
    non_classifierID_stereotype_dict = {}
    component_ID_stereotype_dict = {}
    supplierID_componentID_dict = {}
    supplier_stereotype = None
    for element in supplier_IDs_set:
        supplier_name, supplier_type, classifier_id = get_type_by_id(element, 1)#check type of supplier id e.g. instance specification, class, artifact, activity, etc.
        supplier_stereotype = None
        # supplier_stereotype = get_stereotype_by_path_andID(element, 1)
        supplierID_type_dict.update({element:supplier_type})
        if supplier_type == "uml:InstanceSpecification":
            classifier_name, classifier_type, classifier_stereotype = get_classifier_details_from_itsID(classifier_id, 3)
            classifierID_type_dict.update({classifier_id:classifier_type})
            classifierID_name_dict.update({classifier_id:classifier_name})
            classifierID_stereotype_dict.update({classifier_id:classifier_stereotype})
            supplierID_to_classifierID_dict.update({element:classifier_id})
            supplierID_componentID_dict.update({element:classifier_id})
        elif supplier_type == "uml:Class": #store in requirementID_type_dict if all such elements are found to be SW requirements
            requirementID_type_dict.update({element:supplier_type})
            requirementID_name_dict.update({element:supplier_name})
        elif supplier_type == "uml:Component":
            non_classifierID_type_dict.update({element:supplier_type})
            non_classifierID_name_dict.update({element:supplier_name})
            non_classifierID_stereotype_dict.update({element:supplier_stereotype})
            supplierID_componentID_dict.update({element:element})
        elif supplier_type == "uml:Activity": #dependency between activities are ignored when finding components allocated to each activity
            pass
        elif supplier_type == "uml:Artifact":
            pass
        elif supplier_type == "uml:Constraint":
            pass
        elif supplier_type == None:
            name, type, id, element_stereotype, iterator_type = supplier_typeNone_handler(element)
            if type == "uml:Class" and iterator_type == 7:
                requirementID_type_dict.update({element:type})
                requirementID_name_dict.update({element:name})
            elif type == "uml:Component":
                non_classifierID_type_dict.update({element:type})
                non_classifierID_name_dict.update({element:name})
                non_classifierID_stereotype_dict.update({element:element_stereotype})
                supplierID_componentID_dict.update({element:element})
            elif type == "uml:ProvidedInterface":
                pI_flag = 0 #return component that corresponds to pI interface
                pIcomponent_id, pIcomponent_name, pIcomponent_type = get_component_from_interfaceID(element, 3, pI_flag) #get component id, name, stereotype
                pIcomponent_stereotype = get_stereotype_by_path_andID(pIcomponent_id, 3)
                non_classifierID_type_dict.update({pIcomponent_id:pIcomponent_type})
                non_classifierID_name_dict.update({pIcomponent_id:pIcomponent_name})
                non_classifierID_stereotype_dict.update({pIcomponent_id:pIcomponent_stereotype})
                supplierID_componentID_dict.update({element:element})
            else:
                unknown_non_classifierID_type_dict.update({element:type})
    componentID_type_dict = {**classifierID_type_dict, **non_classifierID_type_dict}
    component_ID_stereotype_dict = {**classifierID_stereotype_dict, **non_classifierID_stereotype_dict}
    component_set = {key for key in componentID_type_dict.keys()}
    componentID_name_dict = {**classifierID_name_dict, **non_classifierID_name_dict}
    return component_set, componentID_name_dict, componentID_type_dict, supplierID_type_dict, classifierID_type_dict, supplierID_to_classifierID_dict, non_classifierID_type_dict, unknown_non_classifierID_type_dict, requirementID_type_dict, component_ID_stereotype_dict, supplierID_componentID_dict

def get_listnames_from_listIDs( elementIDs_list, elementID_name_dict):
    "Get list of names from a list of their IDs by querying data struct"
    value = None
    element_names_list = []
    for element in elementIDs_list:
        value = elementID_name_dict[element]
        element_names_list.append(value)
    return element_names_list

def get_feature_components( feature_list, feature_id_name_dict, iterator_type):
    "Get component_list, component_dict and feature_component_dict"
    all_componentID_set = set()
    activityID_set = set()
    all_activityID_set = set()
    all_componentID_name_dict = {}
    all_componentID_stereotype_dict = {}
    feature_componentID_dict = {} #dict = {feature_id:{set of component_IDs}}
    all_supplierID_componentID_dict = {}
    all_activityID_name_dict = {}
    all_activity_supplierID_dict = {}
    all_featureID_activityID_dict = {}
    for element in feature_list: #for each feature
        activityID_set, feature_supplier_ids_set, activity_supplierID_dict, activity_dict, featureID_activityID_dict = get_supplierIDs_set_per_feature(element, feature_id_name_dict, iterator_type) #Get supplier set per feature
        componentID_set, componentID_name_dict, componentID_type_dict, supplierID_type_dict, classifierID_type_dict, supplierID_to_classifierID_dict, non_classifierID_type_dict, unknown_non_classifierID_type_dict, requirementID_type_dict, componentID_stereotype_dict, supplierID_componentID_dict = get_supplier_structEleIDs_set(feature_supplier_ids_set)
        all_activityID_set.update(activityID_set)
        all_featureID_activityID_dict.update(featureID_activityID_dict)
        all_activity_supplierID_dict.update(activity_supplierID_dict)
        all_activityID_name_dict.update(activity_dict)
        all_supplierID_componentID_dict.update(supplierID_componentID_dict)
        all_componentID_set.update(componentID_set)
        all_componentID_name_dict.update(componentID_name_dict)
        all_componentID_stereotype_dict.update(componentID_stereotype_dict)
        componentID_list = list(componentID_set)
        feature_componentID_dict.update({element:componentID_list})
        component_list = [value for value in componentID_name_dict.values()]
    return feature_componentID_dict, all_componentID_set, all_componentID_name_dict, all_componentID_stereotype_dict, all_supplierID_componentID_dict, all_activityID_name_dict, all_activity_supplierID_dict, all_featureID_activityID_dict          

def redirect_txt_output( output_file_path, text_to_write):
    "Dump print output in a text file in append mode"
    with open(output_file_path, "a") as external_file: #write/append to file
        received_text = text_to_write
        print(received_text, file=external_file)
        external_file.close()

def query_dict_by_key( dict_to_be_querried, key_to_query):
    "query a dict by key"
    value = dict_to_be_querried[key_to_query]
    return value

def query_dict_by_wlistvalue( dict_to_be_querried, value_to_query):
    "query a dict by value; each value corresponding to a key is a list of items"
    key_list = []
    for k,v in dict_to_be_querried.items():
        for j,l in enumerate(v):
            if l == value_to_query:
                key_list.append(k)
                break
    return key_list

def query_dict_by_value( dict_to_be_querried, value_to_query):
    "query a dict (with a key and a value pair) by value"
    key = [k for k,v in dict_to_be_querried.items() if v == value_to_query]
    return key

def query_lists_for_commonelement( list1, list2, list1ID_name_dict):
    "get common elements of 2 lists using Python's set intersection"
    common_elementID_list = list(set(list1).intersection(list2))
    common_elementname_list = []
    common_elementname_list = get_listnames_from_listIDs(common_elementID_list, list1ID_name_dict) #getting names for debugging
    return common_elementID_list, common_elementname_list

def query_lists_for_uniqueelement( list1, list2, list1ID_name_dict):
    "get unique elements present in 2 lists using Python's symmetric difference"
    unique_elementID_list = list(set(list1).symmetric_difference(set(list2)))
    unique_elementname_list = []
    unique_elementname_list = get_listnames_from_listIDs(unique_elementID_list, list1ID_name_dict) #getting names for debugging
    return unique_elementID_list, unique_elementname_list

def get_listoflistnames_from_listoflistIDs( listIDs_of_list, elementID_name_dict):
    "For a list of list of IDs, create a list of list of names"
    names_list_of_list = []
    for element in listIDs_of_list:
        element_name_list = get_listnames_from_listIDs(element, elementID_name_dict)
        if element_name_list not in names_list_of_list:
            names_list_of_list.append(element_name_list)
    return names_list_of_list

def get_itertoolsproductoflists( list1, list2):
    "For lists, i.e. list1 and list2, get the product of list1 and list2, and the product of list2 and list1 and combine (summation) the output of both products obtained"
    productfrom1to2_list = list(itertools.product(list1, list2))
    return productfrom1to2_list