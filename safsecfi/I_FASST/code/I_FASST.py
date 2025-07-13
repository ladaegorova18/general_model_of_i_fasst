# Copyright (c) 2024 Robert Bosch GmbH
# SPDX-License-Identifier: MIT

import timeit
start = timeit.default_timer()
import io
import os
import time
import json
import textwrap
import itertools as it
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import itertools
from itertools import product
from tabulate import tabulate

import sys
dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, '..', 'lib'))
# from I_FASST_lib import *
# from I_FASST_lib import *
from safsecfi.I_FASST.code.I_FASST_lib import *

unrelevant_features = []

INPUT_FILE_IDX = 2
SEARCH_DEPTH = 3

######################################Configurable inputs#####################################
#Configurable inputs for security features
# security_feature_pkg_list
# secFeaturePkgID_list = [] #Specify XMI IDs of each security feature
secFeaturePkgID_list = ["EAPK_93486AAA_C2E4_A9FB_A47A_5746D0D57772", 
                        "EAPK_91006462_6C4C_B382_829A_5A71E850F20A", 
                        "EAPK_9CC5E07E_3A77_E1AD_9100_64626C4CB382",
                        "EAPK_9CC5E07E_3A77_E1AD_9F52_F4B0B3391A78",
                        "EAPK_9CC5E07E_3A77_E1AD_8756_8F8DB560CBD1",
                        "EAPK_ACEBA158_6692_0A8F_99DC_A434943676DC",
                        "EAPK_B679A45A_12B9_0D90_ACEB_A15866920A8F",
                        "EAPK_9CC5E07E_3A77_E1AD_B679_A45A12B90D90",
                        "EAPK_ADA194E9_D3F3_8734_B6F9_E9DBD3AB8D8C",
                        "EAPK_ADA194E9_D3F3_8734_902C_F0B4742FA06D",
                        "EAPK_ADA194E9_D3F3_8734_9808_50D474E86CF0",
                        "EAPK_ADA194E9_D3F3_8734_8727_B2E6F566605D",
                        "EAPK_ADA194E9_D3F3_8734_B31C_F0BB0B71ECCD",
                        "EAPK_ADA194E9_D3F3_8734_BC3C_D32F70F7E032",
                        "EAPK_A47A5746_D0D5_7772_9CC5_E07E3A77E1AD",
                        "EAPK_ADA194E9_D3F3_8734_9E8D_2254BA374F15",
                        "EAPK_ADA194E9_D3F3_8734_BFE4_BC37846E90AF",
                        "EAPK_ADA194E9_D3F3_8734_AF4F_F874AF93E29C",
                        "EAPK_ADA194E9_D3F3_8734_9E1F_34A7D8009024",
                        "EAPK_ADA194E9_D3F3_8734_843F_20E1AF319801",
                        "EAPK_ADA194E9_D3F3_8734_919B_40FAAB0B7E3A",
                        "EAPK_ADA194E9_D3F3_8734_8FCB_0398A055EBA1",
                        "EAPK_ADA194E9_D3F3_8734_9E21_08613103D80D",
                        "EAPK_ADA194E9_D3F3_8734_B51B_4445A2012FD9",
                        "EAPK_91006462_6C4C_B382_ADA1_94E9D3F38734"]

#Configurable inputs for safety features
ecu_sa_main_pkg_path = ".//packagedElement[@xmi:id='{}'][@xmi:type='uml:Package']/packagedElement[@xmi:type='uml:Package']".format('EAPK_511FDC72_60D2_413c_B488_D6CAE1507040') #Specify XMI ID of the main package inside quotes of .format(''); this main package contains other packages, of which each package represents a specific safety feature

#Configure security relevant components for each security feature
#Specify a dict in which each key is the XMI ID of a security feature and the value corresponding to the key is the list of XMI IDs of security relevant components for the security feature e.g. {'EAPK_8451D5F3_2430_4c17_BBA3_FCDD12AFD7DD': ['EAID_CE767137_4FA5_4ed2_9CD5_C504E3D349F2', 'EAID_7FBBC274_4A52_4b4d_AD3C_C4881393D12F']}
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


#For each security relevant component ID, configure its name. Note that alternatively, the names can be automatically extracted from the architecture model
secComponentID_name_dict = {} #Specify a dict in which each key is the XMI ID of a security relevant component and the value corresponding to the key is the name of the security relevant component e.g. {'EAID_CE767137_4FA5_4ed2_9CD5_C504E3D349F2':'MasterSecModule'}

#For each safety relevant component ID, configure its name. Note that alternatively, the names can be automatically extracted from the architecture model
safComponentID_name_dict = {} #Specify a dict in which each key is the XMI ID of a safety relevant component and the value corresponding to the key is the name of the safety relevant component
##############################################################################################
nextiterationcheck = object()

class GetSecurityFeatures():
    "Get a list of all security features as packages"
    def __init__(self, security_feature_list):
        self.security_feature_list = security_feature_list
    
    def get_security_feature_name(self, iterator_type):
        "For each element in the list, find its name and store it in a dict with the key as the feature id and the name as value"
        feature_id_name_dict = {}
        for element in self.security_feature_list:
            path = ".//packagedElement[@xmi:id = '{}'][@xmi:type = 'uml:Package']".format(element)
            path_iterator = get_iterator(path, iterator_type) #search will be performed in the specified input xmi file
            for object in path_iterator:
                id, name, type = get_iterator_attributes(object)
                feature_id_name_dict.update({element:name})
        return feature_id_name_dict

class GetSafetyFeatures():
    "Get a list of all safety features as packages"
    def __init__(self, path):
        self.path = path
    
    def get_safety_feature(self, iterator_type):
        "get all safety features from the main/master safety package"
        feature_id_name_dict = {}
        safety_feature_list = []
        sa_feature_path_iterator = get_iterator(self.path, iterator_type) #search will be performed in the specified input xmi file
        for element in sa_feature_path_iterator:
            id, name, type = get_iterator_attributes(element)
            safety_feature_list.append(id)
            feature_id_name_dict.update({id:name})
        return safety_feature_list, feature_id_name_dict

class GetBehavioralElements():
    "Extract messages and lifelines from sequence diagrams; group (create lists) lifelines that are safety-relevant, security relevant, both safety and security relevant, and neither safety nor security relevant"
    def __init__(self, featurePkgID_list, featurePkgID_name_dict, relComponentID_set, feID_relCompID_dict):
        self.featurePkgID_list = featurePkgID_list
        self.featurePkgID_name_dict = featurePkgID_name_dict
        self.relComponentID_set = relComponentID_set
        self.feID_relCompID_dict = feID_relCompID_dict
    
    def extract_references_inSD(self, lifelineID, referenceID, iterator_type):
        "Extract if the reference to an interaction fragment in a sequence diagram of a feature refers to an interaction fragment in another feature or same feature"
        ownerfeaturepackage = None
        diagramID = None
        dependentfeature_id = None
        dependentfeature_name = None
        dependentfeature_type = None
        referenceSD_dependentFeID_dict = {}
        searchdiagram_path = ".//element[@xmi:idref = '{}'][@xmi:type = 'uml:InteractionOccurrence']/extendedProperties".format(referenceID)
        searchdiagram_iterator = get_iterator(searchdiagram_path, iterator_type) #search will be performed in the specified input xmi file
        for ele1 in searchdiagram_iterator:
            diagramID = ele1.get('diagram')
        if diagramID is not None:
            featureofdiagram_path = ".//diagram[@xmi:id = '{}']/model".format(diagramID)
            featureofdiagram_iterator = get_iterator(featureofdiagram_path, iterator_type) #search will be performed in the specified input xmi file
            for ele2 in featureofdiagram_iterator:
                ownerfeaturepackage = ele2.get('package')
            if ownerfeaturepackage in self.featurePkgID_list:
                pass
            else:
                parentfeaturesearch_path = ".//packagedElement[@xmi:id='{}'][@xmi:type = 'uml:Package']/..".format(ownerfeaturepackage)
                parentfeaturesearch_iterator = get_iterator(parentfeaturesearch_path, iterator_type) #search will be performed in the specified input xmi file
                for ele3 in parentfeaturesearch_iterator:
                    dependentfeature_id, dependentfeature_name, dependentfeature_type = get_iterator_attributes(ele3)
                if dependentfeature_id in self.featurePkgID_list:
                    referenceSD_dependentFeID_dict.update({lifelineID:dependentfeature_id})
                else:
                    grandparentfeaturesearch_path = ".//packagedElement[@xmi:id='{}'][@xmi:type = 'uml:Package']/..".format(dependentfeature_id)
                    grandparentfeaturesearch_iterator = get_iterator(grandparentfeaturesearch_path, iterator_type) #search will be performed in the specified input xmi file
                    for ele4 in grandparentfeaturesearch_iterator:
                        dependentfeature_id, dependentfeature_name, dependentfeature_type = get_iterator_attributes(ele4)
                        if dependentfeature_id in self.featurePkgID_list:
                            referenceSD_dependentFeID_dict.update({lifelineID:dependentfeature_id})
                        else:
                            print("Warning! Parent feature of reference_interaction_fragment: ", referenceID, " not found!")
        return referenceSD_dependentFeID_dict
    
    def extract_classifier_of_lifelines(self, feature, lifeline_set, iterator_type):
        "For a given list of lifelines that may have associated classifiers (i.e. lifelines starting with EAID_LL000000), identify their classifiers"
        name = None
        type = None
        instSpec_ID = None #instance specification ID
        ISclassifier_ID = None #classifier (ID) of the instance specification
        classifier_id = None
        classifierID_set = set()
        classifierID_name_dict = {}
        mappedLLID_classifierID_dict = {}
        refSD_dependentFeID_dict = {}
        
        instSpecID_set = set()
        mappedLLID_ISID_dict = {}
        mappedISID_classifierID_dict = {}
        
        if feature == "EAPK_ADA194E9_D3F3_8734_902C_F0B4742FA06D":
            print(3)

        if feature == "EAPK_91006462_6C4C_B382_829A_5A71E850F20A":
            print(3)
        
        for element in lifeline_set:
            id = None
            represents = None
            instSpec_ID = None

            if element.startswith('EAID_LL000000'):
                LLsearch_path = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//lifeline[@xmi:id = '{}']".format(feature, element)
                LLsearch_iterator = get_iterator(LLsearch_path, iterator_type) #search will be performed in the specified input xmi file
                for ele1 in LLsearch_iterator:
                    represents = ele1.get('represents')
                ISsearch_path = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//*[@xmi:id='{}']/type".format(feature, represents)
                ISsearch_iterator = get_iterator(ISsearch_path, iterator_type) #search will be performed in the specified input xmi file
                for ele2 in ISsearch_iterator:
                    instSpec_ID = ele2.get('{http://schema.omg.org/spec/XMI/2.1}idref')
                #if instSpec_ID is not None
                    
                path = ".//packagedElement[@xmi:id = '{}'][@xmi:type = 'uml:InstanceSpecification']".format(instSpec_ID)

                # ISdetailssearch_path = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//*[@xmi:id='{}']".format(feature, instSpec_ID)
                ISdetailssearch_iterator = get_iterator(path, iterator_type) #search will be performed in the specified input xmi file
                for ele2 in ISdetailssearch_iterator:
                    instSpec_ID, instSpec_name, instSpec_type = get_iterator_attributes(ele2)
                    #print("Debug! Classifier detials of owned_lifeline_id: ", element, " classifier_id: ", instSpec_ID, " classifier_name: ", instSpec_name, " classifier_type: ", instSpec_type)
                    if instSpec_type == 'uml:InstanceSpecification':
                        ISclassifier_ID = ele2.get('classifier')
                        #The following data structs are used to create a lifeline list in appropriate format and use it to find used messages. Note: I-FASST differentiates between owned messages and used messages
                        instSpecID_set.add(instSpec_ID)
                        mappedLLID_ISID_dict.update({element:instSpec_ID})
                        mappedISID_classifierID_dict.update({instSpec_ID:ISclassifier_ID})
                        if ISclassifier_ID is not None:
                            id, name, type, classifier_id = search_allocatedUMLelement_byID(ISclassifier_ID)
                            print("Debug! Classifier details of instance_specID: ", instSpec_ID, " LLclassifier_ID: ", id, " LLclassifier_name: ", name, " LLclassifier_type: ", type, " LLclassifier_classifier: ", classifier_id)
                            if id is not None:
                                classifierID_set.add(id)
                                classifierID_name_dict.update({id:name})
                                mappedLLID_classifierID_dict.update({element:id})
                            else:
                                classifierID_set.add(ISclassifier_ID)
                                classifierID_name_dict.update({ISclassifier_ID:name})
                                mappedLLID_classifierID_dict.update({element:ISclassifier_ID})
                    elif instSpec_type == 'uml:Actor' or instSpec_type == 'uml:Component':
                        classifierID_set.add(instSpec_ID)
                        classifierID_name_dict.update({instSpec_ID:instSpec_name})
                        mappedLLID_classifierID_dict.update({element:instSpec_ID})
                        #The following data structs are used to create a lifeline list in appropriate format and use it to find used messages.
                        instSpecID_set.add(instSpec_ID)
                        mappedLLID_ISID_dict.update({element:instSpec_ID})
                        mappedISID_classifierID_dict.update({instSpec_ID:instSpec_ID})
                    else:
                        print("Warning! classifier of instSpec_ID: ",instSpec_ID, " not found!")
            else:
                #Checking for interface of a component; A message sent to an interface will be depicted in the interaction graph as the message to the component which has this interface.
                id, name, type, classifier_id = get_interfacebyID(feature, element) # packageId, instanceSpecificationId 
                if id is not None:
                    if type == "uml:Interface":
                        classifierID_set.add(id)
                        classifierID_name_dict.update({id:name})
                        mappedLLID_classifierID_dict.update({element:id})
                        #The following data structs are used to create a lifeline list in appropriate format and use it to find used messages.
                        instSpecID_set.add(element)
                        mappedLLID_ISID_dict.update({element:element})
                        mappedISID_classifierID_dict.update({element:id})
                else:
                    #Checking if the classifier of element is a component, class, object, actor etc.
                    id, name, type, ISclassifier_id = search_allocatedUMLelement_byID(element)
                    #print("Debug! Classifier detils of covered_lifeline_id: ", element, " LLWoClassifier_ID: ", id, " LLWoclassifier_name: ", name, " LLWoclassifier_type: ", type, " LLWoclassifier_classifier: ", ISclassifier_id)
                    if id is not None:
                        if type == 'uml:InstanceSpecification':
                            id, name, type, classifier_id = search_allocatedUMLelement_byID(ISclassifier_id)
                            #print("Debug! LLWoClassifier_ID: ", id, " LLclassifier_name: ", name, " LLclassifier_type: ", type, " LLclassifier_classifier: ", classifier_id)
                            #The following data structs are used to create the lifeline list in appropriate format to find used messages
                            instSpecID_set.add(element)
                            mappedLLID_ISID_dict.update({element:element})
                            mappedISID_classifierID_dict.update({element:classifier_id})
                            if id is not None:
                                classifierID_set.add(id)
                                classifierID_name_dict.update({id:name})
                                mappedLLID_classifierID_dict.update({element:id})
                            else:
                                classifierID_set.add(ISclassifier_id)
                                classifierID_name_dict.update({ISclassifier_id:name})
                                mappedLLID_classifierID_dict.update({element:ISclassifier_id})
                        elif type == "uml:InteractionOccurrence": #Reference to a fragment found
                            print("Attention! Reference to internal_interaction_fragment_id: ", id, " name: ", name, " found!")
                            referenceSD_dependentFeID_dict = self.extract_references_inSD(element, id, iterator_type) #search will be performed in the specified input xmi file
                            refSD_dependentFeID_dict.update(referenceSD_dependentFeID_dict)
                        elif type == 'uml:Component' or type == 'uml:Class' or type == 'uml:Actor' or type == 'uml:Object' or type == 'uml:ProvidedInterface':
                            #print("Debug! LLWoClassifier_ID: ", id, " LLclassifier_name: ", name, " LLclassifier_type: ", type, " LLclassifier_classifier: ", classifier_id)
                            classifierID_set.add(id)
                            classifierID_name_dict.update({id:name})
                            mappedLLID_classifierID_dict.update({element:id}) 
                            #The following data structs are used to create the lifeline list in appropriate format to find used messages
                            instSpecID_set.add(element)
                            mappedLLID_ISID_dict.update({element:element})
                            mappedISID_classifierID_dict.update({element:element})
                        else:
                            print("Warning! element_id: ", element, " will not be stored! Classifier ID not None")
                    else:
                        print("Warning! element_id: ", element, " will not be stored! Classifier ID None")   
        return classifierID_set, classifierID_name_dict, mappedLLID_classifierID_dict, refSD_dependentFeID_dict, instSpecID_set, mappedLLID_ISID_dict, mappedISID_classifierID_dict
        
    def extract_lifelines(self, feature, iterator_type):
        "For a given feature, extract its lifelines from fragment element(OccurSpec, CombinedFragment etc.)"
        lifeline_set = set()
        ownedlifelineID_set = set()
        ownedlifelineID_name_dict = {}
        mappedownedLLIDclassifierID_dict = {}
        SeqOccurSpecID_set = set()
        OccurSpecID_lifelineID_dict = {}
        gate_id = None
        gate_name = None
        gate_type = None
        
        lifeline_id = None
        lifeline_name = None
        lifeline_type = None
        
        instSpecID_set = set()
        

        if feature == "EAPK_BAFE23FC_C21C_13B1_955F_FC55463E8321":
            print(3)

        if feature == "EAPK_BAFE23FC_C21C_13B1_955F_FC55463E8321":
            print(3)

        if feature == "EAPK_ADA194E9_D3F3_8734_8FCB_0398A055EBA1":
            print(3)

        if feature == "EAPK_ADA194E9_D3F3_8734_8FCB_0398A055EBA1":
            print(3)
        
        lifeline_path =      ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//lifeline".format(feature) #to extract lifeline ID
        formalGate_path = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//*[@xmi:type='uml:Gate']".format(feature) #to extract gate ID
        combinedFragmentCoveredLL_path = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//fragment[@xmi:type='uml:CombinedFragment']/covered".format(feature) #to extract xmi:idref to collect lifelines covered by the interaction fragment (alt, opt, loop, ...)
        occurSpecCoveredLL_path = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//fragment[@xmi:type='uml:OccurrenceSpecification']".format(feature) #to extract the attribute 'covered'
        
        lifeline_iterator = get_iterator(lifeline_path, iterator_type) #search will be performed in the specified input xmi file
        formalgate_iterator = get_iterator(formalGate_path, iterator_type) #search will be performed in the specified input xmi file
        combinedFragmentCoveredLL_iterator = get_iterator(combinedFragmentCoveredLL_path, iterator_type) #search will be performed in the specified input xmi file
        occurSpecCoveredLL_iterator = get_iterator(occurSpecCoveredLL_path, iterator_type) #search will be performed in the specified input xmi file
        
        for element in lifeline_iterator:
            lifeline_id, lifeline_name, lifeline_type = get_iterator_attributes(element) #extract ID of lifeline
            if lifeline_id.startswith('EAID_LL'):
                lifeline_set.add(lifeline_id)
            else:
                ownedlifelineID_set.add(lifeline_id)
                ownedlifelineID_name_dict.update({lifeline_id: lifeline_name})
                mappedownedLLIDclassifierID_dict.update({lifeline_id:lifeline_id})
        
        for element in formalgate_iterator:
            gate_id, gate_name, gate_type = get_iterator_attributes(element) #extract ID of formal gate
            #print("\nDebug! gate_id: ", gate_id, " gate_name: ", gate_name, " gate_type: ", gate_type)
            if gate_id is not None:
                ownedlifelineID_set.add(gate_id)
                #print("\nDebug! Added gate_id: ", gate_id, " gate_name: ", gate_name, " gate_type: ", gate_type)
                ownedlifelineID_name_dict.update({gate_id: gate_name})
                mappedownedLLIDclassifierID_dict.update({gate_id:gate_id})
        
        for element in combinedFragmentCoveredLL_iterator:
            lifeline_id = element.get('{http://schema.omg.org/spec/XMI/2.1}idref') #extract of lifeline ID covered by combined interaction fragment
            if lifeline_id not in ownedlifelineID_set:
                lifeline_set.add(lifeline_id)
        
        for element in occurSpecCoveredLL_iterator:
            OccurSpecID = element.get('{http://schema.omg.org/spec/XMI/2.1}id') #get occurence specification ID because it is used in sendEvent & receiveEvent IDs of <message xmi:type= 'uml:Message'>
            lifeline_id = element.get('covered') #extract ID of lifeline indicated by occurrence specification
            SeqOccurSpecID_set.add(OccurSpecID) #create a set to add OccurSpec IDs; this list will be used to find src and dst of <message xmi:type= 'uml:Message'>
            if lifeline_id is not None:
                OccurSpecID_lifelineID_dict.update({OccurSpecID:lifeline_id}) #mapping of OccurSpec ID to its corresponding lifeline ID
                if lifeline_id not in ownedlifelineID_set:
                    lifeline_set.add(lifeline_id)
        SeqOccurSpecID_set.update(ownedlifelineID_set)
        OccurSpecID_lifelineID_dict.update(mappedownedLLIDclassifierID_dict)
        #print("\nDebug! Feature: ", self.featurePkgID_name_dict[feature], " lifeline_set: ", lifeline_set)
        classifierID_set, classifierID_name_dict, mappedLLID_classifierID_dict, refSD_dependentFeID_dict, instSpecID_set, mappedLLID_ISID_dict, mappedISID_classifierID_dict = self.extract_classifier_of_lifelines(feature, lifeline_set, iterator_type)
        
        classifierID_set.update(ownedlifelineID_set)
        classifierID_name_dict.update(ownedlifelineID_name_dict)
        mappedLLID_classifierID_dict.update(mappedownedLLIDclassifierID_dict)
        instSpecID_set.update(ownedlifelineID_set)
        
        return lifeline_set, classifierID_set, classifierID_name_dict, mappedLLID_classifierID_dict, SeqOccurSpecID_set, OccurSpecID_lifelineID_dict, refSD_dependentFeID_dict, instSpecID_set, mappedISID_classifierID_dict
    
    def validate_msgtuples(self, edgelisttobevalidated, msgID_list, msgID_name_dict):
        "Validate message tuple i.e. (msgSrcID, msgDstID, msgID) with respect to message list to check if all messages are covered/included in the tuple list"
        msguncoveredintuple_list = []
        msguncoveredintupleName_list = []
        msgfromtuple_list = [ele[-1] for ele in edgelisttobevalidated]
        msguncoveredintupleID_list, msguncoveredintupleName_list = query_lists_for_uniqueelement(msgfromtuple_list, msgID_list, msgID_name_dict)
        return msguncoveredintupleID_list, msguncoveredintupleName_list
    
    def extract_owned_messages(self, feature, LLOccurSpecID_set, mappedLLOccurSpecID_LLID_dict, mappedLLID_classifierID_dict, classifierID_name_dict, refSD_dependentFeID_dict, iterator_type):
        "Extract messages contained in each feature package of type = uml:Message"
        msg_id = None
        msg_name = None
        msg_type = None
        msg_srcClassifierID = None
        msg_dstClassifierID = None
        msg_srcClassifierName = None
        msg_dstClassifierName = None
        
        ownedMsgID_list = []
        ownedMsgID_name_dict = {}
        edge_tuple = ()
        node_set = set()
        nodeID_name_labeldict = {}
        edge_list = []
        edge_label_dict = {}
        
        srcFeID = None
        dstFeID = None
        feID_dependentFeID_dict = {}
        msgID_msgSort_dict = {}
        
        msgID_path_search = ".//packagedElement[@xmi:type = 'uml:Package'][@xmi:id = '{}']/.//message[@xmi:type = 'uml:Message']".format(feature)
        msgID_iterator = get_iterator(msgID_path_search, iterator_type) #search will be performed in the specified input xmi file
        #print("\nDebug! Feature: ", self.featurePkgID_name_dict[feature], " OccurSpec_list: ", LLOccurSpecID_set)
        for object in msgID_iterator:
            msg_id, msg_name, msg_type = get_iterator_attributes(object)
            msg_sort = object.get('messageSort')
            msg_signature = object.get('signature')
            #print("Debug! msgID: ", msg_id, " msgname_list: ", msg_name, " msg_sort: ", msg_sort, " msg_sign: ", msg_signature)
            
            msgID_msgSort_dict.update({msg_id: msg_sort})
            
            ownedMsgID_list.append(msg_id)
            ownedMsgID_name_dict.update({msg_id:msg_name})
            
            msg_src = object.get('sendEvent')
            msg_dst = object.get('receiveEvent')
            
            if (msg_src in LLOccurSpecID_set) and (msg_dst in LLOccurSpecID_set):
                msg_srcClassifierID = query_twodicts_by_key(msg_src, mappedLLOccurSpecID_LLID_dict, mappedLLID_classifierID_dict)
                msg_dstClassifierID = query_twodicts_by_key(msg_dst, mappedLLOccurSpecID_LLID_dict, mappedLLID_classifierID_dict)
                print("\nDebug! Feature: ", self.featurePkgID_name_dict[feature], "msg_id: ", msg_id, " msg_name: ", msg_name, " msg_srcClassifierID: ", msg_srcClassifierID, " msg_dstClassifierID: ", msg_dstClassifierID)
 
                if msg_srcClassifierID is not None and msg_dstClassifierID is not None:
                    #print("TC2! Creating tuple for message : ", msg_name)
                    msg_srcClassifierName = classifierID_name_dict[msg_srcClassifierID]
                    msg_dstClassifierName = classifierID_name_dict[msg_dstClassifierID]
                    edge_tuple = (msg_srcClassifierID, msg_dstClassifierID, msg_id)
                    
                    node_set.add(msg_srcClassifierID)
                    node_set.add(msg_dstClassifierID)
                    nodeID_name_labeldict.update({msg_srcClassifierID: msg_srcClassifierName, msg_dstClassifierID: msg_dstClassifierName})
                
                    edge_list.append(edge_tuple)
                    edge_label_dict.update({edge_tuple:msg_name})
                elif msg_srcClassifierID is None and msg_dstClassifierID is not None:
                    srcFeID = query_twodicts_by_key(msg_src, mappedLLOccurSpecID_LLID_dict, refSD_dependentFeID_dict)
                    if srcFeID is not None:
                        feID_dependentFeID_dict.update({srcFeID:feature})
                    else:
                        print("Warning! msg_srcID: ", msg_src, " not found!")
                elif msg_srcClassifierID is not None and msg_dstClassifierID is None:
                    dstFeID = query_twodicts_by_key(msg_dst, mappedLLOccurSpecID_LLID_dict, refSD_dependentFeID_dict)
                    if dstFeID is not None:
                        feID_dependentFeID_dict.update({feature: dstFeID})
                    else:
                        print("Warning! msg_dstID: ", msg_dst, " not found!")
                elif msg_srcClassifierID is None and msg_dstClassifierID is None:
                    srcFeID = query_twodicts_by_key(msg_src, mappedLLOccurSpecID_LLID_dict, refSD_dependentFeID_dict)
                    dstFeID = query_twodicts_by_key(msg_dst, mappedLLOccurSpecID_LLID_dict, refSD_dependentFeID_dict)
                    if srcFeID is not None and dstFeID is not None:
                        feID_dependentFeID_dict.update({srcFeID: dstFeID})
                    else:
                        print("Warning! msg_srcID: ", msg_src, " or msg_dstID: ", msg_dst, " not found!")
        return ownedMsgID_list, ownedMsgID_name_dict, node_set, nodeID_name_labeldict, edge_list, edge_tuple, edge_label_dict, feID_dependentFeID_dict, msgID_msgSort_dict
    
    def get_used_message_name(self, messageID, searchfilename):
        "For a given message ID, extract its name by tracing the connector for the message"
        messagename_path_search = ".//connector[@xmi:idref = '{}']".format(messageID)
        messagename_iterator = get_iterator(messagename_path_search, searchfilename)
        for ele in messagename_iterator:
            message_name = ele.get('name')
        return message_name
    
    def get_usedmessage_tuples(self, msgSrc, msgDst, msgID, filesearchpath, LLClassifierID_name_dict, mappedISID_classifierID_dict):
        "For a given msgID, msgName, msgSrc, and msgDst, create a tuple"
        node_set = set()
        nodeID_name_labeldict = {}
        edge_label_dict = {}
        edge_tuple = ()
        seq_name = None
        
        msg_srcID = mappedISID_classifierID_dict[msgSrc]
        msg_dstID = mappedISID_classifierID_dict[msgDst]
        if msg_srcID is not None and msg_dstID is not None:
            seq_name = self.get_used_message_name(msgID, filesearchpath)
            msg_srcName = LLClassifierID_name_dict[msg_srcID]
            msg_dstName = LLClassifierID_name_dict[msg_dstID]
            edge_tuple = (msg_srcID, msg_dstID, msgID)
            node_set.add(msg_srcID)
            node_set.add(msg_dstID)
            nodeID_name_labeldict.update({msg_srcID: msg_srcName, msg_dstID: msg_dstName})
            edge_label_dict.update({edge_tuple:seq_name})
        else:
            if msg_srcID is None:
                print("Warning! Msg: ", msgID, " Msg_srcID: ", msgSrc, "'s classifier not found in mappedISID_classifierID_dict input!")
            elif msg_dstID is None:
                print("Warning! Msg: ", msgID, " Msg_dstID: ", msgDst, "'s classifier not found in mappedISID_classifierID_dict input!")
        return seq_name, edge_tuple, node_set, nodeID_name_labeldict, edge_label_dict
    
    def extractSeq_from_iterator(self, seqID_set, edges_list, msgDir, iterator, inputSrcOrDstSeqID, SrcOrDst_string, LLsInCombinedFragment_set, ownedMsgID_list, mappedISID_classifierID_dict, classifierID_name_dict, filesearchpath):
        "For a given sequence search iterator (search sequence with srcID or dstID as input) as input, extract sequence ID of the message"
        seqSrcOrDstID = None
        seqID_set = set()
        seqID_name_dict = {}
        
        seqID_name_dict = {}
        edges_list = []
        edge_labels_dict = {}
        edges_tuple = ()
        nodes_set = set()
        nodesID_name_labeldict = {}
        
        for element in iterator:
            seqID = None
            start_id = element.get('start')
            end_id = element.get('end')
            seqSrcOrDstID = element.get(SrcOrDst_string) #extract source or destination of the message based on input
            if seqSrcOrDstID in LLsInCombinedFragment_set:
                seqID = element.get('{http://schema.omg.org/spec/XMI/2.1}id')
                if seqID not in ownedMsgID_list:
                    if seqID not in seqID_set:
                        seqID_set.add(seqID)
                        if msgDir == 'start':
                            seq_name, edge_tuple, node_set, nodeID_name_labeldict, edge_label_dict = self.get_usedmessage_tuples(inputSrcOrDstSeqID, seqSrcOrDstID, seqID, filesearchpath, classifierID_name_dict, mappedISID_classifierID_dict)
                            if len(edge_tuple) != 0 and edge_tuple not in edges_list:
                                seqID_name_dict.update({seqID:seq_name})
                                edges_list.append(edge_tuple)
                                edge_labels_dict.update(edge_label_dict)
                                nodes_set.update(node_set)
                                nodesID_name_labeldict.update(nodeID_name_labeldict)
                        elif msgDir == 'end':
                            seq_name, edge_tuple, node_set, nodeID_name_labeldict, edge_label_dict = self.get_usedmessage_tuples(seqSrcOrDstID, inputSrcOrDstSeqID, seqID, filesearchpath, classifierID_name_dict, mappedISID_classifierID_dict)
                            if len(edge_tuple) != 0 and edge_tuple not in edges_list:
                                seqID_name_dict.update({seqID:seq_name})
                                edges_list.append(edge_tuple)
                                edge_labels_dict.update(edge_label_dict)
                                nodes_set.update(node_set)
                                nodesID_name_labeldict.update(nodeID_name_labeldict)
                        else:
                            print("Warning! Invalid msgDir: ", msgDir)
                    else:
                        continue
        return seqID_set, nodes_set, nodesID_name_labeldict, edges_list, edge_labels_dict, seqID_name_dict

    def extract_used_messages(self, ownedMsgID_list, lifeline_set, mappedISID_classifierID_dict, classifierID_name_dict, filesearchpath):
        "Search for messages sent to or received by lifelines (lifeline_set as input) that are not owned but only used by the feature being analyzed"
        sequenceID_set = set()
        sequenceID_name_dict = {}
        node_set = set()
        nodeID_name_labeldict = {}
        edge_label_dict = {}
        edge_list = []
        for element in lifeline_set:
            seqID_set1 = set()
            seqID2_set2 = set()
            nodes_set1 = set()
            nodes_set2 = set()
            nodesID_name_labeldict1 = {}
            nodesID_name_labeldict2 = {}
            edges_list1 = []
            edges_list2 = []
            edge_labels_dict1 = {}
            edge_labels_dict2 = {}
            seqID_name_dict1 = {}
            seqID_name_dict2 = {}
            
            seq_sourcepath_search = ".//Sequence[@start = '{}']".format(element) #search for <Sequence> with the lifeline as source
            seq_targetpath_search = ".//Sequence[@end = '{}']".format(element) #search for <Sequence> with the lifeline as destination
            seqsourcepath_iterator = get_iterator(seq_sourcepath_search, filesearchpath)
            seqtargetpath_iterator = get_iterator(seq_targetpath_search, filesearchpath)
            
            seqID_set1, nodes_set1, nodesID_name_labeldict1, edges_list1, edge_labels_dict1, seqID_name_dict1 = self.extractSeq_from_iterator(sequenceID_set, edge_list, 'start', seqsourcepath_iterator, element, 'end', lifeline_set, ownedMsgID_list, mappedISID_classifierID_dict, classifierID_name_dict, filesearchpath)
            
            sequenceID_set.update(seqID_set1)
            for ele in edges_list1:
                if ele not in edge_list:
                    edge_list.append(ele)
            
            seqID2_set2, nodes_set2, nodesID_name_labeldict2, edges_list2, edge_labels_dict2, seqID_name_dict2 = self.extractSeq_from_iterator(sequenceID_set, edge_list, 'end', seqtargetpath_iterator, element, 'start', lifeline_set, ownedMsgID_list, mappedISID_classifierID_dict, classifierID_name_dict, filesearchpath)
            
            sequenceID_set.update(seqID2_set2)
            for ele in edges_list2:
                if ele not in edge_list:
                    edge_list.append(ele)
            
            nodes_set1.update(nodes_set2)
            nodesID_name_labeldict1.update(nodesID_name_labeldict2)
            edge_labels_dict1.update(edge_labels_dict2)
            seqID_name_dict1.update(seqID_name_dict2)
            
            node_set.update(nodes_set1)
            nodeID_name_labeldict.update(nodesID_name_labeldict1)
            edge_label_dict.update(edge_labels_dict1)
            sequenceID_name_dict.update(seqID_name_dict1)
        return sequenceID_set, sequenceID_name_dict, node_set, nodeID_name_labeldict, edge_list, edge_label_dict
    
    def extract_lifelines_and_messages(self):
        "For each feature being analyzed, extract messages. Extract the lifelines involved in the message exchange."
        feID_dependentFeID_dict = {}
        allSD_feID_dependentFeID_dict = {'feature':'interacting_feature'}
        
        feID_nodeIDset_dict = {} # {feature1: (LL1, LL2), feature2:(), ..} here LL1 and LL2 refer to the corresponding classifiers of the lifelines
        feID_nodeIDnamedict_dict = {} # {feature1: {LL1_id:LL1_name, LL2_id:LL2_name}, feature2:(), ..}
        feID_edgeIDlist_dict = {}
        feID_edgeIDnamedict_dict = {}
        feID_msgIDnamedict_dict = {}
        feID_relMsgIDslist_dict = {}
        feID_relMsgNameslist_dict = {}
        msgID_name_dict = {}
        feGroup_msgID_msgSort_dict = {}
        for feature in self.featurePkgID_list:
            feature_name = self.featurePkgID_name_dict[feature]
            msguncoveredintupleID_list = []
            msguncoveredintupleName_list = []
            uncoveredMsgintupleID_list = []
            uncoveredMsgintupleName_list = []
            
            lifeline_set = set()
            classifierID_set = set()
            classifierID_name_dict = {}
            mappedLLID_classifierID_dict = {}
            mappedOccurSpecID_lifelineID_dict = {}
            nodeID_set = set()
            nodeID_name_labeldict = {}
            edge_list = []
            edge_label_dict = {}

            global unrelevant_features
        
            if feature == "EAPK_B679A45A_12B9_0D90_ACEB_A15866920A8F":
                print(3)
                
            #extracting lifelines of each feature
            lifeline_set, classifierID_set, classifierID_name_dict, mappedLLID_classifierID_dict, SeqOccurSpecID_set, mappedOccurSpecID_lifelineID_dict, refSD_dependentFeID_dict, instSpecID_set, mappedISID_classifierID_dict = self.extract_lifelines(feature, INPUT_FILE_IDX) #search will be performed in the specified input xmi file; for our case study, it is input xmi file 2
            classifierNames_list = [value for value in classifierID_name_dict.values()]
            #print("\nDebug! Feature: ", feature_name, " lifelines_no: ", len(classifierID_set), " lifelines: ", classifierID_name_dict)
            
            #extracting owned messages of each feature
            ownedMsgID_list, ownedMsgID_name_dict, ownednode_set, ownednodeID_name_labeldict, ownededge_list, ownededge_tuple, ownededge_label_dict, feID_dependentFeID_dict, msgID_msgSort_dict = self.extract_owned_messages(feature, SeqOccurSpecID_set, mappedOccurSpecID_lifelineID_dict, mappedLLID_classifierID_dict, classifierID_name_dict, refSD_dependentFeID_dict, INPUT_FILE_IDX) #search will be performed in the specified input xmi file; for our case study, it is input xmi file 2
            
            #ownedMsgname_list = [value for value in ownedMsgID_name_dict.values()]
            allSD_feID_dependentFeID_dict.update(feID_dependentFeID_dict)
            feGroup_msgID_msgSort_dict.update(msgID_msgSort_dict)
            
            #validating tuples obtained from extracted owned messages
            msguncoveredintupleID_list, msguncoveredintupleName_list = self.validate_msgtuples(ownededge_list, ownedMsgID_list, ownedMsgID_name_dict)
            
            #print("\nDebug! Feature: ", feature_name, " owned_message_no: ", len(ownedMsgID_list), " ownedMsg: ", ownedMsgID_name_dict)
            #print("\nDebug! Feature: ", feature_name, " owned_tuple_no: ", len(ownededge_list), " ownedMsg: ", ownededge_label_dict)
            print("\nDebug! Feature: ", feature_name, " uncoveredMsgInTuples_no : ", len(msguncoveredintupleID_list), ", uncoveredMsgInTupleIDs: ", msguncoveredintupleID_list, " uncoveredMsgInTuples: ", msguncoveredintupleName_list)
            
            merged_set = lifeline_set.union(instSpecID_set)
            #extracting used messages of each feature
            usedMsgID_set, usedMsgID_name_dict, usednode_set, usednodeID_name_labeldict, usededge_list, usededge_label_dict = self.extract_used_messages(ownedMsgID_list, merged_set, mappedISID_classifierID_dict, classifierID_name_dict, INPUT_FILE_IDX) #search will be performed in the specified input xmi file
            
            #validating tuples obtained from extracted used messages
            uncoveredMsgintupleID_list, uncoveredMsgintupleName_list = self.validate_msgtuples(usededge_list, list(usedMsgID_set), usedMsgID_name_dict)
            
            #print("\nDebug! Feature: ", feature_name, " used_message_no: ", len(usedMsgID_set), " usedMsg: ", usedMsgID_name_dict)
            #print("\nDebug! Feature: ", feature_name, " used_tuple_no: ", len(usededge_list), " usedTuple_list: ", usededge_list, " usedTuple_dict: ", usededge_label_dict)
            print("\nDebug! Feature: ", feature_name, " uncoveredMsgInTuples_no : ", len(uncoveredMsgintupleID_list), ", uncoveredMsgInTupleIDs: ", uncoveredMsgintupleID_list, " uncoveredMsgInTuples: ", uncoveredMsgintupleName_list)
            
            msgID_name_dict.update(ownedMsgID_name_dict)
            msgID_name_dict.update(usedMsgID_name_dict)
            nodeID_set.update(ownednode_set)
            nodeID_set.update(usednode_set)
            nodeID_name_labeldict.update(ownednodeID_name_labeldict)
            nodeID_name_labeldict.update(usednodeID_name_labeldict)
            edge_list.extend(ownededge_list)
            for ele in usededge_list:
                if ele not in edge_list:
                    edge_list.append(ele)
            edge_label_dict.update(ownededge_label_dict)
            edge_label_dict.update(usededge_label_dict)
            
            #Distinguishing relevant messages for each feature i.e. mapping each feature to its relevant messages
            relCompID_list = self.feID_relCompID_dict[feature]
            relCompNames_list = get_listnames_from_listIDs_fromdictwithmissingkeys(relCompID_list, nodeID_name_labeldict)
            relMsgIDs_list = []
            relMsgNames_list = []
            for element in edge_list:
                eachtuples_srcID = element[-3]
                eachtuples_dstID = element[-2]
                if eachtuples_dstID in relCompID_list or eachtuples_srcID in relCompID_list:
                    relMsgID = element[-1]
                    if relMsgID not in relMsgIDs_list:
                        relMsgIDs_list.append(relMsgID)
            relMsgNames_list = get_listnames_from_listIDs(relMsgIDs_list, msgID_name_dict)
            print("\nFeature: ", feature_name, " relevant_lifelines: ", relCompNames_list, "relevant_msgs: ", relMsgNames_list)
            if len(relCompNames_list) == 0:
                unrelevant_features.append(feature_name)

            feID_relMsgIDslist_dict.update({feature: relMsgIDs_list}) #Map feature id to its relevant message ids
            feID_relMsgNameslist_dict.update({feature_name: relMsgNames_list}) #Map feature name to its relevant message names
            
            #Creating data structures to store node and edge details for each feature for the next step: interaction analysis.
            feID_nodeIDset_dict.update({feature:nodeID_set}) #each feature and its corresponding lifeline (i.e. classifier) ID set
            feID_nodeIDnamedict_dict.update({feature:nodeID_name_labeldict})
            feID_edgeIDlist_dict.update({feature:edge_list})
            feID_edgeIDnamedict_dict.update({feature:edge_label_dict})
            feID_msgIDnamedict_dict.update({feature:msgID_name_dict})
        print("\nDebug! Dependency list created by .sd analysis: ", allSD_feID_dependentFeID_dict)
        print(tabulate(allSD_feID_dependentFeID_dict, tablefmt = 'grid', maxcolwidths=[20,20]), "\n")
        return feID_nodeIDset_dict, feID_nodeIDnamedict_dict, feID_edgeIDlist_dict, feID_edgeIDnamedict_dict, msgID_name_dict, feGroup_msgID_msgSort_dict, feID_relMsgIDslist_dict, feID_msgIDnamedict_dict

class InteractionAnalysis():
    "Create a multi directed graph using classifiers of lifelines and messages in the sequence diagrams of all safety and security features. Then identify safety and security relevant lifelines and query the graph to find interaction paths between relevant lifelines."
    def __init__(self, featurePkgID_list, featurePkgID_name_dict, secComponentID_set, safComponentID_set, secsafComponentID_set, feID_nodeIDset_dict, feID_nodeIDnamedict_dict, feID_edgeIDlist_dict, feID_edgeIDnamedict_dict, secFeID_compID_dict, safFeID_compID_dict, msgID_name_dict, secComponentID_name_dict, safComponentID_name_dict, msgID_msgSort_dict, feID_relMsgIDslist_dict, feID_compID_dict, secFeaturePkgID_list, safFeature_pkg_list, relevantComponentID_set):
        self.featurePkgID_list = featurePkgID_list
        self.featurePkgID_name_dict = featurePkgID_name_dict
        self.secComponentID_set = secComponentID_set
        self.safComponentID_set = safComponentID_set
        self.secsafComponentID_set = secsafComponentID_set
        self.feID_nodeIDset_dict = feID_nodeIDset_dict
        self.feID_nodeIDnamedict_dict = feID_nodeIDnamedict_dict
        self.feID_edgeIDlist_dict = feID_edgeIDlist_dict
        self.feID_edgeIDnamedict_dict = feID_edgeIDnamedict_dict
        self.secFeID_compID_dict = secFeID_compID_dict
        self.safFeID_compID_dict = safFeID_compID_dict
        self.msgID_name_dict = msgID_name_dict
        self.secComponentID_name_dict = secComponentID_name_dict
        self.safComponentID_name_dict = safComponentID_name_dict
        self.msgID_msgSort_dict = msgID_msgSort_dict
        self.feID_relMsgIDslist_dict = feID_relMsgIDslist_dict
        self.feID_compID_dict = feID_compID_dict
        self.secFeaturePkgID_list = secFeaturePkgID_list
        self.safFeature_pkg_list = safFeature_pkg_list
        self.relevantComponentID_set = relevantComponentID_set
    
    def get_relevant_lifelines(self, featurenodeIDs_set):
        "Identify which lifelines are safety relevant, security relevant and both safety and security relevant"
        relevantnodeID_list = []
            
        secsafnodeID_set = get_commonelementIDsset(featurenodeIDs_set, self.secsafComponentID_set)
        secnodeID_set = get_commonelementIDsset(featurenodeIDs_set, self.secComponentID_set)
        safnodeID_set = get_commonelementIDsset(featurenodeIDs_set, self.safComponentID_set)
        
        secsafnodeID_list = list(secsafnodeID_set)
        secnodeID_list = list(secnodeID_set)
        safnodeID_list = list(safnodeID_set)
        relevantnodeID_list = list(set(secsafnodeID_list + secnodeID_list + safnodeID_list))
        nonrelnodeID_list = list(filter(lambda i: i not in relevantnodeID_list, list(featurenodeIDs_set))) #set of feature lifelines that are neither safety nor security relevant
            
        return secnodeID_set, safnodeID_set, secsafnodeID_set, set(nonrelnodeID_list)
        
    def get_graphquery_list(self, seclifelineIDs_set, saflifelineID_set, secsaflifelineID_set):
        "Get list of relevant node combinations for querrying the graph"
        LLcmb_SecToSaf_querylist = []
        LLcmb_SafToSec_querylist = []
        if len(seclifelineIDs_set) != 0 and len(saflifelineID_set) != 0: #safety relevant lifelines and security relevant lifelines
            productA_list = list(itertools.product(list(seclifelineIDs_set), list(saflifelineID_set)))
            productB_list = list(itertools.product(list(saflifelineID_set), list(seclifelineIDs_set)))
            if len(productA_list) != 0:
                LLcmb_SecToSaf_querylist.extend(productA_list)
            if len(productB_list) != 0:
                LLcmb_SafToSec_querylist.extend(productB_list)
            if len(secsaflifelineID_set) != 0: #safety relevant lifelines and security relevant lifelines and safety-and-security relevant lifelines
                productB_list = list(itertools.product(list(saflifelineID_set), list(secsaflifelineID_set)))
                productC_list = list(itertools.product(list(secsaflifelineID_set), list(saflifelineID_set)))
                productD_list = list(itertools.product(list(seclifelineIDs_set), list(secsaflifelineID_set)))
                productE_list = list(itertools.product(list(secsaflifelineID_set), list(seclifelineIDs_set)))
                if len(productB_list) != 0:
                    LLcmb_SafToSec_querylist.extend(productB_list)
                if len(productC_list) != 0:
                    LLcmb_SecToSaf_querylist.extend(productC_list)
                if len(productD_list) != 0:
                    LLcmb_SecToSaf_querylist.extend(productD_list)
                if len(productE_list) != 0:
                    LLcmb_SafToSec_querylist.extend(productE_list)
        elif len(seclifelineIDs_set) == 0 and len(saflifelineID_set) != 0 and len(secsaflifelineID_set) != 0: #safety relevant lifelines and safety-and-security relevant lifelines
            productF_list = list(itertools.product(list(saflifelineID_set), list(secsaflifelineID_set)))
            productG_list = list(itertools.product(list(secsaflifelineID_set), list(saflifelineID_set)))
            if len(productF_list) != 0:
                LLcmb_SafToSec_querylist.extend(productF_list)
            if len(productG_list) != 0:
                LLcmb_SecToSaf_querylist.extend(productG_list)
        elif len(seclifelineIDs_set) != 0 and len(saflifelineID_set) == 0 and len(secsaflifelineID_set) != 0: #security relevant lifelines and safety-and-security relevant lifelines
            productH_list = list(itertools.product(list(seclifelineIDs_set), list(secsaflifelineID_set)))
            productI_list = list(itertools.product(list(secsaflifelineID_set), list(seclifelineIDs_set)))
            if len(productH_list) != 0:
                LLcmb_SecToSaf_querylist.extend(productH_list)
            if len(productI_list) != 0:
                LLcmb_SafToSec_querylist.extend(productI_list)
        elif len(seclifelineIDs_set) == 0 and len(saflifelineID_set) == 0 and len(secsaflifelineID_set) != 0: #only safety-and-security relevant lifelines
            pass
        else: #either only security relevant lifelines or only safety relevant lifelines
            pass
        return LLcmb_SafToSec_querylist, LLcmb_SecToSaf_querylist
    
    def collect_Inodes_for_a_path(self, path):
        "for a received path that contains sub-paths, collect all intermediate nodes; note that format of subpath is (SWC1, SWC2, msg)"
        Inodes_set = set()
        if len(path) > 1: #check intermediate nodes if path_len > 1, i.e. if there are any intermediate nodes present in the path
            for index, subpath in enumerate(path):
                if index == 0:
                    Inode2 = subpath[-2]
                    Inodes_set.add(Inode2)
                elif index != 0 and index != len(path)-1:
                    Inode1 = subpath[-2]
                    Inode2 = subpath[-3]
                    Inodes_set.add(Inode1)
                    Inodes_set.add(Inode2)
                elif index == len(path)-1:
                    Inode1 = subpath[-3]
                    Inodes_set.add(Inode1)
                else:
                    print("Warning! no condition met for index: ", index, " for subpath: ", subpath, " in the path: ", path, "!")
        return list(Inodes_set)
        
    def check_Inodes_relevance(self, Inodes_list, firstandlastnode_list):
        "check if any node in the given list of intermediate nodes (for a path) is either safety or security relevant; if at least one intermediate node is safety or security relevant, set the intermediate node (Inode) relevance flag to 0 i.e. ignore path"
        Inode_rel_flag = 1 #consider this path unless this flag is set to 0
        relvComponentID_list = list(set(firstandlastnode_list).symmetric_difference(self.relevantComponentID_set))
        for element in Inodes_list:
            if element in relvComponentID_list:
                Inode_rel_flag = 0 #ignore path because there exists atleast one intermediate node that is safety or security relevant
                break
        return Inode_rel_flag
    
    def get_path_name(self, path, nodeID_name_dict):
        "For a path consisting of subpaths represented in IDs format; get its path name"
        path_name = []
        #print("Debug! path: ", path)
        for subpath in path:
            src_name = nodeID_name_dict[subpath[0]]
            dst_name = nodeID_name_dict[subpath[1]]
            if subpath[-1] in self.msgID_name_dict.keys():
                key_name = self.msgID_name_dict[subpath[-1]]
            else:#if key_name is None:
                key_name = "-"
            subpath_name = (src_name,dst_name,key_name)
            path_name.append(subpath_name)
        return path_name
    
    def extract_FI_based_on_relvMsgs_and_SWC(self, path, src, dst, secnodeID_set, safnodeID_set, nodeID_name_dict):
        "For a given path, check the safety and security relevances of the first and last messages and components of a path"
        srcfeID_list = []
        dstfeID_list = []
        perpath_FIs_list = [] 
        for index, subpath in enumerate(path):
            if index == 0 and index == len(path) - 1:
                firstorlastmsg = subpath[-1]
                feID_list = query_dict_by_wlistvalue(self.feID_relMsgIDslist_dict, firstorlastmsg)
                if len(feID_list) == 0:
                    srcfeID_list = query_dict_by_wlistvalue(self.feID_compID_dict, src)
                    dstfeID_list = query_dict_by_wlistvalue(self.feID_compID_dict, dst)
                else:
                    for element in feID_list:
                        if (element in self.secFeaturePkgID_list and src in secnodeID_set) or (element in self.safFeature_pkg_list and src in safnodeID_set):
                            dstfeID_list = query_dict_by_wlistvalue(self.feID_compID_dict, dst)
                            if element not in srcfeID_list:
                                srcfeID_list.append(element)
                        elif (element in self.secFeaturePkgID_list and dst in secnodeID_set) or (element in self.safFeature_pkg_list and dst in safnodeID_set):
                            srcfeID_list = query_dict_by_wlistvalue(self.feID_compID_dict, src)
                            if element not in dstfeID_list:
                                dstfeID_list.append(element)
                        else:
                            print("Warning! Mismatch in safety and security relevance of software component & feature!")
            elif index != 0 and index != len(path)-1:
                continue
            elif index != 0 and index == len(path)-1:
                lastmsg = subpath[-1]
                feID_list = query_dict_by_wlistvalue(self.feID_relMsgIDslist_dict, lastmsg)
                if len(feID_list) == 0:
                    dstfeID_list = query_dict_by_wlistvalue(self.feID_compID_dict, dst)
                else:
                    for element in feID_list:
                        if (element in self.secFeaturePkgID_list and dst in secnodeID_set) or (element in self.safFeature_pkg_list and dst in safnodeID_set):
                            if element not in dstfeID_list:
                                dstfeID_list.append(element)
                        else:
                            print("Warning! Mismatch in safety and security relevance of software component & feature!")
            elif index == 0 and index != len(path)-1:
                firstmsg = subpath[-1]
                feID_list = query_dict_by_wlistvalue(self.feID_relMsgIDslist_dict, firstmsg)
                if len(feID_list) == 0:
                    srcfeID_list = query_dict_by_wlistvalue(self.feID_compID_dict, src)
                else:
                    for element in feID_list:
                        if (element in self.secFeaturePkgID_list and src in secnodeID_set) or (element in self.safFeature_pkg_list and src in safnodeID_set):
                            if element not in srcfeID_list:
                                srcfeID_list.append(element)
                        else:
                            print("Warning! Mismatch in safety and security relevance of software component & feature!")
            else:
                print("Warning! uncovered/unexpected condition found! index: ", index)
        if len(srcfeID_list) != 0 and len(dstfeID_list) != 0:
            perpath_FIs_list = get_itertoolsproductoflists(srcfeID_list, dstfeID_list)
        return perpath_FIs_list
    
    
    def get_interaction_paths_by_query_graph(self, graph, graphquery_list, nodeID_name_dict, edgeID_name_dict, secnodeID_set, safnodeID_set, secsafnodeID_set, depth):
        "Query the graph using each query in the query list; filter interaction paths that exhibit a chain of interactions"
        paths_counter = 0
        query_pripathfound_list = [] #collect queries for which atleast 1 primary path was found.
        FIs_based_onRelvMsgandSWC_list = [] #store FIs derived for paths that are considered; FIs are derived based on relevant messages; in case of missing relevant messages, FIs are derived based on relevant components
        pri_plus_sec_path_counter = 0
        primary_path_count = 0
        
        for index, value in enumerate(graphquery_list):
            src = value[0]
            dst = value[1]

            if src == "EAID_8951E9DA_1663_B252_AB7A_00A899A5A0DF" and dst == "EAID_800FB2AF_2CF8_D260_9D14_7703597ADA94":
                print(src)

            if src == "EAID_BCD60E86_B55A_A9FA_A5C1_3E5E0B3365C6":
                print(3)

            if dst == "EAID_A56B23EF_2944_71C3_837B_D5E0B3E13852":
                print(3)

            if src == "EAID_BCD60E86_B55A_A9FA_A5C1_3E5E0B3365C6" and dst == "EAID_A56B23EF_2944_71C3_837B_D5E0B3E13852":
                print(3)

            current_queryID_list = [src, dst]
            for path in nx.all_simple_edge_paths(graph, source = src, target = dst, cutoff = depth): #query graph to find paths from source node to destination node
                pri_plus_sec_path_counter = pri_plus_sec_path_counter + 1
                
                path_name = self.get_path_name(path, nodeID_name_dict) #a function to get pathname for debugging/validating the path as primary (path without interaction chain) or secondary (path with interaction chain)
                Inodes_list = self.collect_Inodes_for_a_path(path) #a function to collect intermediate nodes for an interaction path whose length > 1
                
                #for a path with cutoff>1, check safety and security relevance of its intermediate nodes (Inodes); if at least one Inode is safety or security relevant, ignore the path and go to next path; If all Inodes are neither security nor safety relevant, count it as an interaction path and derive its corresponding feature interaction(s)
                if len(Inodes_list) != 0: #check safety and security relevance of Inodes of the current path whose cutoff > 1
                    Inode_rel_flag = self.check_Inodes_relevance(Inodes_list, current_queryID_list) #flag set to 0 if at least 1 safety or security relevant Inode found; flag is set to 1 if all Inodes are neither security nor safety relevant
                else: #path with no intermediate nodes is automatically considered/included in output.
                    Inode_rel_flag = 1 #path considered
                
                if len(path) != 0 and Inode_rel_flag == 1:
                    if value not in query_pripathfound_list:
                        query_pripathfound_list.append(value)
                
                if Inode_rel_flag == 0: #if the interaction path exhibits an interaction chain
                    #print("\nDebug! path_name: ", path_name, " is a path with a chain of interactions!")
                    continue #go to next path
                else: #if the interaction path is primary interaction path
                    #print("\nDebug! path_name: ", path_name, " is a path without any chain of interactions!")
                    primary_path_count = primary_path_count + 1 #count the interaction path
                    
                    ############### Retrieve FIs based on relevant messages and relevant software components##########
                    perpath_FIs_based_onRelvMsgandSWC_list = self.extract_FI_based_on_relvMsgs_and_SWC(path, src, dst, secnodeID_set, safnodeID_set, nodeID_name_dict)
                    perpath_FInames_based_onRelvMsgandSWC_list = get_listoflistnames_from_listoflistIDs(perpath_FIs_based_onRelvMsgandSWC_list, self.featurePkgID_name_dict)
                    #print("Debug! path: ", path_name, " extracted_FIs_based_on_msg_relv_and_SWC: ", len(perpath_FIs_based_onRelvMsgandSWC_list), " : ", perpath_FInames_based_onRelvMsgandSWC_list, "\n")
                    for element in perpath_FIs_based_onRelvMsgandSWC_list:
                        if element not in FIs_based_onRelvMsgandSWC_list:
                            FIs_based_onRelvMsgandSWC_list.append(element)
                
        return primary_path_count, pri_plus_sec_path_counter, FIs_based_onRelvMsgandSWC_list, query_pripathfound_list
    
    def get_nodes_edges_of_all_saf_and_sec_features(self):
        "store nodes of all safety and security features in a single data struct; do the same for edges"
        nodeIDs_set = set()
        nodeID_name_dict = {}
        edgeIDs_list = []
        edgeID_name_dict = {}
        for element in self.featurePkgID_list: #for each safety or security feature
            if element == "EAPK_B679A45A_12B9_0D90_ACEB_A15866920A8F":
                print(3)

            if element == "EAPK_88EFC992_BBF2_ADA1_BB31_0E5AB5517B59":
                print(2)

            if element == "EAPK_ADA194E9_D3F3_8734_902C_F0B4742FA06D":
                print(2)
            
            perelement_nodeIDs_set = self.feID_nodeIDset_dict[element]
            if len(perelement_nodeIDs_set) != 0:
                nodeIDs_set.update(perelement_nodeIDs_set)
            perelement_nodeID_name_dict = self.feID_nodeIDnamedict_dict[element]
            if len(perelement_nodeID_name_dict.keys()) != 0:
                nodeID_name_dict.update(perelement_nodeID_name_dict)
            perelement_edgeIDs_list = self.feID_edgeIDlist_dict[element]
            if len(perelement_edgeIDs_list) != 0:
                edgeIDs_list.extend(perelement_edgeIDs_list)
            perelement_edgeID_name_dict = self.feID_edgeIDnamedict_dict[element]
            if len(perelement_edgeID_name_dict.keys()) != 0:
                edgeID_name_dict.update(perelement_edgeID_name_dict)
        #print("\nDebug! edgeID_name_dict: ", edgeID_name_dict)
        return nodeIDs_set, nodeID_name_dict, edgeIDs_list, edgeID_name_dict
    
    def get_interaction_list(self, depth):
        "Get a list of feature interactions between safety and security features"
        safFe_interactingSecFe_list = []
        secFe_interactingSafFe_list = []
        relComponentID_name_dict = {}
        relComponentID_name_dict.update(self.secComponentID_name_dict)
        relComponentID_name_dict.update(self.safComponentID_name_dict)
        all_FInames_listsoflist = []
        allQuery_pripathfound_list = []
        allQuery_list = []
        
        #unpack the node_list, nodeID_name_labeldict, edge_list, edgeID_name_dict for all safety and security features
        nodeIDs_set, nodeID_name_dict, edgeIDs_list, edgeID_name_dict = self.get_nodes_edges_of_all_saf_and_sec_features() #data struct of all nodes and edges
        print("\nDebug! len(nodes): ", len(nodeIDs_set), " and len(edges): ", len(edgeIDs_list), " for all safety & security features!")
        
        secnodeID_set, safnodeID_set, secsafnodeID_set, nonrelnodeID_set = self.get_relevant_lifelines(nodeIDs_set) #identify safety relevant, security relevant, and both safety and security relevant lifelines
        print("\nDebug! Relevant lifelines for .sd of all saf-&sec features! secnodeID_no: ", len(secnodeID_set), ", safnodeID_no: ", len(safnodeID_set), ", secsafnodeID_no: ", len(secsafnodeID_set))
        
        print("\nCreating nx multi directed graph ...")
        featureseqdiags_graph = create_multidi_graph(nodeIDs_set, edgeIDs_list)

        for edge in edgeIDs_list:
            if edge[0] != edge[1]:
                print(nodeID_name_dict[edge[0]], " ", nodeID_name_dict[edge[1]])

        debug_list = []
        for node in secnodeID_set:
            debug_list.append(nodeID_name_dict[node])
        
        print("\nGenerating graph query list ...")
        LLcmb_SafToSec_querylist, LLcmb_SecToSaf_querylist = self.get_graphquery_list(secnodeID_set, safnodeID_set, secsafnodeID_set)
        print("\nDebug! len(LLcmb_SafToSec_querylist): ", len(LLcmb_SafToSec_querylist), " len(LLcmb_SecToSaf_querylist): ", len(LLcmb_SecToSaf_querylist))
        
        for query in LLcmb_SafToSec_querylist:
            if query not in allQuery_list:
                allQuery_list.append(query)
        for query in LLcmb_SecToSaf_querylist:
            if query not in allQuery_list:
                allQuery_list.append(query)

        # for query in allQuery_list:
        #     query_1 = query[0]
        #     query_2 = query[1]
        #     if query_1 == "EAID_8951E9DA_1663_B252_AB7A_00A899A5A0DF" and query_2 == "EAID_800FB2AF_2CF8_D260_9D14_7703597ADA94":
        #         print(nodeID_name_dict[query_1])

        # for query in LLcmb_SafToSec_querylist:
        #     query_1 = query[0]
        #     query_2 = query[1]
        #     if query_1 == "EAID_8951E9DA_1663_B252_AB7A_00A899A5A0DF" and query_2 == "EAID_800FB2AF_2CF8_D260_9D14_7703597ADA94":
        #         print(nodeID_name_dict[query_1])

        # for query in LLcmb_SecToSaf_querylist:
        #     query_1 = query[0]
        #     query_2 = query[1]
        #     if query_1 == "EAID_8951E9DA_1663_B252_AB7A_00A899A5A0DF" and query_2 == "EAID_800FB2AF_2CF8_D260_9D14_7703597ADA94":
        #         print(nodeID_name_dict[query_1])
        
        print("\nQuerying graph to get interaction paths from safety to security...")
        SafToSec_paths_counter, SafToSec_pri_plus_sec_path_counter, SafToSecFIs_based_onRelvMsgandSWC_list, querySafToSec_pripathfound_list = self.get_interaction_paths_by_query_graph(featureseqdiags_graph, LLcmb_SafToSec_querylist, nodeID_name_dict, edgeID_name_dict, secnodeID_set, safnodeID_set, secsafnodeID_set, depth)
        
        for query in querySafToSec_pripathfound_list:
            if query not in allQuery_pripathfound_list:
                allQuery_pripathfound_list.append(query)
        
        print("\nQuerying graph to get interaction paths from security to safety...")
        SecToSaf_paths_counter, SecToSaf_pri_plus_sec_path_counter, SecToSafFIs_based_onRelvMsgandSWC_list, querySecToSaf_pripathfound_list = self.get_interaction_paths_by_query_graph(featureseqdiags_graph, LLcmb_SecToSaf_querylist, nodeID_name_dict, edgeID_name_dict, secnodeID_set, safnodeID_set, secsafnodeID_set, depth)
        
        for query in querySecToSaf_pripathfound_list:
            if query not in allQuery_pripathfound_list:
                allQuery_pripathfound_list.append(query)
        
        pri_plus_sec_interac_paths = SafToSec_pri_plus_sec_path_counter + SecToSaf_pri_plus_sec_path_counter
        interaction_paths_that_passedFilter = SecToSaf_paths_counter + SafToSec_paths_counter
        
        print("Primary FI (based on relvant msg & software component (SWC)) from_safety_to_security! len(SafToSecFIs_based_onRelvMsgandSWC_list): ", len(SafToSecFIs_based_onRelvMsgandSWC_list), " are: ")
        create_table_for_interactingfeatures(get_listoflistnames_from_listoflistIDs(SafToSecFIs_based_onRelvMsgandSWC_list, self.featurePkgID_name_dict))
        
        print("Primary FI (based on relvant msg & SWC) from_security_to_safety! len(SecToSafFIs_based_onRelvMsgandSWC_list): ", len(SecToSafFIs_based_onRelvMsgandSWC_list), " are: ")
        create_table_for_interactingfeatures(get_listoflistnames_from_listoflistIDs(SecToSafFIs_based_onRelvMsgandSWC_list, self.featurePkgID_name_dict))
        
        for element in SafToSecFIs_based_onRelvMsgandSWC_list: #computes total FIs for primary paths based on relevant messages and SWCs in absence of relevant messages
            if element not in SecToSafFIs_based_onRelvMsgandSWC_list:
                SecToSafFIs_based_onRelvMsgandSWC_list.append(element)
        pri_FInames_RelvMsgandSWC_list = get_listoflistnames_from_listoflistIDs(SecToSafFIs_based_onRelvMsgandSWC_list, self.featurePkgID_name_dict)
        
        print("Summary! Queries_for_which_atleast_1_primary_path_was_found: ", len(allQuery_pripathfound_list), " out_of_total_queries: ", len(allQuery_list))
        print("Summary! Total Primary FI (based on relvant msg & SWC)! len(pri_FInames_RelvMsgandSWC_list): ", len(pri_FInames_RelvMsgandSWC_list), " pri_FInames_RelvMsgandSWC_list: ", pri_FInames_RelvMsgandSWC_list)
        create_table_for_interactingfeatures(pri_FInames_RelvMsgandSWC_list)
        
        print("\nDebug! Total_pri_and_sec_paths: ", pri_plus_sec_interac_paths, " total_pri_paths: ", interaction_paths_that_passedFilter, "\nFIs_basedonRelvMsg&SWC_due_to_pri_paths: ", len(SecToSafFIs_based_onRelvMsgandSWC_list))
        

        # print(SecToSafFIs_based_onRelvMsgandSWC_list)
        # print(SafToSecFIs_based_onRelvMsgandSWC_list)
        print("\n\n")
        # print(pri_FInames_RelvMsgandSWC_list)
        return pri_plus_sec_interac_paths, interaction_paths_that_passedFilter

def main():
    msgID_name_dict = {}
    featurePkgID_list = []
    featurePkgID_name_dict = {}
    featureID_nodeIDset_dict = {}
    featureID_nodeIDnamedict_dict = {}
    featureID_edgeIDlist_dict = {}
    featureID_edgeIDnamedict_dict = {}
    msgID_msgSort_dict = {}
    feID_relMsgIDslist_dict = {}
    feID_compID_dict = {}
    relevantComponentID_set = set() #this set will include both safety and security relevant components
    iterator_type = INPUT_FILE_IDX #search will be performed in the specified input xmi file; for our case study, its xmi input file 2
    
    print("\nGetting security features...")
    GSeF = GetSecurityFeatures(secFeaturePkgID_list)
    secFeaturePkgID_name_dict = GSeF.get_security_feature_name(iterator_type) #search will be performed in the specified input xmi file
    #print("\nsecurity_feature_list: ", secFeaturePkgID_list, "\n\nse_feature_pkg_dict: ", secFeaturePkgID_name_dict)
    
    print("\n\nGetting safety features...")
    GSaF = GetSafetyFeatures(ecu_sa_main_pkg_path)
    safFeature_pkg_list, safFeaturePkgID_name_dict = GSaF.get_safety_feature(iterator_type) #search will be performed in the specified input xmi file
    #print("\nsafety_feature_list: ", safFeature_pkg_list, "\n\nsafFeaturePkgID_name_dict: ", safFeaturePkgID_name_dict)
    
    secComponentID_set = get_values_from_dict(secFeID_compID_dict)
    safComponentID_set = get_values_from_dict(safFeID_compID_dict)
    secsafComponentID_set = get_commonelementIDsset(secComponentID_set, safComponentID_set) #getting components that are both safety and security relevant
    if len(secsafComponentID_set) != 0:
        secComponentID_set = get_uniqueelementIDsset(secComponentID_set, secsafComponentID_set)
        safComponentID_set = get_uniqueelementIDsset(safComponentID_set, secsafComponentID_set)
    print("\nlen(safComponentID_set): ", len(safComponentID_set), " len(secComponentID_set): ", len(secComponentID_set), " len(secsafComponentID_set): ", len(secsafComponentID_set))
    
    print("\nAnalyzing sequence diagrams of security features to get messages and lifelines")
    GSecSDA = GetBehavioralElements(secFeaturePkgID_list, secFeaturePkgID_name_dict, secComponentID_set, secFeID_compID_dict)
    secFeID_nodeIDset_dict, secFeID_nodeIDnamedict_dict, secFeID_edgeIDlist_dict, secFeID_edgeIDnamedict_dict, secMsgID_name_dict, secMsgID_msgSort_dict, secFeID_relMsgIDslist_dict, secFeID_msgIDnamedict_dict = GSecSDA.extract_lifelines_and_messages()
    
    print("\nAnalyzing sequence diagrams of safety features to get messages and lifelines")
    GSafSDA = GetBehavioralElements(safFeature_pkg_list, safFeaturePkgID_name_dict, safComponentID_set, safFeID_compID_dict)
    safFeID_nodeIDset_dict, safFeID_nodeIDnamedict_dict, safFeID_edgeIDlist_dict, safFeID_edgeIDnamedict_dict, safMsgID_name_dict, safMsgID_msgSort_dict, safFeID_relMsgIDslist_dict, safFeID_msgIDnamedict_dict = GSafSDA.extract_lifelines_and_messages()
    
    msgID_name_dict.update(secMsgID_name_dict)
    msgID_name_dict.update(safMsgID_name_dict)
    
    featurePkgID_list.extend(secFeaturePkgID_list)
    featurePkgID_list.extend(safFeature_pkg_list)
    featurePkgID_name_dict.update(secFeaturePkgID_name_dict)
    featurePkgID_name_dict.update(safFeaturePkgID_name_dict)
    featureID_nodeIDset_dict.update(secFeID_nodeIDset_dict)
    featureID_nodeIDset_dict.update(safFeID_nodeIDset_dict)
    featureID_nodeIDnamedict_dict.update(secFeID_nodeIDnamedict_dict)
    featureID_nodeIDnamedict_dict.update(safFeID_nodeIDnamedict_dict)
    featureID_edgeIDlist_dict.update(secFeID_edgeIDlist_dict)
    featureID_edgeIDlist_dict.update(safFeID_edgeIDlist_dict)
    featureID_edgeIDnamedict_dict.update(secFeID_edgeIDnamedict_dict)
    featureID_edgeIDnamedict_dict.update(safFeID_edgeIDnamedict_dict)
    msgID_msgSort_dict.update(safMsgID_msgSort_dict)
    msgID_msgSort_dict.update(secMsgID_msgSort_dict)
    feID_relMsgIDslist_dict.update(safFeID_relMsgIDslist_dict)
    feID_relMsgIDslist_dict.update(secFeID_relMsgIDslist_dict)
    feID_compID_dict.update(secFeID_compID_dict)
    feID_compID_dict.update(safFeID_compID_dict)
    relevantComponentID_set.update(secComponentID_set)
    relevantComponentID_set.update(safComponentID_set)
    
    depth = SEARCH_DEPTH #cutoff for edge path search
    
    print("Performing interaction analysis of security and safety features")
    GINA = InteractionAnalysis(featurePkgID_list, featurePkgID_name_dict, secComponentID_set, safComponentID_set, secsafComponentID_set, featureID_nodeIDset_dict, featureID_nodeIDnamedict_dict, featureID_edgeIDlist_dict, featureID_edgeIDnamedict_dict, secFeID_compID_dict, safFeID_compID_dict, msgID_name_dict, secComponentID_name_dict, safComponentID_name_dict, msgID_msgSort_dict, feID_relMsgIDslist_dict, feID_compID_dict, secFeaturePkgID_list, safFeature_pkg_list, relevantComponentID_set)
    pri_plus_sec_interac_paths, interaction_paths_that_passedFilter = GINA.get_interaction_list(depth)
    
    stop = timeit.default_timer()
    print('Time: ', stop - start)

    return pri_plus_sec_interac_paths, interaction_paths_that_passedFilter

def run_i_fasst():
    return main()

if __name__ == "__main__":
    main()