from I_FASST_for_KG import I_FASST_KG
import timeit
import os, sys

# dirname = os.path.dirname(__file__)

INPUTFILE_1 = "inputfile1.xml"
TESTDB_1 = "testdb"

# big case - ~25 security features and 50 safety features
INPUTFILE_2 = "inputfile2.xml"
TESTDB_2 = "testdb2"

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-3]))

from safsecfi.I_FASST.code.I_FASST import *

def print_interaction_paths_with_logs(filtered_paths):
        table = [['path', 'path_length', 'alert_messages', 'is_suspicious']]
        for extended_path in filtered_paths:
            # p = path[0]
            # all_nodes = p['all_nodes']
            path = extended_path[0]
            all_nodes = path[3]
            all_nodes_list = ""
            for node in all_nodes:
                all_nodes_list = all_nodes_list + " -> " + node.get('name')

            path_length = len(all_nodes) - 1
            row = [all_nodes_list, path_length, extended_path[1], extended_path[2]] # p = path[0], lifeline1 = path[1], lifeline2 = path[2]
            table.append(row)

        print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))
        with open('table_i_fasst_logs.txt', 'w', encoding="utf-8") as f:
            f.write(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))

start = timeit.default_timer()
    
# ------------- I-FASST for knowledge graphs --------------------
i_fasst_kg = I_FASST_KG(INPUTFILE_2, TESTDB_2)
kg_filtered_paths = i_fasst_kg.start()

stop = timeit.default_timer()
print('Time for KG: ', stop - start)

anomaly_logs = dict() # key - lifeline id, value - anomaly log
anomaly_logs["EAID_LL000000_8CB4_BC9B_8C2E_7329DD6154FE"] = "Sensor value S1 of feature fwVerifier 21 is out-of-bounds" # -> fwVerifier 21 -> fwLoader 44  
anomaly_logs["EAID_LL000000_8428_2537_B016_7C742602B1E8"] = "Sensor value S2 of feature fwLoader 49 is disabled" # -> fwVerifier 10 -> fwLoader 49
anomaly_logs["EAID_LL000000_8CB4_BC9B_A19A_D3BDAAF55766"] = "Sensor value S3 of feature fwVerifier 20 is suspicious" # -> fwVerifier 20 -> fwLoader 51

kg_filtered_paths_with_logs = []
for path in kg_filtered_paths:
    ll_start = path[0][0][0]
    ll_end = path[0][0][1]
    alert_messages = ""

    if ll_start.get('node_id') in anomaly_logs:
         alert_messages += anomaly_logs[ll_start.get('node_id')]
    if ll_end.get('node_id') in anomaly_logs:
         if alert_messages != "":
              alert_messages += " "
         alert_messages += anomaly_logs[ll_end.get('node_id')]
    is_suspicious = alert_messages != ""
    extended_path = (path, alert_messages, is_suspicious)
    kg_filtered_paths_with_logs.append(extended_path)

print_interaction_paths_with_logs(kg_filtered_paths_with_logs)
# i_fasst_kg.print_interaction_paths()
    


# ------------- I-FASST for XML file --------------------
# pri_plus_sec_interac_paths, interaction_paths_that_passed_filter = run_i_fasst()