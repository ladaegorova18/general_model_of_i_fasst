import lxml.etree as etree
import networkx as nx
import os

from py2neo import Graph, Node, Relationship

ns = {
    'uml':'http://schema.omg.org/spec/UML/2.1',
    'xmi':'http://schema.omg.org/spec/XMI/2.1',
    'SysML':'http://www.omg.org/spec/SysML/20120322/SysML',
    'sysml':'http://www.omg.org/spec/SysML/20080501/SysML-profile'
    }

# Create a graph object
graph = Graph("bolt://localhost:7687", name="testdb", auth=("neo4j", "neo4jneo4j"))

dirname = os.path.dirname(__file__)
#Relative path of input xml files to be parsed
file_path_inputfile1 = os.path.join(dirname, '..', 'data', 'inputfile1.xml')

tree = etree.parse(file_path_inputfile1)
root = tree.getroot()