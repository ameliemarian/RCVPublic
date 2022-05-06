import sys
sys.path.append('../src')
import make_tree
import ballot
import helpers
import numpy as np
import pickle

def save_tree(fname: str, missing: int):
    file = "../data/NYC_DEM_MAYOR_ELE.json"
    global ballot

    ballotset = ballot.BallotSet(14)
    data = helpers.load_data_NYC(file, 5) 

    for ballot in data:
        ballot = np.array(ballot)
        ballotset.add_ballot(ballot)

    t = make_tree.MakeTree(missing,ballotset)
    t.get_tree()

    for node in t.tree.all_nodes():
        if node.tag!="Root":
            node.tag = helpers.lookup_NYC(int(node.tag))

    pickle.dump(t.tree, open(fname, "wb" ))

    print("dumped pickle!")

def open_tree(fname: str):

    t = pickle.load( open(fname, "rb" ) )
    t.show(line_type="ascii-em")


save_tree("NYC.p",0)
