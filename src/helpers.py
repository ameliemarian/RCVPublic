import os
import re
import json 
import pandas as pd
import numpy as np
import progressbar


ProgressBar = progressbar.NullBar

'''
Given path to raw Cast Vote Record json files folder and
contest id (check ContestManifest.json), merge_SF() will extract marks for 
that voter and save them all in 1 json file. New JSON data follows
format below:

    {
    "votes": [
        {
            "ManifestationId": ####,
            "Marks": [
                {
                    *****
                    Copied from CVR json
                    *****
                },
                ...
            ]
        },
        ...
        ]
    }
'''

#merges all json files for SanFrancisco into 1 large one
def merge_SF(path = '../data/sanfran_data_raw/data', fname = "SF_D1.json", id = 15): #id of 15 is for BOARD OF SUPERVISORS DISTRICT 7 contest, 12-17 for all districts
    write_in_ids = [126, 128, 123, 127, 125, 131, 122, 129, 130, 132, 124]
    progress = ProgressBar()
    rgx = re.compile('CvrExport_.*\.json')

    voter_data = {"votes": []}

    for file in progress(os.listdir(path)):
        if rgx.match(file):
            with open(os.path.join(path,file)) as f:
                data = json.load(f)
                for session in data["Sessions"]:
                    for contest in session["Original"]["Cards"]:
                        for l in contest["Contests"]:
                            if l["Id"] == id: 
                                tmp = {}
                                tmp["ManifestationId"] = l["ManifestationId"]
                                new_marks = []
                                for cands in l["Marks"]:
                                    if cands["CandidateId"] not in write_in_ids:
                                        new_marks.append(cands)
                                tmp["Marks"] = new_marks
                                voter_data["votes"].append(tmp)
                f.close()

    with open(fname, 'w', encoding='utf-8') as file:
        json.dump(voter_data, file, ensure_ascii=False, indent=4,sort_keys=False)
    print("Merging Done!")


#merges all NYC csv (manually convert excel to csv) files into 1 large json
#for given contest regex (column)
def merge_NYC(path = '../data/nyc_data_raw/data', fname = "NYC_DEM_MAYOR.json", column = r"DEM Mayor Choice"):

    progress = ProgressBar()

    rgx = re.compile('2021.*\.csv')
    rgx_col = re.compile(column)
    voter_data = {"votes": []}

    for file in progress(os.listdir(path)):
        if rgx.match(file):
            print(file)

            df = pd.read_csv(os.path.join(path, file))

            for index, row in df.iterrows():
                ballot = []
                for key in row.keys():
                    if rgx_col.match(key):
                        ballot.append(row[key])
                if ballot:
                    voter_data["votes"].append(ballot)
                else:
                    #data for this contest not in this file
                    break



    with open(fname, 'w', encoding='utf-8') as file:
        json.dump(voter_data, file, ensure_ascii=False, indent=4,sort_keys=False)
    print("Merging Done!")



def merge_NYC_abs(path = '../data/nyc_data_raw/data', columns = r"DEM Mayor Choice"):

    progress = ProgressBar()

    rgx = re.compile('2021.*\.csv')
    rgx_col = re.compile(columns)
    count = 0
    for file in progress(os.listdir(path)):
        if rgx.match(file):

            df = pd.read_csv(os.path.join(path, file))

            for _, row in df.iterrows():
                ballot = []
                for key in row.keys():
                    if rgx_col.match(key):
                        ballot.append(row[key])
                if ballot:
                    if ballot[0]!="undervote":
                        count+=1
                else:
                    #data for this contest not in this file
                    break

    print("Counted Absentee:",count)



#merges raw nyc data for some contest into a json of precinct frequencies for that contest

def NYC_precinct_count(path = '../data/nyc_data_raw/data', fname = "precints.json", column = r"DEM Mayor Choice",party='DEM'):

    progress = ProgressBar()

    rgx = re.compile('2021.*\.csv')
    rgx_col = re.compile(column)
    count = 0
    precincts = {}
    if party == "DEM":
        party = "REP"
    elif party == "REP":
        party = "DEM"
    for file in progress(os.listdir(path)):
        if rgx.match(file):
            print(file)

            df = pd.read_csv(os.path.join(path, file))

            seen = False
            for index, row in df.iterrows():

                incremented = False
                for key in row.keys():
                    if rgx_col.match(key):
                        seen = True
                        if row[key] == "undervote":
                            continue
                        count+=1
                        if row["Precinct"] in precincts:
                            precincts[row["Precinct"]]+=1
                        else:
                            precincts[row["Precinct"]]=1
                        incremented = True
                        break
                
                if incremented:
                    for key in row.keys():
                        if key.find(party) != -1 and row[key] != "undervote":
                            precincts[row["Precinct"]]-=1
                            count-=1
                            break
                
                if not seen:
                    break
                


    with open(fname, 'w', encoding='utf-8') as file:
        json.dump(precincts, file, ensure_ascii=False, indent=4,sort_keys=False)
    print("Merging Done for ", count, " ballots")

#total number of ballots in folder for some contest specified in `column`
def get_count_NYC(path = '../data/nyc_data_raw/data',column = r"DEM Mayor Choice"):

    progress = ProgressBar()
    rgx = re.compile('2021.*\.csv')
    rgx_col = re.compile(column)

    ballots = 0

    for file in progress(os.listdir(path)):
        if rgx.match(file):
            df = pd.read_csv(os.path.join(path, file))
            ballots+=len(df.index)

    return ballots



'''
Given a candidate ID, will return the candidates name
from CandidateManifest.json
'''


seen_names_sf = {}

def lookup_SF(cid, path = "../data/sanfran_data_raw/CandidateManifest.json"):


    if cid in seen_names_sf:
        return seen_names_sf[cid]

    with open(path) as f:
        data = json.load(f)
        for cands in data["List"]:
            if cands["Id"] == cid:
                f.close()
                seen_names_sf[cid] = cands["Description"]
                return cands["Description"]
        f.close()
        return None


seen_names_nyc = {}

def lookup_NYC(cid, path = "../data/nyc_data_raw/2021P_CandidacyID_To_Name.xlsx"):
    if not isinstance(cid, int):
        return cid

    if cid in seen_names_nyc:
        return seen_names_nyc[cid]

    df = pd.read_excel(path,sheet_name=None,engine='openpyxl')

    row = df["Sheet1"].loc[df["Sheet1"]["CandidacyID"] == cid]
    if not row.empty:
        seen_names_nyc[cid] = row["DefaultBallotName"].item()
        return row["DefaultBallotName"].item()
    if cid == 0:
        return "Write-in"
    return None

def lookup_mock(cid):
    if not isinstance(cid, int):
        return cid


    return chr(cid+64)


def load_data_SF(path: str, numRanks: int, reducedEP = None):
    
    progress = ProgressBar()
    with open(path) as f:
        data = json.load(f)
        all_votes = []

        round = 0
        for vote in progress(data["votes"]):
            round+=1
            ballot = []

            vote["Marks"] = sorted(vote["Marks"], key=lambda k: k['Rank'])
            for rank in range(numRanks):
                rank = rank+1
                seen = 0
                for mark in vote["Marks"]:
                    if mark["Rank"]==rank and mark["IsVote"] and mark["CandidateId"] not in ballot:
                        seen+=1
                
                if seen == 1:
                    for mark in vote["Marks"]:
                        if mark["Rank"]==rank and mark["IsVote"] and mark["CandidateId"] not in ballot:
                            if reducedEP:
                                if mark["CandidateId"] not in reducedEP:
                                    ballot.append(mark["CandidateId"])
                            else:
                                ballot.append(mark["CandidateId"])
                else:
                    break

            
            if ballot:
                all_votes.append(ballot)
        
        f.close()
    return all_votes
    
#recuedEP 0 is for write-in
def load_data_NYC(path: str, numRanks: int, reducedEP = None):
    progress = ProgressBar()

    with open(path) as f:
        data = json.load(f)
        all_votes = []

        for vote in progress(data["votes"]):
            seen_candidates = set()
            ballot = []

            for mark in vote:
                if mark == "undervote":
                    continue
                if mark == "overvote":
                    break
                if mark=="Write-in":
                    continue #skip write-in for now
                    #0 is the candidate id for a write-in
                    mark = 0
                if mark in seen_candidates:
                    continue

                seen_candidates.add(mark)
                if reducedEP:
                    if int(mark) not in reducedEP:
                        ballot.append(int(mark))
                else:
                    ballot.append(int(mark))


            #all ballots should be added regardless
            if ballot:
                all_votes.append(ballot)
        
        f.close()
    return all_votes

