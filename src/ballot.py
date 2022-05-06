import math
import random
import numpy as np
import copy

'''
each ballot is a tuple of candidate ID's in order of rank:
(13, 24, 12, 45, 43, 52, 32)

'''
class BallotSet():
    
    def __init__(self, numCands): #max number of candidates allowed on each ballot
        self.ballots = {} #a dict of tuple keys that are ballots and frequency values
        self.numCands = numCands #number of candidates
        self.candidates = set() #set of candidate id's
        self.current_idx = {} #current active candidate index for each tuple key
        self.artificial_bals = [] #a list of tuples that are generated as missing ballots
        self.artificial_idx = [] #current active candidate index for each missing ballot
        self.in_pool = [] #missing ballots (by index) currently available to be assigned a new candidate
        self.active_cands = [] #candidates still in the election
        self.missing = 0 #number of remaining missing ballots
        self.upper_bound = {} #current absantee ballots allocated for each candidate

    def __deepcopy__(self, memo):
        ballotset = BallotSet(self.numCands)

        ballotset.ballots = self.ballots
        ballotset.candidates = self.candidates.copy()
        ballotset.current_idx = self.current_idx.copy()
        ballotset.artificial_bals = self.artificial_bals.copy()
        ballotset.artificial_idx = self.artificial_idx.copy()
        ballotset.in_pool = self.in_pool.copy()
        ballotset.active_cands = self.active_cands.copy()
        ballotset.missing = self.missing

        return ballotset

    '''
    If any duplicates are found, add_ballots will automatically trim the array to end at the duplicate
    '''
    
    def add_ballot(self,ballot: np.array):
        for mark in ballot:
            if mark not in self.candidates:
                self.candidates.add(mark)

        if ballot.size > self.numCands:
            ballot = ballot[:self.numCands]

        seen = []
        for idx, vote in np.ndenumerate(ballot):
            if vote in seen:
                ballot = ballot[: idx]
                break
            seen.append(vote)

        tpl = tuple(ballot)
        if tpl in self.ballots:
            self.ballots[tpl]+=1

        else:
            self.ballots[tpl]=1
            self.current_idx[tpl] = 0
        

    def reset(self):
        for key in self.current_idx:
            self.current_idx[key] = 0
        self.artificial_bals.clear()
        self.artificial_idx.clear()
        self.in_pool.clear()
        #self.upper_bound = {}

    def soft_reset(self):
        
        self.active_cands = list(self.candidates)
        
        for key in self.current_idx:
            self.current_idx[key] = 0

        for key in self.artificial_idx:
            self.artificial_idx[key] = 0

        for key in self.in_pool:
            self.in_pool[key] = False



