import sys, os
import timeit

from tabulate import tabulate
from py2neo import Graph, Node, Relationship

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-3]))

from FIISS.code.converter import Converter

INPUTFILE_1 = "inputfile1.xml"
TESTDB_1 = "testdb"

# big case - ~25 security features and 50 safety features
INPUTFILE_2 = "inputfile2.xml"
TESTDB_2 = "testdb2"

REALIZATION      = Relationship.type("REALIZATION")
OCC_MESSAGE      = Relationship.type("OCC_MESSAGE")
MESSAGE          = Relationship.type("MESSAGE")
CONTROL_FLOW     = Relationship.type("CONTROL_FLOW")
IS_CLASSIFIER    = Relationship.type("CLASSIFIES")
REPRESENTS       = Relationship.type("REPRESENTS")
OCCURENCE        = Relationship.type("OCCURENCE_SPECIFICATION")
BEHAVIOR_OF      = Relationship.type("BEHAVIOR_OF")
SEQUENCE_MESSAGE = Relationship.type("SEQUENCE_MESSAGE")

SEARCH_DEPTH = 2 # in this case, at both sides from source and destination 

sa_nodes = []
se_nodes = []

def print_paths(paths):
    table = [['path', 'path_length']]
    for path in paths:
        all_nodes = path['all_nodes']
        all_nodes_list = ""
        for node in all_nodes:
            all_nodes_list = all_nodes_list + " -> " + node.get('name')

        path_length = len(all_nodes) - 1
        row = [all_nodes_list, path_length] # p = path[0], lifeline1 = path[1], lifeline2 = path[2]
        table.append(row)

    print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))

def print_complex_paths(paths):
    table = [['path', 'path_length']]
    for path in paths:
        all_nodes = path.nodes
        all_nodes_list = ""
        for node in all_nodes:
            all_nodes_list = all_nodes_list + " -> " + node.get('name')

        path_length = len(all_nodes) - 1
        row = [all_nodes_list, path_length] # p = path[0], lifeline1 = path[1], lifeline2 = path[2]
        table.append(row)
    with open('table_possible_paths.txt', 'w', encoding="utf-8") as f:
            f.write(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))

    print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))

def check_path_relevance(path, relevant_array, irrelevant_array, is_reversed = False):
    all_nodes = path['all_nodes']
    last_node_idx = 0 if is_reversed else len(all_nodes) - 1

    if not all_nodes[last_node_idx] in relevant_array:
        return False # skip paths with the last irrelevant node

    if is_reversed:
        all_nodes = reversed(all_nodes) # for paths to src we check the relevance from end to start
    
    for node in all_nodes:
        if node in relevant_array:
            return True
        elif node in irrelevant_array:
            return False # skip path if it has the same relevance

    return False

def get_relevance_arrays(node):
    if node in se_nodes:
        return sa_nodes, se_nodes
    elif node in sa_nodes:
        return se_nodes, sa_nodes

def check_edge(node_src, node_dst, edge):
    if (node_src in sa_nodes and node_dst in sa_nodes) or (node_src in se_nodes and node_dst in se_nodes):
        print("Path is not relevant, both nodes have the same relevance")

    elif (node_src in sa_nodes and node_dst in se_nodes) or (node_src in se_nodes and node_dst in sa_nodes):
        print(f"Path {edge} is potentially relevant")

    else:
        print("Src node and/or dst node is not relevant, so check for extra paths")

        # three cases are possible: 
        # 1. src node is relevant, dst node is not, so search for paths from dst node to potentially relevant nodes
        # 2. dst node is relevant, src node is not, so search for paths to src node from potentially relevant nodes
        # 3. both nodes are not relevant, so search for paths from and to and print all possible combinations
        src_id = node_src.get('node_id')
        dst_id = node_dst.get('node_id')

        edge_id = edge.get('node_id')
        query = "MATCH p = (a)-[r]->(b) where r.node_id=$edge_id return p"
        result = graph.run(query, edge_id=edge_id)
        data = result.data()

        target_path = data[0]['p']

        # can be optimised, do not need to search to_src paths if src is relevant and vice versa
        query_to_src = f"MATCH p=(n) - [:MESSAGE*1..{SEARCH_DEPTH}] -> (m) WHERE m.node_id='{src_id}' return p, nodes(p) as all_nodes"
        result_to_src = graph.run(query_to_src)
        paths_to_src = result_to_src.data()

        query_from_dst = f"MATCH p=(n) - [:MESSAGE*1..{SEARCH_DEPTH}] -> (m) WHERE n.node_id='{dst_id}' return p, nodes(p) as all_nodes"
        result_from_dst = graph.run(query_from_dst)
        paths_from_dst = result_from_dst.data()

        possbile_relevant_paths = []
        relevant_array = []
        irrelevant_array = [] # if the node has the same relevant as src node, it is not interesting to us
        # case 1
        if node_src in se_nodes or node_src in sa_nodes:
            print("We have case 1")
            relevant_array, irrelevant_array = get_relevance_arrays(node_src)

            for path in paths_from_dst:
                if check_path_relevance(path, relevant_array, irrelevant_array):
                    path_to_append = target_path + path['p']
                    possbile_relevant_paths.append(path_to_append)
            
            print_complex_paths(possbile_relevant_paths)
            return possbile_relevant_paths
        
        # case 2
        if node_dst in se_nodes or node_dst in sa_nodes:
            print("We have case 2")
            relevant_array, irrelevant_array = get_relevance_arrays(node_dst)

            for path in paths_to_src:
                if check_path_relevance(path, relevant_array, irrelevant_array, True):
                    path_to_append = path['p'] + target_path
                    possbile_relevant_paths.append(path_to_append)
            
            print_complex_paths(possbile_relevant_paths)
            return possbile_relevant_paths


        # case 3
        print("We have case 3")
        relevant_array = sa_nodes
        irrelevant_array = se_nodes

        relevant_paths_to_src = []
        relevant_path_from_dst = []
        for path in paths_from_dst:
            if check_path_relevance(path, relevant_array, irrelevant_array):
                relevant_path_from_dst.append(path)

        for path in paths_to_src:
            if check_path_relevance(path, irrelevant_array, relevant_array, True): # relevance of src node should be different from target
                relevant_paths_to_src.append(path)

        for to_src_path in relevant_paths_to_src:
            for from_dst_path in relevant_path_from_dst:
                res_path = to_src_path['p'] + target_path + from_dst_path['p']
                possbile_relevant_paths.append(res_path)

        print("Possible paths count from security to safety, to source node: ", len(relevant_paths_to_src), " from destination node: ", len(relevant_path_from_dst))
        
        relevant_array = se_nodes
        irrelevant_array = sa_nodes
        relevant_paths_to_src = []
        relevant_path_from_dst = []

        for path in paths_from_dst:
            if check_path_relevance(path, relevant_array, irrelevant_array):
                relevant_path_from_dst.append(path)

        for path in reversed(paths_to_src):
            if check_path_relevance(path, irrelevant_array, relevant_array):
                relevant_paths_to_src.append(path)

        for to_src_path in relevant_paths_to_src:
            for from_dst_path in relevant_path_from_dst:
                res_path = to_src_path['p'] + target_path + from_dst_path['p']
                possbile_relevant_paths.append(res_path)

        print("Possible paths count from safety to security, to source node: ", len(relevant_paths_to_src), " from destination node: ", len(relevant_path_from_dst))

        print_complex_paths(possbile_relevant_paths)
        return possbile_relevant_paths
    

def add_edge_and_check(src_id, dst_id, properties, edge_id):
    node_src = converter.find_node_by_id(src_id)
    node_dst = converter.find_node_by_id(dst_id)

    if node_src == None or node_dst == None:
        print("Error! Nodes are not valid!")
        return

    edge = MESSAGE(node_src, node_dst)

    for prop_map in properties:
        edge[prop_map] = properties[prop_map]

    edge["node_id"] = edge_id
    edge["occ_message_id"] = edge_id
    converter.push_or_create(edge, edge_id)

    print("Edge added!")
    return check_edge(node_src, node_dst, edge)


def get_relevant_nodes(relevant_type):
    query = "MATCH (n) where n.type=$relevant_type return n"
    result = graph.run(query, relevant_type=relevant_type)
    data = result.data()
    for info in data:
        node = info['n']
        safety_relevance = node.get('safety_relevance')
        security_relevance = node.get('security_relevance')

        name = node.get('name')
        if safety_relevance or 'fwLoader' in name:
            sa_nodes.append(node)
        
        if security_relevance:
            se_nodes.append(node)

def remove_edge(edge_id):
    query = "MATCH (n) -[r] -> (m) where r.node_id=$node_id detach delete r"
    graph.run(query, node_id=edge_id)

graph = Graph("bolt://localhost:7687", name=TESTDB_2, auth=("neo4j", "neo4jneo4j"))
converter = Converter(INPUTFILE_2, TESTDB_2, 'EAPK_511FDC72_60D2_413c_B488_D6CAE1507040', 'EAPK_A4E14F79_C0CB_4e3a_8A7A_ACB1EB7362C4', 'EAPK_F7282E3A_E460_4a55_813A_FA109AA4BB0E')
relevant_type = "uml:Lifeline"

get_relevant_nodes(relevant_type)

properties = dict()
properties["type"] = "uml:Message"

# define safety and security relevances

# remove_edge("test_edge_6")

# add_edge_and_check("EAID_LL000000_B3FF_CE1D_B92E_A1DF8B0B6F44", "EAID_LL000000_C6A3_255C_BDE0_75EE3D1C4643", properties, "test_edge_1") # both nodes are differently relevant, path is relevant

# add_edge_and_check("EAID_LL000000_8428_2537_B384_4BBA3FFBDAF8", "EAID_LL000000_8428_2537_A707_0E0E158ED807", properties, "test_edge_2") # the nodes are similarly relevant, path is not relevant

add_edge_and_check("EAID_LL000000_E003_58A4_8068_F099064ECE90", "EAID_LL000000_C529_2261_9D7A_26602389077F", properties, "test_edge_3") # the src node is security relevant, check paths from dst node
# # fwVerifier 9 -> NRF5 sequence 7 

# add_edge_and_check("EAID_LL000000_C529_2261_9EE5_80E0F26CB05A", "EAID_LL000000_8B0B_6F44_B346_2E1B84DB0ED0", properties, "test_edge_4") # the dst node is safety relevant, check paths to src node

# add_edge_and_check("EAID_LL000000_C529_2261_9D7A_26602389077F", "EAID_LL000000_51AE_48b9_A133_10D9C5292261", properties, "test_edge_5") # both nodes are not relevant
# paths = add_edge_and_check("EAID_LL000000_8B0B_6F44_8B23_68C4884F0298", "EAID_LL000000_C529_2261_9EE5_80E0F26CB05A", properties, "test_edge_6") # both nodes are not relevant