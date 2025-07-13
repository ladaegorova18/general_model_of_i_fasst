import networkx as nx
import os

from enum import Enum
from py2neo import Graph, Node, Relationship

from FIISS.code.converter import Converter
# from converter import Converter # uncomment if want to run FIISS itself

# Create a graph object
graph = Graph("bolt://localhost:7687", name="testdb2", auth=("neo4j", "neo4jneo4j"))

dirname = os.path.dirname(__file__)

PACKAGE_TYPE = "uml:Package"
ACTIVITY_TYPE = "uml:Activity"
MESSAGE_TYPE = "MESSAGE"

SAFETY_TYPE = "SAFETY"
SECURITY_TYPE = "SECURITY"
OTHER_TYPE    = "OTHER"


class InteractionType(Enum):
    SAF_SEC = 1
    SAF_SAF_SEC = 2
    SEC_SAF = 3
    SEC_SAF_SEC = 4
    SAF_SEC_SAF = 5
    SAF_SEC_SEC = 6

class FIISS_KG:
    def __init__(self, input_file, db_name):
        self.input_file = input_file
        self.db_name = db_name

        self.safety_packages = [] # each package represents a feature
        self.security_packages = []

        self.sa_activites = []
        self.se_activities = []

        self.sa_components = []
        self.se_components = []

        self.sa_lifelines    = []
        self.se_lifelines    = []
        self.sa_se_lifelines = []
        self.not_relevant_lifelines = []

        self.message_exchanges = []

        self.interactions = dict() # mapping of each feature to its self.interactions

        self.sa_features_lifelines = dict() # mapping of safety features to their lifelines
        self.se_features_lifelines = dict() # mapping of security features to their lifelines

        self.features_safety_components = dict() # mapping of safety and security features to their components
        self.features_security_components = dict() # mapping of safety and security features to their components
        pass

    def get_values_from_dict(self, FeID_compID_dict):
        components_set = []
        for feature in FeID_compID_dict:
            for component_id in FeID_compID_dict[feature]:
                components_set.append(component_id)
        return components_set

    def has_type(self, node, type):
        node_type = node.get('type')
        return node_type == type

    def add_node_to_array(self, node, arr):
        # avoiding duplicating data in array
        dbug_name = 'not relevant component'
        temp_name = node.get('name')
        if temp_name == dbug_name:
            print(3)
        if not node in arr:
            arr.append(node) # maybe use sets

    def find_all_packages(self):
        query = f"MATCH (n:`{PACKAGE_TYPE}`) return n"
        result = graph.run(query)
        node_array = []
        nodes = result.data()
        for node in nodes:
            node_array.append(node['n'])

        for package in node_array:
            package_type = package.get('package_type')
            package_id = package.get('node_id')
            if package_type == SAFETY_TYPE and package_id not in self.safety_packages:
                self.safety_packages.append(package_id)
                self.sa_features_lifelines[package_id] = []
            elif package_type == SECURITY_TYPE and package_id not in self.security_packages:
                self.security_packages.append(package_id)
                self.se_features_lifelines[package_id] = []
            elif package_type != OTHER_TYPE:
                print("ERROR! Package has no type!")
        return node_array, self.safety_packages, self.security_packages
    
    def analyse_activity(self, activity, components, features_components, sa_se_type):
        node_id = activity.get('node_id') # could be optimised, e.g., to take all necessary nodes in one query
        # query = "MATCH (n:{node_id: '{node_id}'})-[r]-(n) RETURN r, n".format(node_id)
        query = """
        MATCH (n) -[r]-> (m) WHERE n.node_id = $node_id RETURN r, m
        """
        result = graph.run(query, node_id=node_id)
        data = result.data()
        for data_elem in data:
            node = data_elem['m']
            if self.has_type(node, "uml:Component"):
                self.add_node_to_array(node, components)
                feature = node.get('package')
                if not feature in features_components:
                    features_components[feature] = []
                features_components[feature].append(node)
                if sa_se_type == SAFETY_TYPE:
                    if not feature in self.features_safety_components:
                        self.features_safety_components[feature] = []
                    if not node in self.features_safety_components[feature]:
                        self.features_safety_components[feature].append(node)
                elif sa_se_type == SECURITY_TYPE:
                    if not feature in self.features_security_components:
                        self.features_security_components[feature] = []
                    if not node in self.features_security_components[feature]:
                        self.features_security_components[feature].append(node)


    def get_features_security_components(self):
        return self.features_security_components
    
    def get_features_safety_components(self):
        return self.features_safety_components

    def arch_analysis(self):
        # % 1. arch analysis
        # sa se activities - go through graph and take all activites and their packages and check that it's safety or security package 
        # for activites take their components and make a list of relevant components
        self.find_all_packages()
        nodes = self.converter.get_all_nodes()
        for node in nodes:
            if node.get('type') == ACTIVITY_TYPE:
                # print(node.get('name')) 
                package = node.get('package')
                if package in self.safety_packages:
                    self.sa_activites.append(node)
                elif package in self.security_packages:
                    self.se_activities.append(node)
        # now we have lists of safety and security activities
                    
        for activity in self.sa_activites:
            self.analyse_activity(activity, self.sa_components, self.features_safety_components, SAFETY_TYPE)
                    
        for activity in self.se_activities:
            self.analyse_activity(activity, self.se_components, self.features_security_components, SECURITY_TYPE)

        print("Architectural analysis finished")

    def find_node_by_query_and_id(self, query, node_id):
        result = graph.run(query, node_id=node_id)
        return result.data()

    def check_if_lifeline_sa_se(self, component_node, lifeline):
        # if lifeline.get('type') == "uml:InstanceSpecification":
        #     query = "MATCH (n) -[r:REPRESENTS]-> (m) WHERE m.node_id = $node_id RETURN n"
        #     data = self.find_node_by_query_and_id(query, lifeline.get('node_id'))
        #     lifeline = data[0]['n']
        component = component_node.get('node_id')
        safety_relevance = False
        security_relevance = False
        if component in self.se_components:
            security_relevance = True
            self.add_node_to_array(lifeline, self.se_lifelines)
            if component in self.sa_components:
                safety_relevance = True
                self.add_node_to_array(lifeline, self.sa_lifelines)
                self.add_node_to_array(lifeline, self.sa_se_lifelines)
        elif component in self.sa_components:
            safety_relevance = True
            self.add_node_to_array(lifeline, self.sa_lifelines)
        else:
            self.add_node_to_array(lifeline, self.not_relevant_lifelines)

        lifeline['safety_relevance'] = safety_relevance
        lifeline['security_relevance'] = security_relevance
        self.converter.graph.push(lifeline)


    def add_lifeline_to_a_package(self, lifeline, package_id):
        # match lifeline to its package and add it to the dict
        if package_id in self.se_features_lifelines:
                curr_list = self.se_features_lifelines[package_id]
                if not lifeline in curr_list:
                    self.se_features_lifelines[package_id].append(lifeline) # remove duplicating nodes
        elif package_id in self.sa_features_lifelines:
                curr_list = self.sa_features_lifelines[package_id]
                if not lifeline in curr_list:
                    self.sa_features_lifelines[package_id].append(lifeline)

    def find_message_exchanges(self):
        query = """
        MATCH (n) -[r]-> (m) WHERE r:OCC_MESSAGE RETURN n, r, m
        """ # input message type
        result = graph.run(query)
        data = result.data()

        for data_elem in data:
            occ_spec_n = data_elem['n']
            occ_spec_m = data_elem['m']
            relation = data_elem['r']

            n_package = occ_spec_n.get('package')
            m_package = occ_spec_m.get('package')
            
            n_covered = occ_spec_n.get('covered')
            m_covered = occ_spec_m.get('covered')

            lifeline_n = self.converter.find_node_by_id(n_covered)
            lifeline_m = self.converter.find_node_by_id(m_covered)

            self.add_lifeline_to_a_package(lifeline_n, n_package) 
            self.add_lifeline_to_a_package(lifeline_m, m_package)

            if n_package == m_package:
                triple = (lifeline_n, relation, lifeline_m)
                # triple = (occ_spec_n, relation, occ_spec_m)
                self.message_exchanges.append(triple)
        return self.message_exchanges

    
    def get_features_sa_lifelines(self):
        return self.sa_features_lifelines
    
    def get_features_se_lifelines(self):
        return self.se_features_lifelines
    
    def check_node(self, node, feature):
        node_type = node.get('type')
        if node_type == "uml:InstanceSpecification":
            return True
        
        if node_type == "uml:Lifeline":
            ll_package = node.get('package')
            component = self.find_inst_spec_of_a_lifeline(node)
            inst_package = component.get('package')
            if component.get('type') == "uml:InstanceSpecification":
                component = self.find_component_of_inst_spec(component)
            comp_package = component.get('package')
            return ll_package == inst_package #or ll_package == comp_package
        return True
    
    def find_inst_spec_of_a_lifeline(self, lifeline):
        query = """
        MATCH (n) -[r]-> (m) WHERE n.node_id = $node_id and r:REPRESENTS RETURN m
        """
        data_n = self.find_node_by_query_and_id(query, lifeline.get('node_id'))

        for data_elem in data_n:
            instance_n = data_elem['m']
        return instance_n
    
    def find_component_of_inst_spec(self, instance):
        query = """
        MATCH (n) -[r]-> (m) WHERE m.node_id = $node_id and r:CLASSIFIES RETURN n
        """
        result = self.find_node_by_query_and_id(query, instance.get('node_id'))
        component = None

        for data_elem in result:
            component = data_elem['n']
        return component


    def find_relevant_lifelines(self):
        for triple in self.ll_message_exchanges:
            lifeline_n = triple[0]
            lifeline_m = triple[2]

            instance_n = lifeline_n
            instance_m = lifeline_m

            # query to find an instance specification of a lifeline
            query = """
            MATCH (n) -[r]-> (m) WHERE n.node_id = $node_id and r:REPRESENTS RETURN m
            """
            n_type = lifeline_n.get('type')
            if n_type == "uml:Lifeline":
                instance_n = self.find_inst_spec_of_a_lifeline(lifeline_n)
            elif n_type == "uml:InstanceSpecification":
                instance_n = lifeline_n

            m_type = lifeline_m.get('type')
            if m_type == "uml:Lifeline":
                instance_m = self.find_inst_spec_of_a_lifeline(lifeline_m)
            elif m_type == "uml:InstanceSpecification":
                instance_m = lifeline_m

            if instance_n == None:
                print("ERROR! No instance specification for lifeline {} {}".format(lifeline_n.get('node_id'), lifeline_n.get('name')))
                continue

            if instance_m == None:
                print("ERROR! No instance specification for lifeline {} {}".format(lifeline_m.get('node_id'), lifeline_n.get('name')))
                continue
            
            component_n = instance_n
            component_m = instance_m

            if instance_n.get('type') == "uml:InstanceSpecification":
                component_n = self.find_component_of_inst_spec(instance_n)

            if instance_m.get('type') == "uml:InstanceSpecification":
                component_m = self.find_component_of_inst_spec(instance_m)

            # print("Components for lifelines are found")
            
            self.check_if_lifeline_sa_se(component_n, lifeline_n)
            self.check_if_lifeline_sa_se(component_m, lifeline_m)
    

    def behav_analysis(self):
        # % 2. behav analysis

        # % 1) find message exchanges (l1, m, l2) for sf that
        # for all messages check their source and destination and that their packages sf are equal, then form an exchange triple
        # % (or use nodes for that)

        # 2) take message triple, find for each lifeline its classifier - component c and check that c is in the list of sa and not in se components -> lifeline is sa relevant and the same for se
        # % sa-se relevant lifeline - a component c which is SAFETY RELEVANT and the classifier of l is c; and it exists a component c with c being SECURITY RELEVANT and the classifier of l is c

        self.message_exchanges = self.find_message_exchanges()
        print("Message triples are formed")

        self.find_relevant_lifelines()

        print("Behavioral analysis finished")

    def try_to_find_path(self, lifeline1, lifeline2, max_length = -1):
        # checks if there is a path in the directional graph from one lifeline to another
        # we have three ways to solve it: 
        # 1. use message exchanges to build a graph and work with it
        # (we already have a graph, so do we actually need a second one?)
        # 2. or work directly on our graph and find interacton between occurence specifications
        # (okay but we need to add extra code which can lead to errors)
        # 3. rewrite the converter code to avoid occurence specifications and work directly with lifelines 
        # (not good, we will hide some potential nodes, so it's information leakage)

        # so far we stopped at the option 2
        query = """
        MATCH p = (n) -[*]-> (m) WHERE n.covered = $start_value and m.covered = $end_value RETURN p
        """
        if max_length > 0:
            query = f"MATCH p = (n) -[*..{max_length}]-> (m) WHERE n.covered = $start_value and m.covered = $end_value RETURN p"
        # path between occurence spec-s that belong to lifelines
        
        start_value = lifeline1.get('node_id')
        end_value = lifeline2.get('node_id')
        
        result = graph.run(query, start_value=start_value, end_value=end_value)
        return result.data()

    def identify_path(self, feature, p, lifeline1, lifeline2):
        interaction_type = InteractionType.SAF_SEC
        if lifeline1 in self.sa_lifelines:
            if lifeline2 in self.se_lifelines:
                interaction_type = InteractionType.SAF_SEC
                
            elif lifeline2 in self.sa_se_lifelines:
                interaction_type = InteractionType.SAF_SAF_SEC

        elif lifeline1 in self.se_lifelines:
            if lifeline2 in self.sa_lifelines:
                interaction_type = InteractionType.SEC_SAF
                
            elif lifeline2 in self.sa_se_lifelines:
                interaction_type = InteractionType.SEC_SAF_SEC

        elif lifeline1 in self.sa_se_lifelines:
            if lifeline2 in self.sa_lifelines:
                interaction_type = InteractionType.SAF_SEC_SAF
                
            elif lifeline2 in self.se_lifelines:
                interaction_type = InteractionType.SAF_SEC_SEC
        
        if not feature in self.interactions:
            self.interactions[feature] = []
        
        inter_data = (p, interaction_type, lifeline1, lifeline2)
        self.interactions[feature].append(inter_data)

    def find_paths_for_features(self, features_lifelines_dict):
        paths = []
        for feature in features_lifelines_dict:
            curr_feature_lifelines = features_lifelines_dict[feature]  

            for lifeline1 in curr_feature_lifelines:
                if lifeline1 == None:
                    print("lifeline1 is None")
                    continue

                for lifeline2 in curr_feature_lifelines:
                    if lifeline1 == lifeline2:
                        continue # skip messages from a lifeline to itself

                    if lifeline2 == None:
                        print("lifeline2 is None")
                        continue

                    path = self.try_to_find_path(lifeline1, lifeline2, 10)
                    paths.append(path)
                    if len(path) > 0:
                        p = path[0]['p'] # do we need all possible paths?
                        self.identify_path(feature, p, lifeline1, lifeline2)
        return self.interactions, paths
            
    def interaction_analysis(self):
        # % 3. Interaction analysis
        # % 1) for each feature take its lifelines 
        # Then check, is there a path from one to another and the first lifeline is sa, se, or sa-se relevant (6 combinations)
        # % sf specifies an interaction from l1 to l2, if there is a path in the graph

        self.find_paths_for_features(self.sa_features_lifelines)
        self.find_paths_for_features(self.se_features_lifelines)
        print(self.interactions)
        print("Interaction analysis completed")

    def connect_to_db(self):
        self.graph = Graph("bolt://localhost:7687", name=self.db_name, auth=("neo4j", "neo4jneo4j"))
        self.converter = Converter(self.input_file, self.db_name, 'EAPK_511FDC72_60D2_413c_B488_D6CAE1507040', 'EAPK_A4E14F79_C0CB_4e3a_8A7A_ACB1EB7362C4', 'EAPK_F7282E3A_E460_4a55_813A_FA109AA4BB0E')   

    def start(self): 
        self.connect_to_db()
        self.converter.convert()

        self.arch_analysis()
        self.behav_analysis()
        self.interaction_analysis()
        
        print("FIISS analysis completed")

    def get_interaction(self):
        return self.interactions

# fiiss = FIISS_KG("inputfile7.xml", "testdb2")
# fiiss.start()