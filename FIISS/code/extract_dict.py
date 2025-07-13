import lxml.etree as etree
import networkx as nx
import os

ns = {
    'uml':'http://schema.omg.org/spec/UML/2.1',
    'xmi':'http://schema.omg.org/spec/XMI/2.1',
    'SysML':'http://www.omg.org/spec/SysML/20120322/SysML',
    'sysml':'http://www.omg.org/spec/SysML/20080501/SysML-profile'
    }

file_name = "inputfile2.xml"

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
ecu_sa_main_pkg_path = ".//packagedElement[@xmi:id='{}'][@xmi:type='uml:Package']/packagedElement[@xmi:type='uml:Package']".format('EAPK_511FDC72_60D2_413c_B488_D6CAE1507040')

dirname = os.path.dirname(__file__)
#Relative path of input xml files to be parsed
file_path_inputfile = os.path.join(dirname, '..', 'data', file_name)

tree = etree.parse(file_path_inputfile)
root = tree.getroot()

other_root_id = 'EAPK_F7282E3A_E460_4a55_813A_FA109AA4BB0E'
safety_root_id = "EAPK_511FDC72_60D2_413c_B488_D6CAE1507040"
security_root_id = "EAPK_A4E14F79_C0CB_4e3a_8A7A_ACB1EB7362C4"

# we leave elements of type uml:Collaboration and uml:Interaction as separate nodes (not sure we need them for analysis)
ecu_safety_main_pkg_path = ".//packagedElement[@xmi:id='{}']".format(safety_root_id) # safety root id
ecu_security_main_pkg_path = ".//packagedElement[@xmi:id='{}']".format(security_root_id) # security root id

def get_root_element(root_path):
    element_iter = root.iterfind(path=root_path, namespaces=ns)
    root_element = None
    for element in element_iter:
        root_element = element # we have the root element now
    return root_element
        
def extract_ancestors(path, sf_dict):
# Find all ancestors of the root and add them to the list
    temp_root = get_root_element(path)
    CURR_PACKAGE = ""

    for element in temp_root.iter():
        type = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}type')
        id = element.attrib.get('{http://schema.omg.org/spec/XMI/2.1}id')
        if type == "uml:Package":
            CURR_PACKAGE = id
            if not CURR_PACKAGE in sf_dict and CURR_PACKAGE != "":
                sf_dict[id] = []
        elif type == "uml:Component":
            sf_dict[CURR_PACKAGE].append(id)
             

sa_mapping_dict = dict()
se_mapping_dict = dict()

extract_ancestors(ecu_safety_main_pkg_path, sa_mapping_dict)
extract_ancestors(ecu_security_main_pkg_path, se_mapping_dict)

print("Safety mapping")
print(sa_mapping_dict)

print("Security mapping")
print(se_mapping_dict)