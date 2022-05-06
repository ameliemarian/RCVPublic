import sys
sys.path.append('../src')
import make_tree
import ballot
import helpers
import numpy as np
import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'
import csv
import signal
import ast


def timeout_handler(signum, frame):   # Custom signal handler
    raise Exception("Contest timed out")


def compute(file,num_cands,spots,missing,DP=True,remove_cands = []):

    ballotset = ballot.BallotSet(num_cands) #numcands: 14 NYC or 7 SF or 5 fake
    data = helpers.load_data_NYC(file,spots,remove_cands) #spots: 5 NYC (always) or 7 SF or 5 fake
    #for nyc mayoral: [221458, 218922, 218117, 221141, 217654]
    #data = random.sample(data, 100000)


    for bal in data:
        bal = np.array(bal)
        ballotset.add_ballot(bal)
        
    t = make_tree.MakeTree(missing,ballotset)

    runtime = -1
    if DP:
        runtime = t.get_tree(all_bound=False)
    else:
        runtime = t.brute_force()

    num_possible_winners = len(t.min_bound)

    min_names = {}
    for cand in t.min_bound:
        min_names[helpers.lookup_NYC(cand)] = t.min_bound[cand]
    del t
    del ballotset
    return (num_possible_winners, min_names, runtime)


signal.signal(signal.SIGALRM, timeout_handler)

with open('elections.csv','r') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    writer = csv.writer(open('results.csv','w'),delimiter=',')

    writer.writerow(csv_reader.fieldnames)
    
    for row in csv_reader:
        file = "../data/{0}.json".format(row["Contest/District"])

        try:
            missing = int(row["Missing Ballots"])
        except ValueError:
            break
        remove_cands = []
        if row["Removed reduction candidates"]:
            remove_cands = ast.literal_eval(row["Removed reduction candidates"])

        num_cands = int(row["Candidates"]) - len(remove_cands)

        spots = min(5,num_cands)

        for use_dp in (False,True):
            #2 hour timeout for each test
            signal.alarm(7200)
            try:
                num_possible_winners, min_names, runtime = compute(file,num_cands,spots,missing,use_dp,remove_cands)
            except Exception:
                runtime="timeout"
                num_possible_winners=""
                min_names=""
            else:
                signal.alarm(0)

            #add data to CSV
            if use_dp:
                row["DP Time (S)"] = runtime
                row["Possible Winners"] = num_possible_winners
                row["Min Bound"] = min_names
            else:
                row["Brute Force Time (S)"] = runtime

        writer.writerow(row.values())
        csv_file.flush()
        print(row["Contest/District"], num_possible_winners, min_names, row["DP Time (S)"], row["Brute Force Time (S)"])