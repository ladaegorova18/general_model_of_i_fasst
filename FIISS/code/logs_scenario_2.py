from py2neo import Graph, Node, Relationship
from converter import Converter

# Scenario 2 - check logs info and if there are some alerts, add corresponding info to the graph
# -> fwVerifier 21 -> fwLoader 44 
# Safety feature fwLoader 44 has sensor value S1 out-of-bounds

INPUTFILE_2 = "inputfile2.xml"
TESTDB_2 = "testdb2"
LOG_ALERT = Relationship.type("LOG_ALERT")
LOG_TYPE = "LOG_INFO"

table = [("EAID_LL000000_3D1C_4643_AAF1_663DC1625107", "EAID_LL000000_B3FF_CE1D_B92E_A1DF8B0B6F44"),
("EAID_LL000000_8CB4_BC9B_8C2E_7329DD6154FE", "EAID_LL000000_8428_2537_A50F_802085E313F8")]

graph = Graph("bolt://localhost:7687", name=TESTDB_2, auth=("neo4j", "neo4jneo4j"))
converter = Converter(INPUTFILE_2, TESTDB_2, 'EAPK_511FDC72_60D2_413c_B488_D6CAE1507040', 'EAPK_A4E14F79_C0CB_4e3a_8A7A_ACB1EB7362C4', 'EAPK_F7282E3A_E460_4a55_813A_FA109AA4BB0E')
logs = ""
anomaly_logs = dict() # key - lifeline id, value - anomaly log
anomaly_logs["EAID_LL000000_8428_2537_A50F_802085E313F8"] = ("Sensor value S1 is out-of-bounds", "12:04:22")

for node_id, log in anomaly_logs.items():
    node_dst = Node(LOG_TYPE)
    node_dst["message"] = log[0]
    node_dst["msg_time"] = log[1]
    graph.create(node_dst)

    node_src = converter.find_or_create_node(node_id)
    edge = LOG_ALERT(node_src, node_dst)
    graph.create(edge)
    print("New edge is added")