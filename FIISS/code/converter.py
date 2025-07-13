import lxml.etree as etree
import os
import timeit
import random

from py2neo import Graph, Node, Relationship

ns = {
    'uml':'http://schema.omg.org/spec/UML/2.1',
    'xmi':'http://schema.omg.org/spec/XMI/2.1',
    'SysML':'http://www.omg.org/spec/SysML/20120322/SysML',
    'sysml':'http://www.omg.org/spec/SysML/20080501/SysML-profile'
    }
        
# 1. array of node types and relationships types
# 2. dict of each xml type to graph type (uml:Package -> package)
# 3. iter for safety features:
# 4. for each node save id, type, name (as node name) + supplier and client for edges + additional parameters
# 5. same (3, 4) for security features
# 6. if it's a package, don't add it directly to a diagram, it can't be connected to anything as 
# an element, but add this property to it's children  
        
# "uml:Package", "uml:Lifeline", "uml:OccurrenceSpecification", "uml:Interaction"
nodes_types = []
edges_types = ["uml:Message", "uml:Realization"]

diagram_ids = ["EAPK_B5DA57A0_AB69_6786_B972_3F19CB76FF40"]

CURR_PACKAGE = ""
NODE_NAME = "name"
NODE_TYPE = "type"
NODE_PACKAGE = "package"
NODE_PARENT_PACKAGE = "parent_package"

REALIZATION      = Relationship.type("REALIZATION")
OCC_MESSAGE      = Relationship.type("OCC_MESSAGE")
MESSAGE          = Relationship.type("MESSAGE")
CONTROL_FLOW     = Relationship.type("CONTROL_FLOW")
IS_CLASSIFIER    = Relationship.type("CLASSIFIES")
REPRESENTS       = Relationship.type("REPRESENTS")
OCCURENCE        = Relationship.type("OCCURENCE_SPECIFICATION")
BEHAVIOR_OF      = Relationship.type("BEHAVIOR_OF")
SEQUENCE_MESSAGE = Relationship.type("SEQUENCE_MESSAGE")

SAFETY_TYPE   = "SAFETY"
SECURITY_TYPE = "SECURITY"
OTHER_TYPE    = "OTHER"

class Converter:
    def __init__(self, file_name, db_name, safety_root_id, security_root_id, other_root_id):
        self.file_name = file_name
        self.db_name = db_name
        self.safety_root_id = safety_root_id
        self.security_root_id = security_root_id
        self.other_root_id = other_root_id
        self.connect_to_graph()
        pass

    def node_exists(self, node_id):
        query = "MATCH (n) WHERE n.node_id = $node_id RETURN n"
        result = self.graph.run(query, node_id=node_id)
        length = len(result.data())
        return length > 0

    def find_node_by_id(self, node_id):
            query = "MATCH (n) WHERE n.node_id = $node_id RETURN n"
            result = self.graph.run(query, node_id=node_id)

            # assume that the graph contains the node
            data = result.data()
            temp_node = None
            for node in data:
                temp_node = node['n']
            return temp_node

    def push_or_create(self, node, node_id):
        if self.node_exists(node_id):
            self.graph.push(node)
        else:
            self.graph.create(node)

    def find_or_create_node(self, node_id, name="None", type="None"):
        # tries to find a node by id, and, if it is not in the graph, creates it
        node = None
        if self.node_exists(node_id):
            node = self.find_node_by_id(node_id)
            
        if node == None:
            # print("Node with id {} is not in the graph".format(node_id))
            node = Node(type)
        
        if not NODE_NAME in node or (node[NODE_NAME] == "None" and name != None and name != "None"):
            # a node can be created as a source or target for edge and may not have these attributes initially
            # so we add them here when we actually parse the node
            node[NODE_NAME] = name
        
        if not NODE_TYPE in node or (node[NODE_TYPE] == "None" and type != None and name != "None"):
            node[NODE_TYPE] = type

        node.add_label(type)
        node["node_id"] = node_id
        
        return node

    def find_and_create_edge(self, source, target, id, type, edge_curr_package):
        # creates an edge by source and target: if source and target are not in the graph, creates them
        source_node = self.find_or_create_node(source)
        self.push_or_create(source_node, source)
        # print(source_node[type])

        target_node = self.find_or_create_node(target)
        self.push_or_create(target_node, target)

        if type == "uml:Realization":
            edge = REALIZATION(source_node, target_node, type=type, node_id=id, package=edge_curr_package)
        elif type == "uml:Message":
            edge = OCC_MESSAGE(source_node, target_node, type=type, node_id=id, package=edge_curr_package)
        elif type == "uml:ControlFlow":
            edge = CONTROL_FLOW(source_node, target_node, type=type, node_id=id, package=edge_curr_package)
        else:
            edge = Relationship(source_node, target_node, type=type, node_id=id, package=edge_curr_package)
        return edge


    def add_edge(self, edge_info):
        element = edge_info[0]
        edge_curr_package = edge_info[1]
        edge_package_type = edge_info[2]
        type = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}type')
        name = element.attrib.get('name')
        id = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}id')
        if self.try_to_parse_activity_diagram_element(element, edge_curr_package, edge_package_type):
            return
        
        if type == "uml:Realization":
            supplier = element.attrib.get('supplier')
            client = element.attrib.get('client')

            edge = self.find_and_create_edge(supplier, client, id, type, edge_curr_package)
            self.push_or_create(edge, id)

        elif type == "uml:Message":
            sendEvent = element.attrib.get('sendEvent')
            receiveEvent = element.attrib.get('receiveEvent')
            messageKind = element.attrib.get('messageKind')
            messageSort = element.attrib.get('messageSort')

            edge = self.find_and_create_edge(sendEvent, receiveEvent, id, type, edge_curr_package)
            edge['messageSort'] = messageSort
            edge['messageKind'] = messageKind
            edge['name'] = name

            diagram_id = ""
            diagram_node = self.find_ancestor_of_type(element, "uml:Interaction")
            if diagram_node != None:
                diagram_id = diagram_node.attrib.get('{http://schema.omg.org/spec/XMI/2.1}id')

            edge['diagram_id'] = diagram_id

            self.push_or_create(edge, id)

    def has_ancestor(self, element, diagram_id):
        # if the element has an ancestor with a specific id
        parents = element.xpath("ancestor::*[@xmi:id='{}']".format(diagram_id), namespaces=ns)
        return len(parents) > 0
    
    def find_ancestor_of_type(self, element, type):
        # if the element has an ancestor with a specific id
        parents = element.xpath("ancestor::*[@xmi:type='{}']".format(type), namespaces=ns)
        if len(parents) > 0:
            return parents[0]
        return None

    def is_diagram_element(self, element):
        # check elements's ancestors if one of them belongs to a diagram
        for diagram_id in diagram_ids:
            if self.has_ancestor(element, diagram_id):
                return True
        return False

    def check_and_add_property(self, element, node, property_name):
        property = element.get(property_name)
        if property != None:
            node[property_name] = property


    def add_node(self, node_info):
        # parse element into a node and then add it to graph, then push
        element = node_info[0]
        node_curr_package = node_info[1]
        node_package_type = node_info[2]
        type = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}type')
        name = element.get('name')
        id = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}id')

        if self.try_to_parse_activity_diagram_element(element, node_curr_package, node_package_type):
            return

        if element.tag == 'ownedAttribute':
            types = element.findall('type')
            if len(types):
                idref = types[0].attrib.get('{http://schema.omg.org/spec/XMI/2.1}idref')
                if idref:
                    node = self.find_or_create_node(id, "ownedAttribute", type)
                    node["idref"] = idref
                    self.push_or_create(node, id)
            return
        
        node = self.find_or_create_node(id, name, type)

        self.check_and_add_property(element, node, "classifier")
        self.check_and_add_property(element, node, "represents")
        self.check_and_add_property(element, node, "covered")
        
        if type == "uml:Package":
            node["package_type"] = node_package_type
            # node["package_type"] = PACKAGE_TYPE

        if not NODE_PACKAGE in node or (node[NODE_PACKAGE] == "None" and node_curr_package != "None"):
            node[NODE_PACKAGE] = node_curr_package
            # node[NODE_PACKAGE] = CURR_PACKAGE

        self.push_or_create(node, id)


    def get_root_element(self, root_path):
        element_iter = self.root.iterfind(path=root_path, namespaces=ns)
        root_element = None
        for element in element_iter:
            root_element = element # we have the root element now
        return root_element

    def find_child_with_tag(self, parent_node, tag):
        # find an element's first child with a specific tag
        first_child = parent_node.xpath("//{}".format(tag))[0]
        if first_child == None:
            print("No children found!")
        return first_child

    def try_to_parse_activity_diagram_element(self, element, curr_package, package_type):
        if element.tag == "node":
            # save to nodes the nodes from the initial diagram with id, type and, if there is a behavior, 
            # idref of activity implemented. other properties can be expressed by edges elements
            type = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}type')
            name = element.get('name')
            id = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}id')

            node = self.find_or_create_node(id, name, type)
            behavior = self.find_child_with_tag(element, "behavior")
            node['package'] = curr_package
            if behavior != None:
                idref = behavior.attrib.get('{http://schema.omg.org/spec/XMI/2.1}idref')
                node["idref"] = idref

            self.push_or_create(node, id)

        elif element.tag == "edge":
            type = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}type')
            id = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}id')
            source = element.get('source')
            target = element.get('target')

            edge = self.find_and_create_edge(source, target, id, type, curr_package)
            self.graph.create(edge)
        else:
            return False

        # add connections between uml:CallBehaviorAction and their activities
        nodes = self.get_all_nodes()
        for behav_node in nodes:
            idref = behav_node.get('idref')
            type = behav_node.get('type')
            if type == "uml:CallBehaviorAction" and idref != None:
                activity = self.find_node_by_id(idref)
                if activity != None:
                    edge = BEHAVIOR_OF(behav_node, activity)
                    self.graph.create(edge)
        return True

    def get_all_nodes(self):
        query = "MATCH (n) return n"
        result = self.graph.run(query)
        node_array = []
        nodes = result.data()
        for node in nodes:
            node_array.append(node['n'])
        return node_array

    def get_node_from_query(self, result):
        instance = None
        for node in result.data():
            instance = node['n']
        return instance

    def add_classifier_edges(self):
        # add edges between uml:Lifeline and ownedAttribute idref (uml:InstanceSpecification)
        # and then between uml:InstanceSpecification and its classifier (uml:Component)
        nodes = self.get_all_nodes()
        for represents_node in nodes:
            represents = represents_node.get('represents')
            if represents != None:
                query = "match (n) where n.name = 'ownedAttribute' and n.node_id = $node_id return n"
                result = self.graph.run(query, node_id=represents)
                ownedAttribute = self.get_node_from_query(result)

                instance = None
                # now we need to find a classifier by idref
                if ownedAttribute != None:
                    idref = ownedAttribute.get('idref')
                    instance = self.find_node_by_id(idref)

                if instance != None:
                    edge = REPRESENTS(represents_node, instance)
                    self.graph.create(edge)

                    classifier = instance.get('classifier')
                    comp_node = self.find_node_by_id(classifier)
                    if comp_node != None:
                        edge = IS_CLASSIFIER(comp_node, instance)

                    self.graph.create(edge)

    def add_occurence_spec_edges(self):
        # add connections between uml:OccurrenceSpecification and their uml:Lifeline
        nodes = self.get_all_nodes()
        for occ_node in nodes:
            covered = occ_node.get('covered')
            if covered != None:
                instance = self.find_node_by_id(covered)
                if instance != None:
                    edge = OCCURENCE(occ_node, instance)
                    self.graph.create(edge)

    def create_message(self, node_n, node_m, r_package, diagram_id, occ_message_id):
        if node_n == node_m:
            return # ignore building messages where src and dst is the same
        
        msg_time = random.randint(1, 10)
    
        query = """
            MERGE (t1 {node_id: $node_n})
            MERGE (t2 {node_id: $node_m})
            CREATE (t1)-[r:MESSAGE]->(t2) set r.package =$r_package, r.diagram_id=$diagram_id, r.occ_message_id=$occ_message_id, r.msg_time=$msg_time
        """
        self.graph.run(query, node_n=node_n, node_m=node_m, r_package=r_package, diagram_id=diagram_id, occ_message_id=occ_message_id, msg_time=msg_time)
        # self.graph.run(query, node_n=node_n, node_m=node_m, r_package=r_package_int, diagram_id=diagram_id)

    def update_lifeline_package(self, element):
        if element.get('type') == "uml:Lifeline":
            parent_node = self.find_node_by_id(element.get('represents'))
            component = self.find_node_by_id(parent_node.get('idref'))
            if component.get('type') == "uml:InstanceSpecification":
                component = self.find_node_by_id(component.get('classifier'))
            element[NODE_PARENT_PACKAGE] = component.get('package')
            self.graph.push(element)
            return element
        
    def get_real_lifeline_from_IS(self, element):
        instance_id = element.get('node_id')
        query = "MATCH (n) -[r]-> (m) WHERE r:REPRESENTS and m.node_id=$node_id RETURN n, m"
        result = self.graph.run(query, node_id=instance_id)
        data = result.data()
        temp_node = None
        for node in data:
            temp_node = node['n']
        return temp_node

    def add_lifelines_messages(self):
        # The idea is to add extra relationships between lifelines based on the occurence specifications. 
        # It will save the initial structure and make the search easier
        query = """
        MATCH (n) -[r]-> (m) WHERE r:OCC_MESSAGE RETURN n, r, m
        """
        result = self.graph.run(query)
        data = result.data()
        for info in data:
            n_node = info['n']
            m_node = info['m']
            r_edge = info['r']

            n_lifeline = self.find_node_by_id(n_node.get('covered'))
            m_lifeline = self.find_node_by_id(m_node.get('covered'))

            if n_lifeline.get('type') == "uml:Lifeline":
                n_lifeline = self.update_lifeline_package(n_lifeline)
                
            if m_lifeline.get('type') == "uml:Lifeline":
                m_lifeline = self.update_lifeline_package(m_lifeline)

            if n_lifeline.get('type') == "uml:InstanceSpecification":
                n_lifeline = self.get_real_lifeline_from_IS(n_lifeline)

            if m_lifeline.get('type') == "uml:InstanceSpecification":
                m_lifeline = self.get_real_lifeline_from_IS(m_lifeline)

                
            self.create_message(n_lifeline.get('node_id'), m_lifeline.get('node_id'), n_node.get('package'), r_edge.get('diagram_id'), r_edge.get('node_id'))

    def add_sequences_to_graph(self):
        seq_sourcepath_search = ".//Sequence"
        iterator = self.root.iterfind(path=seq_sourcepath_search, namespaces=ns)
        for element in iterator:
            start = element.get('start')
            end = element.get('end')
            node_start = self.find_node_by_id(start)
            node_end = self.find_node_by_id(end)
            edge = SEQUENCE_MESSAGE(node_start, node_end)
            self.graph.create(edge)

    def set_package(self, element):
        id = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}id')
        global CURR_PACKAGE
        CURR_PACKAGE = id

    def set_package_type(self, type):
        global PACKAGE_TYPE
        PACKAGE_TYPE = type
            
    def extract_ancestors(self, path, root_package_type):
        # Find all ancestors of the root and add them to the graph
        temp_root = self.get_root_element(path)

        for element in temp_root.iter():
            type = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}type')
            # if type == None:
            #     print("Error: element has no type!")
            #     continue

            if type == "uml:Package":
                self.set_package(element) # print("Element {} is a package, add it to its children".format())
                self.set_package_type(root_package_type)
                # continue # don't skip a package, we will need it for analysis

            if type in edges_types:
                self.edges.append((element, CURR_PACKAGE, PACKAGE_TYPE))
            else:
                self.nodes.append((element, CURR_PACKAGE, PACKAGE_TYPE))

    def add_nodes_edges_to_graph(self):
        for node_info in self.valid_nodes:
            self.add_node(node_info)
        for edge_info in self.valid_edges:
            self.add_edge(edge_info)

    def connect_to_graph(self):
        # Create a graph object
        self.graph = Graph("bolt://localhost:7687", name=self.db_name, auth=("neo4j", "neo4jneo4j"))

    def check_property_and_add_node(self, node_info, element, property_name):
        element_property = element.get(property_name)
        if element_property != None:
            self.valid_nodes.append(node_info)

    def clear_dataset(self):
        # Clearing the dataset, e.g., removing non-valid or duplicating nodes or relationships
        self.valid_nodes = []
        self.valid_edges = []
        for node_info in self.nodes:
            element = node_info[0]
            id = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}id')
            type = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}type')
            if type == None or id == None:
                continue
            if type == "uml:Lifeline":
                self.check_property_and_add_node(node_info, element, 'represents')
            elif type == "uml:InstanceSpecification":
                self.check_property_and_add_node(node_info, element, 'classifier')
            elif type == "uml:OccurrenceSpecification":
                self.check_property_and_add_node(node_info, element, 'covered')
            else:
                self.valid_nodes.append(node_info)
        for edge_info in self.edges:
            element = edge_info[0]
            id = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}id')
            type = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}type')
            if type == None or id == None:
                continue
            if type == "uml:Message":
                sendEvent = element.get('sendEvent')
                receiveEvent = element.get('receiveEvent')
                messageKind = element.attrib.get('messageKind')
                messageSort = element.attrib.get('messageSort')
                if sendEvent != None and receiveEvent != None and messageKind != None and messageSort != None:
                    self.valid_edges.append(edge_info)
            elif type == "uml:Realization":
                supplier = element.attrib.get('supplier')
                client = element.attrib.get('client')
                if supplier != None and client != None:
                    self.valid_edges.append(edge_info)
            else:
                self.valid_edges.append(edge_info)


    def convert(self):
        start = timeit.default_timer()

        dirname = os.path.dirname(__file__)
        #Relative path of input xml files to be parsed
        file_path_inputfile = os.path.join(dirname, '..', 'data', self.file_name)

        tree = etree.parse(file_path_inputfile)
        self.root = tree.getroot()

        # we leave elements of type uml:Collaboration and uml:Interaction as separate nodes (not sure we need them for analysis)
        ecu_safety_main_pkg_path = ".//packagedElement[@xmi:id='{}']".format(self.safety_root_id) # safety root id
        ecu_security_main_pkg_path = ".//packagedElement[@xmi:id='{}']".format(self.security_root_id) # security root id
        ecu_other_main_pkg_path = ".//packagedElement[@xmi:id='{}']".format(self.other_root_id) # other elements root id

        self.nodes = []
        self.edges = []

        self.extract_ancestors(ecu_safety_main_pkg_path, SAFETY_TYPE)
        self.extract_ancestors(ecu_security_main_pkg_path, SECURITY_TYPE)
        self.extract_ancestors(ecu_other_main_pkg_path, OTHER_TYPE)

        self.clear_dataset()
        self.add_nodes_edges_to_graph()

        self.add_classifier_edges()
        self.add_occurence_spec_edges()
        self.add_lifelines_messages()
        # self.add_sequences_to_graph()

        stop = timeit.default_timer()
        print('Conversion completed in time: ', stop - start)

# converter = Converter("inputfile6.xml", "testdb2", 'EAPK_511FDC72_60D2_413c_B488_D6CAE1507040', 'EAPK_A4E14F79_C0CB_4e3a_8A7A_ACB1EB7362C4')
# converter.convert()