# General model of I-FASST tool

This work was done during the intenship "Joint analysis of safety and security: identifying interactions between safety and security, from model level to language level".

The work is dedicated to the analysis of safety and security and its implementation using a general data representation model. Knowledge graphs were chosen as a possible option, and test scenarios were developed. Then, the graph was used for research on possible runtime verification applications.

## Conversion of an XML file to a knowledge graph
To run the conversion, you have to download Neo4j Desktop database or use an online version (this one was not tested).

Use the script FIISS/converter.py with your XML file created in Enterprise Architect and, if you connected to a database correctly (update the credentials according to your DB login and password), you will obtain a knowledge graph there.

## Comparison of two models

Before comparison make sure you have:
- a KG of your model (or uncomment line 381 in I_FASST_KG/code/I_FASST_for_KG.py to run conversion first)
- an XML file of a diagram (without it you will not be able to obtain a KG, refer to the previous section)

Run the script I_FASST_KG/comparator.py to compare I_FASST based on KG and I_FASST based on XML file. 

## Runtime scenarios 

There are three scripts with possible runtime verification scenarios in the folder I_FASST_KG/code:
- runtime_maintainer.py (Scenario 1 in the report)
- runtime_scenario_2.py (Scenario 2 in the report)
- logs_i_fasst.py (Logs scenario 1 in the report)

There are also two scripts with possible logs scenarios in the folder FIISS/code:
- logs_scenario_1.py
- logs_scenario_2.py

The main file for experimentations is safsecfi/I_FASST/data/inputfile1.xml
