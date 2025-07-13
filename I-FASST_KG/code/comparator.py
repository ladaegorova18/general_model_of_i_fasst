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

start = timeit.default_timer()
    
# ------------- I-FASST for knowledge graphs --------------------
i_fasst_kg = I_FASST_KG(INPUTFILE_2, TESTDB_2)
kg_filtered_paths = i_fasst_kg.start()

stop = timeit.default_timer()
print('Time for KG: ', stop - start)

i_fasst_kg.print_interaction_paths()


# ------------- I-FASST for XML file --------------------
# pri_plus_sec_interac_paths, interaction_paths_that_passedFilter = run_i_fasst()