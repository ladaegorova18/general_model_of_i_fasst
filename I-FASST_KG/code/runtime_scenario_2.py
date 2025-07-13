import sys, os
import timeit

from tabulate import tabulate
from py2neo import Graph

from I_FASST_for_KG import I_FASST_KG

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-3]))

from FIISS.code.converter import Converter
from FIISS.code.FIISS_for_KG import FIISS_KG

LIFELINE_TYPE = "uml:Lifeline"
SEARCH_DEPTH = 2

INPUTFILE_1 = "inputfile1.xml"
TESTDB_1 = "testdb"

# big case - ~25 security features and 50 safety features
INPUTFILE_2 = "inputfile2.xml"
TESTDB_2 = "testdb2"

def check_timings(path, messages_dict):
    prev_msg_time = -1
    for path_step in path:
        message_id = path_step[2]
        message = messages_dict[message_id]
        
        msg_time = message.get('msg_time')
        if msg_time <= prev_msg_time:
            return False
        prev_msg_time = msg_time
    return True

def check_relevance(path, pp_1, pp_2, messages_dict):
    prev_message_package = ""
    prev_msg_time = -1
    for path_step in path:
        message_id = path_step[2]
        message = messages_dict[message_id]
        message_package = message.get('package')
        
        msg_time = message.get('msg_time')
        if msg_time <= prev_msg_time:
            return False
        prev_msg_time = msg_time

        if prev_message_package == "":
            prev_message_package = message_package 

        if prev_message_package != message_package:
            return False
        
        nodes = message.nodes
        lifeline_1 = nodes[0]
        lifeline_2 = nodes[1]

        package_1 = lifeline_1.get('package')
        package_2 = lifeline_2.get('package')
        
        if package_1 != pp_1 and package_1 != pp_2 and lifeline_1 not in not_relevant_lifelines:
            return False
        if package_2 != pp_1 and package_2 != pp_2 and lifeline_2 not in not_relevant_lifelines:
            return False

    return True


def extract_all_nodes_from_path(path, edges = None):
    all_nodes = []
    if edges == None:
        edges = path[0]
    for edge in edges:
        node_src = edge[0]
        node_dst = edge[1]
        is_duplicating = False
        if len(all_nodes) > 0 and all_nodes[len(all_nodes) - 1] == node_src:
            is_duplicating = True
        if not is_duplicating:
            all_nodes.append(node_src)
        all_nodes.append(node_dst)

    return all_nodes


def form_queries(relevance_array, queries):
    for lifeline1 in relevance_array:
        for lifeline2 in not_relevant_lifelines:
            query = (lifeline1, lifeline2)
            if not query in queries:
                queries.append(query)

            query = (lifeline2, lifeline1)
            if not query in queries:
                queries.append(query)
    return queries


def find_paths_for_lifeline(lifeline1, lifeline2, path_info, search_path_method):
    paths_temp = []
    if lifeline1 in not_relevant_lifelines:
        if lifeline2 in se_lifelines:
            paths_temp = search_path_method(lifeline1, SEARCH_DEPTH, [], path_info[0], sa_lifelines)
        elif lifeline2 in sa_lifelines:
            paths_temp = search_path_method(lifeline1, SEARCH_DEPTH, [], path_info[0], se_lifelines)
        else:
            paths_se = search_path_method(lifeline1, SEARCH_DEPTH, [], path_info[0], sa_lifelines)
            paths_sa = search_path_method(lifeline1, SEARCH_DEPTH, [], path_info[0], se_lifelines)
            paths_temp = paths_se + paths_sa
    return paths_temp


def find_src_paths_to_lifeline(lifeline, search_depth, total_paths, target_path, relevant_array):
    if search_depth == 0:
        return total_paths
    if not lifeline in end_nodes_to_paths:
        return []
    paths = end_nodes_to_paths[lifeline]
    for path in paths:
        all_nodes = extract_all_nodes_from_path(path)
        first_node = all_nodes[0]
        if path[1] in not_relevant_lifelines: # should continue path to src
            continued_paths = find_src_paths_to_lifeline(path[1], search_depth - 1, [], path[0] + target_path, relevant_array)
            if len(continued_paths) > 0:
                total_paths.extend(continued_paths) # adds a list to a list

        if first_node in relevant_array:
            total_paths.append(path[0] + target_path)
        continue
    return total_paths


def find_dst_paths_from_lifeline(lifeline, search_depth, total_paths, target_path, relevant_array):
    if search_depth == 0:
        return total_paths
    if not lifeline in start_nodes_to_paths:
        return []
    paths = start_nodes_to_paths[lifeline]
    for path in paths:
        all_nodes = extract_all_nodes_from_path(path)
        last_node = all_nodes[len(all_nodes) - 1]
        if path[2] in not_relevant_lifelines: # should continue path from dst
            continued_paths = find_dst_paths_from_lifeline(path[2], search_depth - 1, [], target_path + path[0], relevant_array)
            if len(continued_paths) > 0:
                total_paths.extend(continued_paths)

        if last_node in relevant_array:
            total_paths.append(target_path + path[0])
        continue
    return total_paths


def print_paths(filtered_paths):
    table = [['path', 'lifeline 1', 'lifeline 2', 'path_length']]
    for path in filtered_paths:
        all_nodes = extract_all_nodes_from_path(path, path)
        all_nodes_list = ""
        for node in all_nodes:
            all_nodes_list = all_nodes_list + " -> " + node.get('name')

        path_length = len(all_nodes) - 1
        row = [all_nodes_list, all_nodes[0].get('node_id'), all_nodes[path_length].get('node_id'), path_length] # p = path[0], lifeline1 = path[1], lifeline2 = path[2]
        table.append(row)

    print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))
    print("Total amount of possible paths between diagrams {}".format((len(table) - 1)))

    with open('table_scenario_2.txt', 'w', encoding="utf-8") as f:
        f.write(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))

# We search for paths in different diagrams;
# The path starts or/and ends with not relevant lifeline;
# We take a look on another diagrams and search for possible paths in them where the src lifeline is equal to dst lifeline;
# As we are working with graphs, we can take the relationship property diagram_id to define the diagram of interaction;
# In runtime there are also timings that may be another constraint

start_time = timeit.default_timer()

i_fasst = I_FASST_KG(INPUTFILE_1, TESTDB_1)
i_fasst.connect_to_db()

i_fasst.arch_element_analysis()

se_lifelines = i_fasst.se_lifelines
sa_lifelines = i_fasst.sa_lifelines
not_relevant_lifelines = i_fasst.not_relevant_lifelines

queries = form_queries(sa_lifelines, [])
queries = form_queries(se_lifelines, queries)

for src in not_relevant_lifelines:
    for dst in not_relevant_lifelines:
        if src != dst:
            queries.append((src, dst))

print("Total queries: ", len(queries))

paths = i_fasst.find_paths_using_network_X(queries)
print("Total paths with not relevant src or/and dst: ", len(paths))

filtered_paths, feature_interactions = i_fasst.interaction_path_processing(check_relevance, paths)

print(len(filtered_paths))

# we have a set of paths where src or/and dst nodes are not relevant
# we can form possible relevant paths from them if there is another path that ends with the same node where the path starts and vice versa

start_nodes_to_paths = dict()
end_nodes_to_paths = dict()

for path_info in filtered_paths:
    lifeline1 = path_info[1]
    lifeline2 = path_info[2] 

    if lifeline1 in not_relevant_lifelines:
        if not lifeline1 in start_nodes_to_paths:
            start_nodes_to_paths[lifeline1] = []

        start_nodes_to_paths[lifeline1].append(path_info)

    if lifeline2 in not_relevant_lifelines:
        if not lifeline2 in end_nodes_to_paths:
            end_nodes_to_paths[lifeline2] = []

        end_nodes_to_paths[lifeline2].append(path_info)

print("start nodes to paths ", len(start_nodes_to_paths))
print("end nodes to paths ", len(end_nodes_to_paths))
possible_relevant_paths = []

for path_info in filtered_paths:
    lifeline1 = path_info[1]
    lifeline2 = path_info[2]

    src_paths = []
    dst_paths = []

    src_paths_temp = find_paths_for_lifeline(lifeline1, lifeline2, path_info, find_src_paths_to_lifeline)
    dst_paths_temp = find_paths_for_lifeline(lifeline2, lifeline1, path_info, find_dst_paths_from_lifeline)

    for path in src_paths_temp:
        if len(path) <= SEARCH_DEPTH:
            src_paths.append(path)

    for path in dst_paths_temp:
        if len(path) <= SEARCH_DEPTH:
            dst_paths.append(path)

    if lifeline1 in not_relevant_lifelines and lifeline2 in not_relevant_lifelines:
        for src_path in src_paths:
            for dst_path in dst_paths:
                src_node = src_path[0][0]
                dst_node = dst_path[len(dst_path) - 1][1]
                if src_node in sa_lifelines and dst_node in se_lifelines or src_node in se_lifelines and dst_node in sa_lifelines:
                    src_concat = src_path[:-1]
                    src_last_msg = src_concat[len(src_concat) - 1][2]
                    dst_first_msg = dst_path[0][2]

                    src_last_msg_time = i_fasst.messages_dict[src_last_msg]['msg_time']
                    dst_first_msg_time = i_fasst.messages_dict[dst_first_msg]['msg_time']
                    if dst_first_msg_time <= src_last_msg_time:
                        continue

                    path = src_concat + dst_path
                    possible_relevant_paths.append(path)

    elif len(src_paths) > 0:
        for path in src_paths:
            if check_timings(path, i_fasst.messages_dict):
                possible_relevant_paths.append(path)
    
    elif len(dst_paths) > 0:
        for path in dst_paths:
            if check_timings(path, i_fasst.messages_dict):
                possible_relevant_paths.append(path)

stop_time = timeit.default_timer()

print('Time for the Scenario 2: ', stop_time - start_time)

print_paths(possible_relevant_paths)