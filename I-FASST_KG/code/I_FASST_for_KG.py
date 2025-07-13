import networkx as nx
import os, sys

from py2neo import Graph

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-3]))

from tabulate import tabulate
from FIISS.code.FIISS_for_KG import FIISS_KG
from FIISS.code.converter import Converter
import timeit

interactions = dict() # mapping of each feature to its interactions

PACKAGE_TYPE = "uml:Package"
ACTIVITY_TYPE = "uml:Activity"
MESSAGE_TYPE = "MESSAGE"
LIFELINE_TYPE = "uml:Lifeline"

SAFETY_TYPE = "SAFETY"
SECURITY_TYPE = "SECURITY"

INPUTFILE_1 = "inputfile1.xml"
TESTDB_1 = "testdb"

# big case - ~25 security features and 50 safety features
INPUTFILE_2 = "inputfile2.xml"
TESTDB_2 = "testdb2"

SEARCH_DEPTH = 3
secFeID_compID_dict = {'EAPK_A4E14F79_C0CB_4e3a_8A7A_ACB1EB7362C4': [], 'EAPK_91006462_6C4C_B382_ADA1_94E9D3F38734': ['EAID_BBDC88AD_3B32_A50E_8951_E9DA1663B252'], 'EAPK_ADA194E9_D3F3_8734_B51B_4445A2012FD9': ['EAID_8951E9DA_1663_B252_9785_E9F9A013960C'], 'EAPK_80555360_9A28_B1E5_85D1_5D7D844F27D9': [], 'EAPK_ADA194E9_D3F3_8734_9E21_08613103D80D': ['EAID_8951E9DA_1663_B252_8A23_28461B584E6F'], 'EAPK_ADA194E9_D3F3_8734_8FCB_0398A055EBA1': ['EAID_8951E9DA_1663_B252_B025_B79164001836'], 
                       'EAPK_ADA194E9_D3F3_8734_919B_40FAAB0B7E3A': ['EAID_8951E9DA_1663_B252_8B0D_5D955A26E5D4'], 'EAPK_ADA194E9_D3F3_8734_843F_20E1AF319801': ['EAID_8951E9DA_1663_B252_88F7_E21EB90A5356'], 'EAPK_ADA194E9_D3F3_8734_9E1F_34A7D8009024': ['EAID_8951E9DA_1663_B252_9122_D7797CC570A5'], 'EAPK_ADA194E9_D3F3_8734_AF4F_F874AF93E29C': ['EAID_8951E9DA_1663_B252_98EB_3EDE4B48C040'], 'EAPK_80555360_9A28_B1E5_9504_A25BA3EC89A7': [], 'EAPK_ADA194E9_D3F3_8734_BFE4_BC37846E90AF': ['EAID_8951E9DA_1663_B252_863F_F40003A2D1EF'], 'EAPK_ADA194E9_D3F3_8734_9E8D_2254BA374F15': ['EAID_8951E9DA_1663_B252_933B_6664BCD6C728'], 
                       'EAPK_A47A5746_D0D5_7772_9CC5_E07E3A77E1AD': ['EAID_B5B88534_9845_FCA2_967D_49C4CAD568A2'], 'EAPK_ADA194E9_D3F3_8734_BC3C_D32F70F7E032': ['EAID_8951E9DA_1663_B252_A74A_19158C10E3AE'], 'EAPK_ADA194E9_D3F3_8734_B31C_F0BB0B71ECCD': ['EAID_8951E9DA_1663_B252_A946_AEE73BC0F606'], 
                       'EAPK_ADA194E9_D3F3_8734_8727_B2E6F566605D': ['EAID_8951E9DA_1663_B252_B91C_8DBA9AFA1560'], 'EAPK_ADA194E9_D3F3_8734_9808_50D474E86CF0': ['EAID_8951E9DA_1663_B252_A98A_FA567EF9AABB'], 'EAPK_80555360_9A28_B1E5_B1E1_36455FAFD722': [], 'EAPK_ADA194E9_D3F3_8734_902C_F0B4742FA06D': ['EAID_8951E9DA_1663_B252_AB7A_00A899A5A0DF'], 'EAPK_80555360_9A28_B1E5_8F36_570B715E66F9': [], 'EAPK_ADA194E9_D3F3_8734_B6F9_E9DBD3AB8D8C': ['EAID_80C3E555_CC11_600B_8CA5_D163A4D495AC', 'EAID_8951E9DA_1663_B252_80C3_E555CC11600B'], 'EAPK_80555360_9A28_B1E5_811F_899964728FBA': [], 
                       'EAPK_9CC5E07E_3A77_E1AD_B679_A45A12B90D90': ['EAID_967D49C4_CAD5_68A2_9989_F016048C1FF7'], 'EAPK_951D53B8_B63E_3F52_BBB4_9D5604F5C556': [], 'EAPK_B679A45A_12B9_0D90_ACEB_A15866920A8F': ['EAID_9989F016_048C_1FF7_A482_3F6F1CDCAC69'], 'EAPK_ACEBA158_6692_0A8F_99DC_A434943676DC': ['EAID_A4823F6F_1CDC_AC69_8864_7030968356E8'], 'EAPK_9CC5E07E_3A77_E1AD_8756_8F8DB560CBD1': ['EAID_967D49C4_CAD5_68A2_BB2E_9CA01D82116E'], 'EAPK_9CC5E07E_3A77_E1AD_9F52_F4B0B3391A78': ['EAID_967D49C4_CAD5_68A2_A1E5_DB8D87DCD9FF'], 
                       'EAPK_9CC5E07E_3A77_E1AD_9100_64626C4CB382': ['EAID_967D49C4_CAD5_68A2_BBDC_88AD3B32A50E'], 'EAPK_91006462_6C4C_B382_829A_5A71E850F20A': ['EAID_BBDC88AD_3B32_A50E_AF90_9BC341FC6D55'], 'EAPK_93486AAA_C2E4_A9FB_A47A_5746D0D57772': ['EAID_F310DC17_CC3D_40f0_B5B8_85349845FCA2'], 'EAPK_B5DA57A0_AB69_6786_B972_3F19CB76FF40': []}

#Configure safety relevant components for each safety feature
#Specify a dict in which each key is the XMI ID of a safety feature and the value corresponding to the key is the list of XMI IDs of security relevant components for the security feature
safFeID_compID_dict = {'EAPK_511FDC72_60D2_413c_B488_D6CAE1507040': [], 'EAPK_BAFE23FC_C21C_13B1_91C6_A897E15AE324': ['EAID_A56B23EF_2944_71C3_837B_D5E0B3E13852'], 'EAPK_88EFC992_BBF2_ADA1_AF8F_D5B93037F27E': ['EAID_800FB2AF_2CF8_D260_868D_04B5DAADFABF'], 'EAPK_88EFC992_BBF2_ADA1_8E4E_10CA7B05CDAB': ['EAID_800FB2AF_2CF8_D260_87A4_BCBCEFF44014'], 
                       'EAPK_88EFC992_BBF2_ADA1_9885_B17F28B8F682': ['EAID_800FB2AF_2CF8_D260_9747_A065E11E2187'], 'EAPK_88EFC992_BBF2_ADA1_99F2_42D6B195D2DA': ['EAID_800FB2AF_2CF8_D260_BC1C_46960C103963'], 'EAPK_88EFC992_BBF2_ADA1_BB31_0E5AB5517B59': ['EAID_800FB2AF_2CF8_D260_9D14_7703597ADA94'], 
                       'EAPK_88EFC992_BBF2_ADA1_AD4F_85C98BA5A231': ['EAID_800FB2AF_2CF8_D260_B4A4_02CCDB5D7DFE'], 'EAPK_88EFC992_BBF2_ADA1_A0F0_155B0E4504F7': ['EAID_800FB2AF_2CF8_D260_BBBC_9C0F04C9EC4F'], 'EAPK_88EFC992_BBF2_ADA1_A0C9_C0E54C0520FE': ['EAID_800FB2AF_2CF8_D260_AFC4_332817A1CC81'], 'EAPK_88EFC992_BBF2_ADA1_B773_6FF9AAEA6AA0': ['EAID_800FB2AF_2CF8_D260_9D3E_6C113325DAB9'], 
                       'EAPK_8C1B0AE6_982F_CFA6_A7AA_BD4C51DCA387': ['EAID_AC5A71C2_6704_0437_BCD6_0E86B55AA9FA'], 'EAPK_88EFC992_BBF2_ADA1_81CA_3800245D2BB2': ['EAID_800FB2AF_2CF8_D260_82FC_661FBD6B3454'], 
                       'EAPK_88EFC992_BBF2_ADA1_A078_5FDEEFB7DEAC': ['EAID_800FB2AF_2CF8_D260_A502_623102DA2193'], 'EAPK_A7AABD4C_51DC_A387_85D3_300FDC5B31D8': ['EAID_BCD60E86_B55A_A9FA_BC4E_3E216F099F5E'], 'EAPK_A7AABD4C_51DC_A387_A3A8_C477D30B2B3B': ['EAID_BCD60E86_B55A_A9FA_89E3_654331285749'], 'EAPK_A7AABD4C_51DC_A387_8A03_09A1330D33EB': ['EAID_BCD60E86_B55A_A9FA_8F45_B77A0DBAAC13'], 'EAPK_A7AABD4C_51DC_A387_B69E_0093A628A2EE': ['EAID_BCD60E86_B55A_A9FA_B026_1262B770C237'], 'EAPK_A7AABD4C_51DC_A387_9DC3_C53EA7EB4AFC': ['EAID_BCD60E86_B55A_A9FA_8F84_AE178C81028F'], 
                       'EAPK_A7AABD4C_51DC_A387_98E1_7822B51DAD42': ['EAID_BCD60E86_B55A_A9FA_96FD_FCD2D5A4BC59'], 'EAPK_A7AABD4C_51DC_A387_91E1_101D2B14E073': ['EAID_BCD60E86_B55A_A9FA_8BCE_10549C3368A9'], 
                       'EAPK_A7AABD4C_51DC_A387_A33B_EBA36596CB5A': ['EAID_BCD60E86_B55A_A9FA_889B_BD25A1199289'], 'EAPK_A7AABD4C_51DC_A387_800D_B080506590A2': ['EAID_BCD60E86_B55A_A9FA_8753_9DD1B00442A9'], 'EAPK_A7AABD4C_51DC_A387_9D7B_6C5B986BC1D9': ['EAID_BCD60E86_B55A_A9FA_8EA7_BF48F4987A7A'], 'EAPK_A7AABD4C_51DC_A387_BD80_ED9680EF7C01': ['EAID_BCD60E86_B55A_A9FA_8DAA_94305DF0679A'], 'EAPK_A7AABD4C_51DC_A387_A050_54E1119DBC47': ['EAID_BCD60E86_B55A_A9FA_A5C1_3E5E0B3365C6'], 'EAPK_A7AABD4C_51DC_A387_8C29_DEAB3FA5776D': ['EAID_BCD60E86_B55A_A9FA_BCAD_195779219425'], 
                       'EAPK_A7AABD4C_51DC_A387_999D_0BAC6F0A7132': ['EAID_BCD60E86_B55A_A9FA_9ACB_09E042488213'], 'EAPK_A7AABD4C_51DC_A387_9696_82FE471B6654': ['EAID_BCD60E86_B55A_A9FA_AD52_24F693165D41'], 'EAPK_A7AABD4C_51DC_A387_8250_94D2BCADBA59': ['EAID_BCD60E86_B55A_A9FA_BBCC_8ED224D73C3B'], 'EAPK_A7AABD4C_51DC_A387_8A38_B33ECD1905FF': ['EAID_BCD60E86_B55A_A9FA_91AA_5AC0422AEB15'], 
                       'EAPK_A7AABD4C_51DC_A387_BEB0_A675B79E87CC': ['EAID_BCD60E86_B55A_A9FA_B6E5_1E3E54196DB7'], 'EAPK_A7AABD4C_51DC_A387_9201_29D66A47498D': ['EAID_BCD60E86_B55A_A9FA_B30F_9D23F28F79D4'], 'EAPK_800DB080_5065_90A2_BAFE_23FCC21C13B1': ['EAID_87539DD1_B004_42A9_A56B_23EF294471C3'], 'EAPK_BAFE23FC_C21C_13B1_AA6C_2BD1071DADDE': ['EAID_A56B23EF_2944_71C3_B745_F538CDCAFBC0'], 'EAPK_BAFE23FC_C21C_13B1_95A0_038B547C9737': ['EAID_A56B23EF_2944_71C3_AEAA_3881436348A9'], 'EAPK_BAFE23FC_C21C_13B1_BF8B_A27AA472EAF5': ['EAID_A56B23EF_2944_71C3_9D6A_741E2391AD3C'], 
                       'EAPK_BAFE23FC_C21C_13B1_955F_FC55463E8321': ['EAID_A56B23EF_2944_71C3_817F_8E5012F654D1'], 'EAPK_BAFE23FC_C21C_13B1_8465_A97BEA3A340E': ['EAID_A56B23EF_2944_71C3_8CFE_D76C58C517A8'], 'EAPK_BAFE23FC_C21C_13B1_819C_46F9685D1249': ['EAID_A56B23EF_2944_71C3_A251_45A8670455E5'], 'EAPK_BAFE23FC_C21C_13B1_98A4_574B2D831650': ['EAID_A56B23EF_2944_71C3_9141_E50751816ECA'], 'EAPK_BAFE23FC_C21C_13B1_8193_9F680CBA1B75': ['EAID_A56B23EF_2944_71C3_B00D_60E23539E8CB'], 'EAPK_BAFE23FC_C21C_13B1_963A_02CCC1EFE2D1': ['EAID_A56B23EF_2944_71C3_85ED_4CBB0B9E1489'], 
                       'EAPK_BAFE23FC_C21C_13B1_A5B2_6BC8C6CBE6CE': ['EAID_A56B23EF_2944_71C3_9D22_40EDCEDF8228'], 'EAPK_800DB080_5065_90A2_86C0_619DDA219FAD': ['EAID_87539DD1_B004_42A9_BE09_647B11467AC8'], 'EAPK_BAFE23FC_C21C_13B1_B824_2FBF2DCDDB34': ['EAID_A56B23EF_2944_71C3_A726_DE8E1E655D72'], 'EAPK_BAFE23FC_C21C_13B1_9001_2BD834000825': ['EAID_A56B23EF_2944_71C3_9330_E59576822B9D'], 'EAPK_800DB080_5065_90A2_9190_7C79A9EEC4B2': ['EAID_87539DD1_B004_42A9_95D8_06AC3075B04D'], 'EAPK_BAFE23FC_C21C_13B1_8206_B6092E2CAE5A': ['EAID_A56B23EF_2944_71C3_8490_AAC919E4518E'], 
                       'EAPK_BAFE23FC_C21C_13B1_9181_E271E8E769A3': ['EAID_A56B23EF_2944_71C3_92E7_F5A4565FDF90'], 'EAPK_BAFE23FC_C21C_13B1_88EF_C992BBF2ADA1': ['EAID_A56B23EF_2944_71C3_800F_B2AF2CF8D260'], 'EAPK_BD1C86BB_28FF_1023_8C1B_0AE6982FCFA6': ['EAID_3533CB2C_F8C7_4299_AC5A_71C267040437']}

def get_mapped_name(node_id):
    if node_id == 'fwVerifier':
        return 'Secure boot of automotive firmware'
    elif 'fwVerifier' in node_id:
        return node_id.replace('fwVerifier', 'Secure boot')
    elif 'fwLoader' in node_id:
        return node_id.replace('fwLoader', 'Safety integrity check')
    # elif ' sequence ' in node_id:
        # return node_id.replace(' sequence ', ' ')
        # return node_id.replace('NRF', 'Not relevant')
    return node_id

class I_FASST_KG(FIISS_KG):
    # I-FASST analysis
    # input:
    # UML diagram in the form of knowledge graph
    # list of safety and security features
    # each feature mapped to its security and safety relevant components
    # (can deduce from the graph)
    def __init__(self, input_file, db_name):
        super().__init__(input_file, db_name)

        self.packages = []
        self.safety_packages = [] # each package represents a feature
        self.security_packages = []
        self.all_interaction_paths = []

        self.sa_features_lifelines = dict() # mapping of safety features to their lifelines
        self.se_features_lifelines = dict() # mapping of security features to their lifelines
    
    
    def find_relevant_components(self):
        self.se_components = self.get_values_from_dict(secFeID_compID_dict)
        self.sa_components = self.get_values_from_dict(safFeID_compID_dict)
    
    
    def find_paths_using_network_X(self, queries):
        node_set = set()
        edges_list = []
        self.messages_dict = dict()
        nodes_dict = dict()
        for message in self.ll_message_exchanges:
        # for message in self.ll_message_exchanges:
            message_src  = message[0]
            message_info = message[1]
            message_dst  = message[2]

            node_set.add(message_src)
            node_set.add(message_dst)
            node_src_id = message_src.get('node_id')
            node_dst_id = message_dst.get('node_id')

            nodes_dict[node_src_id] = message_src
            nodes_dict[node_dst_id] = message_dst

            message_id = message_info.get('occ_message_id')
            # message_id = message_info.get('node_id')
            self.messages_dict[message_id] = message_info

            if message_src != message_dst:
                edges_list.append((message_src, message_dst, message_id))

        for lifeline in self.se_lifelines:
            node_set.add(lifeline)

        for lifeline in self.sa_lifelines:
            node_set.add(lifeline)
        
        graph = nx.MultiDiGraph()
        graph.add_nodes_from(node_set)
        graph.add_edges_from(edges_list)

        for query in queries:
            lifeline1 = query[0]
            lifeline2 = query[1]
            for path in nx.all_simple_edge_paths(graph, source = lifeline1, target = lifeline2, cutoff = SEARCH_DEPTH):
                if lifeline1 == lifeline2:
                    continue
                all_nodes = []
                for path_step in path:
                    node_src = path_step[0]
                    node_dst = path_step[1]
                    if not node_src in all_nodes:
                        all_nodes.append(node_src)

                    if not node_dst in all_nodes:
                        all_nodes.append(node_dst)
                self.all_interaction_paths.append((path, lifeline1, lifeline2, all_nodes))

        return self.all_interaction_paths


    def check_path_relevance(self, path, pp_1, pp_2, messages_dict = None):
        prev_message_package = ""
        for path_step in path:
        # p = path['p']
        # for message in p:
            message_id = path_step[2]
            if messages_dict == None:
                messages_dict = self.messages_dict
            message = messages_dict[message_id]
            message_package = message.get('package')
            if prev_message_package == "":
                prev_message_package = message_package 

            if prev_message_package != message_package:
                return False

            nodes = message.nodes
            lifeline_1 = nodes[0]
            lifeline_2 = nodes[1]

            package_1 = lifeline_1.get('package')
            package_2 = lifeline_2.get('package')

            package_1_int = package_1
            package_2_int = package_2
            # package_1_int = abs(hash(package_1)) % (10 ** 8)
            # package_2_int = abs(hash(package_2)) % (10 ** 8)
            if package_1 != pp_1 and package_1 != pp_2:
                return False
            if package_2 != pp_1 and package_2 != pp_2:
                return False

            if message_package != package_1_int and message_package != package_2_int:
                return False
            
            query = "match (n) - [r:REPRESENTS] -> (m) where n.node_id=$node_id return m"

            result_1 = self.graph.run(query, node_id=lifeline_1.get('node_id'))
            data = result_1.data()
            instance_spec_1 = data[0]['m']
            is_type_1 = instance_spec_1.get('type')

            result_2 = self.graph.run(query, node_id=lifeline_2.get('node_id'))
            data = result_2.data()
            instance_spec = data[0]['m']
            is_type_2 = instance_spec.get('type')

            if is_type_1 != "uml:InstanceSpecification" or is_type_2 != "uml:InstanceSpecification":
                return False

            if message_package != package_1:
                return False
            
            # query="MATCH p=(n) - [r1:REPRESENTS] -> (m) - [r2:CLASSIFIES] -> (t) <- [r3:REPRESENTS] - (t2) where n.node_id=$node_id RETURN p"
            # result = self.graph.run(query, node_id=lifeline_1.get('node_id'))
            # data = result.data()
            # if len(data) > 0:
            #     return False
            
            # result = self.graph.run(query, node_id=lifeline_2.get('node_id'))
            # data = result.data()
            # if len(data) > 0:
            #     return False
            
            # 1. both lifelines belong to the same feature
            # 2. one of the features has either both lifelines or a lifeline and a link to IS of the second lifeline

        return True
    

    def find_lifelines_message_exhanges(self):
        self.ll_message_exchanges = []

        query = "MATCH (n) -[r:MESSAGE]-> (m) RETURN n, r, m"
        result = self.graph.run(query)
        data = result.data()
        for triple in data:
            src = triple['n']
            dst = triple['m']
            message_r = triple['r']
            self.ll_message_exchanges.append((src, message_r, dst))

    
    def arch_element_analysis(self):
        # A. architectural element analysis
        # 0) for each feature find its sa/se relevant components
        self.packages, self.safety_packages, self.security_packages = self.find_all_packages() # remove duplicates
        self.find_relevant_components()
        # self.arch_analysis()
        # self.features_sa_components = self.get_features_safety_components() # mapping of safety and security features to their components
        # self.features_se_components = self.get_features_security_components() # remove duplicates

        # 1) find safety and security relevant lifelines for each feature
        # mapping from a safety feature to its safety relevant ll and
        # from a security feature to its security relevant ll

        # 2) find message exchanges (look for FIISS)
        self.find_lifelines_message_exhanges()
        # self.message_exchanges = self.find_message_exchanges()
        self.find_relevant_lifelines()

        print("Architectural element analysis finished")

    
    def inter_feature_interaction_analysis(self):
        # B. Inter-feature interaction analysis
        # 1) Interaction graph
        # each node is a lifeline and each edge is a message exchange 
        # (don't need this because we already use the graph) so skip it
        # (if we do it as discussed in FIISS for KG, try_to_find_path)

        # 2) Lifeline query list
        # list of queries, where each query is a tuple of source and dest lifeline
        # from A.1) and the first in se relevant and second is sa relevant and vice versa
        # in FIISS we search paths between all possible combinations of lifelines,
        # here we look only for combinations of lifelines that have different relevance
        queries = []
        for se_lifeline in self.se_lifelines:
            for sa_lifeline in self.sa_lifelines:
                query = (se_lifeline, sa_lifeline) 
                queries.append(query)

        for sa_lifeline in self.sa_lifelines:
            for se_lifeline in self.se_lifelines:
                query = (sa_lifeline, se_lifeline)
                queries.append(query)

        # 3) Interaction paths
        # Apply queries to the graph to find paths (as in the FIISS)
        # also can configure their maximum length p
        # self.find_all_interaction_paths_in_one_query(queries)
        # self.find_all_interaction_paths(queries)
        # self.find_optimized_interaction_paths()
        self.find_paths_using_network_X(queries)

        print("Inter-feature interaction analysis finished")


    def interaction_path_processing(self, check_relevance, paths = None):
        # C. Interaction path processing
        # 1) Filtering interaction paths
        # indirect path - sequence of messages between source and destination ll
        # remove paths with interaction chains
        # (exclude the paths that contain one or more sa/se relevant intermediate ll)
        self.filtered_paths = []
        self.feature_interactions = []
        if paths == None:
            paths = self.all_interaction_paths
            
        for path_info in paths:
            # each path is (p, lifeline1, lifeline2) if we use features like in FIISS
            # or (p, lifeline1, lifeline2) if we avoid features (we use option 2)
            path = path_info[0]

            all_nodes = path_info[3]

            # all_nodes = path['all_nodes']
            intermediate_nodes = all_nodes[1:-1] # take all elements except first and last
            has_interaction_chains = False

            lifeline1 = path_info[1]
            lifeline2 = path_info[2]
            
            pp_1 = lifeline1.get('parent_package')
            pp_2 = lifeline2.get('parent_package')
            
            if not check_relevance(path, pp_1, pp_2, self.messages_dict):
                # print("path {} {} is not relevant, continue".format(lifeline1.get('name'), lifeline2.get('name')))
                continue

            for node_id in intermediate_nodes:
                if self.has_type(node_id, LIFELINE_TYPE):
                    if node_id in self.sa_lifelines or node_id in self.se_lifelines or node_id in self.sa_se_lifelines:
                        has_interaction_chains = True

            # 2) Interacting safety and security features
            # Get feature interactions from the filtered interaction paths
            if has_interaction_chains:
                # print("Has interaction chains, continue")
                continue
            
            feature1 = lifeline1.get('parent_package') 
            feature2 = lifeline2.get('parent_package')
            features_interaction = (feature1, feature2)

            if not (features_interaction in self.feature_interactions): # remove interaction is src and dst are already in the list
                self.filtered_paths.append(path_info)
                self.feature_interactions.append(features_interaction) 

        print("Interaction path processing finished")

        return self.filtered_paths, self.feature_interactions


    def print_interaction_paths(self):
        table = [['path', 'lifeline 1', 'lifeline 2', 'path_length']]
        for path in self.filtered_paths:
            # p = path[0]
            # all_nodes = p['all_nodes']
            all_nodes = path[3]
            all_nodes_list = ""
            for node in all_nodes:
                if all_nodes_list != "":
                    all_nodes_list = all_nodes_list + " -> "
                all_nodes_list = all_nodes_list + get_mapped_name(node.get('name'))

            path_length = len(all_nodes) - 1
            row = [all_nodes_list, path[1].get('node_id'), path[2].get('node_id'), path_length] # p = path[0], lifeline1 = path[1], lifeline2 = path[2]
            table.append(row)

        print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))

        path_count = (len(table) - 1)
        print("Total amount of unfiltered paths {}".format(len(self.all_interaction_paths)))
        print("Total amount of filtered paths {}".format(path_count))

        with open('table_kg.txt', 'w', encoding="utf-8") as f:
            f.write(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))

        with open('table_kg_unformatted.txt', 'w', encoding="utf-8") as f:
            for line in table:
                f.write(line[1] + " " + line[2] + "\n")

        fi_table = [['feature 1', 'feature 2']]
        for feature_int in self.feature_interactions:
            row = [feature_int[0], feature_int[1]]
            fi_table.append(row)

        with open('table_kg_features.txt', 'w', encoding="utf-8") as f:
            f.write(tabulate(fi_table, headers='firstrow', tablefmt='fancy_grid'))    


    def start(self):
        self.graph = Graph("bolt://localhost:7687", name=self.db_name, auth=("neo4j", "neo4jneo4j")) # Create a graph object

        self.converter = Converter(self.input_file, self.db_name, 'EAPK_511FDC72_60D2_413c_B488_D6CAE1507040', 'EAPK_A4E14F79_C0CB_4e3a_8A7A_ACB1EB7362C4', 'EAPK_F7282E3A_E460_4a55_813A_FA109AA4BB0E')    
        # self.converter.convert() # comment if already have a graph

        self.arch_element_analysis()
        self.inter_feature_interaction_analysis()
        self.interaction_path_processing(self.check_path_relevance)

        print("I-FASST analysis completed")

        return self.filtered_paths


# start = timeit.default_timer()
# i_fasst_kg = I_FASST_KG(INPUTFILE_1, TESTDB_1)
# kg_filtered_paths = i_fasst_kg.start()

# stop = timeit.default_timer()
# print('Time for KG: ', stop - start)

# i_fasst_kg.print_interaction_paths()