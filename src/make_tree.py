from treelib import Node, Tree
import progressbar
import time
import networkx as nx
import copy
import hashlib 
import ballot
from typing import List
import os, psutil
import itertools

ProgressBar = progressbar.NullBar

class MakeTree:
    def __init__(self, missing: int, ballot_set: ballot.BallotSet):
        self.missing = missing #number of missing ballots
        #print("Number of Ballots: ",sum(ballot_set.ballots.values()))
        self.ballot_set = copy.deepcopy(ballot_set) #populated BallotSet object
        #print("Number of Candidates: ",len(self.ballot_set.candidates))
        self.ballot_set.active_cands = self.ballot_set.candidates.copy()
        self.seen_configs = {}
        self.min_bound = {}
        self.bound_test = {}
        
        for _ in range(missing):
            self.ballot_set.artificial_bals.append(tuple())
            self.ballot_set.in_pool.append(True)
            self.ballot_set.artificial_idx.append(0)

        self.tree = Tree()
        
    
    def _reset(self):
        self.ballot_set.reset()
        for _ in range(self.missing):
            self.ballot_set.artificial_bals.append(tuple())
            self.ballot_set.in_pool.append(True)
            self.ballot_set.artificial_idx.append(0)
        self.ballot_set.active_cands = self.ballot_set.candidates.copy()

    def brute_force(self,all_bound = False):
        process = psutil.Process(os.getpid())
        s = time.time()
        
        permutations = list(itertools.permutations(self.ballot_set.candidates))
        
        #print("Computing ", len(permutations), " permutations")
        progress = ProgressBar()
        elim_orders = []
        for p in progress(permutations):
            root = self.tree.get_node("root")
            ballot_set = copy.deepcopy(self.ballot_set)
            ballot_set.missing = self.missing
            if self._verify(p, ballot_set):
                elim_orders.append(p)
                if int(p[-1]) in self.min_bound:
                        self.min_bound[int(p[-1])] = min(self._get_bound(p, copy.deepcopy(ballot_set)), self.min_bound[int(p[-1])])
                else:
                    self.min_bound[int(p[-1])] = self._get_bound(p, copy.deepcopy(ballot_set))

                if len(p) == self.ballot_set.numCands and all_bound == True:
                    self.bound_test[str(p)] = self._get_bound(p, copy.deepcopy(ballot_set))
            del ballot_set

        self.lists_to_tree(elim_orders)
        
        e = time.time()
        #print(process.memory_info().peak_wset/(1024 ** 2), " Peak MB of RAM used")
        #print("Took: ", "%.3f" % (e-s), " seconds")
        return ("%.3f" % (e-s))


    def lists_to_tree(self,elim_orders):
        root = self.tree.create_node("Root","root")

        for elim in elim_orders:
            ptr = root
            
            for c in elim:
                exists = False
                for childs in self.tree.children(ptr.identifier):
                    if int(c) == int(childs.tag):
                        ptr = childs
                        exists = True
                        break
                if not exists:
                    ptr = self.tree.create_node(str(c),parent=ptr.identifier)


                

    def get_tree(self, all_bound = False):
        process = psutil.Process(os.getpid())
        s = time.time()
        root = self.tree.create_node("Root","root")
        self._make_tree(0,root,self.ballot_set.candidates.copy(), get_all_bound = all_bound)
        e = time.time()
        #print(process.memory_info().peak_wset/(1024 ** 2), " Peak MB of RAM used")
        #print("Took: ", "%.3f" % (e-s), " seconds")
        return ("%.3f" % (e-s))

    #skip middle initials
    #problematic if multiple same initials exist
    def get_initials(self,name):
        initials = ""
        initials+=name.split()[0][0]
        initials+=name.split()[-1][0]
        return initials

    def tree2graph(self,compress=True, initials = True):
        s = time.time()
        
        G = nx.DiGraph()
        labeldict = {}

            
        #populate currently empty graph with subtrees that are shared
        #make id for root of each subtree the MD5 hash of its json string

        for node in self.tree.all_nodes():
        
            if compress:
                parent = hashlib.md5(self.tree.subtree(node.identifier).to_json().encode()).hexdigest()
            else:
                parent = node.identifier

            

            if initials:
                labeldict[parent] = self.get_initials(node.tag)
            else:
                labeldict[parent] = node.tag
                

            if parent not in G:
                G.add_node(parent)

            for id in self.tree.get_node(node.identifier).successors(self.tree.identifier):
                if compress:
                    subt = hashlib.md5(self.tree.subtree(id).to_json().encode()).hexdigest()
                else:
                    subt = id
                if subt not in G:
                    G.add_node(subt)

                if node.data is not None:
                    G.add_edge(parent, subt,weight=node.data)
                else:
                    if subt not in G.neighbors(parent):
                            G.add_edge(parent, subt)

        e = time.time()
        #print("Took: ", e-s)
        return (G,labeldict)



    def _make_tree(self, level: int, node: Node, cands: List[int], get_all_bound = False):

        key_hash = hashlib.md5(str(self._get_path(node)).encode()).hexdigest()

        #elections over, return
        if level >= self.ballot_set.numCands:
            
            if key_hash in self.seen_configs:
                del self.seen_configs[key_hash]
            

            return


        
        #iterate through remaining candidates and see which ones can be eliminated
        for c in cands:
            #reset missing ballot states when exploring which canidate to eliminate in current round
            #self._reset()
            
            n = self.tree.create_node(str(c),parent=node.identifier)
            #ballot_set.active_cands = self.ballot_set.candidates.copy()
            
            elim_order = self._get_path(n)
            copy_elim = elim_order.copy()
            
            path_hash = hashlib.md5(str(elim_order).encode()).hexdigest()
            

            if key_hash in self.seen_configs:
                ballot_set = copy.deepcopy(self.seen_configs[key_hash])
                single = elim_order[-1]
                elim_order.clear()
                elim_order.append(single)
            else:
                ballot_set = copy.deepcopy(self.ballot_set)
                ballot_set.missing = self.missing

            
            if self._verify(elim_order, ballot_set):
                self.seen_configs[path_hash] = copy.deepcopy(ballot_set)
                new_cands = cands.copy()
                new_cands.remove(c)


                #for getting bound ballots for winning candidate
                
                if level == self.ballot_set.numCands-1:
                    
                    if int(c) in self.min_bound:
                        self.min_bound[int(c)] = min(self._get_bound(copy_elim, copy.deepcopy(ballot_set)), self.min_bound[int(c)])
                    else:
                        self.min_bound[int(c)] = self._get_bound(copy_elim, copy.deepcopy(ballot_set))

                    if len(copy_elim) == self.ballot_set.numCands and get_all_bound == True:
                        self.bound_test[str(copy_elim)] = self._get_bound(copy_elim, copy.deepcopy(ballot_set))
                    self.tree.parent(n.identifier).data = self.min_bound[int(c)]
                    

                self._make_tree(level+1,n,new_cands,get_all_bound=get_all_bound)

            else:
                #self.seen_configs[path_hash] = copy.deepcopy(ballot_set)

                self.tree.remove_node(n.identifier)
        
        if key_hash in self.seen_configs:
            del self.seen_configs[key_hash]
    
    #Returns minimum number of missing ballots that must be bound for the winner of an elimination order
    #this is essentially load balancing
    def _get_bound(self, elim_order, ballot_set: ballot.BallotSet):
        bound = 0
        ballot_set.soft_reset()
        empty = self._get_empty_unbound(ballot_set)
        winner = elim_order[-1]
        for x in range(len(elim_order)-1):
            rankings = self._get_rankings(ballot_set)
            c2 = rankings[min(rankings,key=rankings.get)]
            del rankings[min(rankings,key=rankings.get)]
            c1 = rankings[min(rankings,key=rankings.get)]
            spots = c1-c2-1
            empty-=spots
            self._redistribute(elim_order[x],ballot_set)

        
        if empty>0:
            bound+=(empty//len(elim_order) + empty%len(elim_order))
        


        for ballot in ballot_set.artificial_bals:
            try:
                if winner in ballot:
                    bound+=1

            except (KeyError, IndexError) as e:
                pass
        return bound


    #get number of unexpressed missing ballots in ballotset
    def _get_empty_unbound(self,ballot_set: ballot.BallotSet):
        empty = 0
        for ballot in ballot_set.artificial_bals:
            try:
                if not ballot:
                    empty+=1

            except (KeyError, IndexError) as e:
                pass
        return empty

    #return tally count for a candidate in a ballotset
    def _tally_count(self,c: int, ballot_set: ballot.BallotSet):
        tally = 0
        for ballot in ballot_set.ballots:
            #tally new vote for real ballots
            try:
                if c == ballot[ballot_set.current_idx[ballot]-1]:
                    tally+=ballot_set.ballots[ballot]
            except IndexError:
                pass

        for idx, ballot in enumerate(ballot_set.artificial_bals):
        
            #tally new vote for artificial ballots
            try:
                if c == ballot[ballot_set.artificial_idx[idx]-1]:
                    tally+=1
            except (KeyError, IndexError) as e:
                pass
        
        return tally

    #given an elimination order and number of missing ballots, will decide wether elimination order is possible
    def _verify(self, elim_order: List[int],ballot_set: ballot.BallotSet):
        
        self._reset()
        #ballot_set.upper_bound = {}

        for candidate in elim_order:
            ranks = self._get_rankings(ballot_set)
            ranked_below = []
            currentRank = ranks[candidate]
            for c in ranks:
                if currentRank >= ranks[c]:
                    ranked_below.append(c)
            
            ranked_below.remove(candidate)
            for r in ranked_below:
                z = ranks[candidate] - ranks[r] + 1
                done = self._add_ballots(r,z,ballot_set) #add z ballots to candidate r from pool of missing ballots
                
                #not enough artifical ballots to bring r to rank above candidate
                if done != z:

                    return False

                ballot_set.missing -= done
                if ballot_set.missing < 0:
                    ballot_set.missing = 0
                    return False
            
            ballot_set.missing+= self._redistribute(candidate,ballot_set)
            del ranks[candidate]

        return True
    


    def _get_path(self, node: Node):
        path = []
        path.append(node.tag)
        while self.tree.parent(node.identifier):
            path.append(self.tree.parent(node.identifier).tag)
            node = self.tree.parent(node.identifier)
        path.reverse()

        path.remove("Root") #this is the root node
        path = list(map(int, path))
        return path


    # returns dict of rankings for current ballotset
    def _get_rankings(self,ballot_set: ballot.BallotSet):
        round_votes = {}

        for candidate in ballot_set.active_cands:
            round_votes[candidate] = 0
        
        for ballot in ballot_set.ballots:
        
            #tally new vote for real ballots
            try:
                round_votes[ballot[ballot_set.current_idx[ballot]]] += ballot_set.ballots[ballot]
            except IndexError:
                pass

        for idx, ballot in enumerate(ballot_set.artificial_bals):
        
            #tally new vote for artificial ballots
            try:
                round_votes[ballot[ballot_set.artificial_idx[idx]-1]] += 1
            except (KeyError, IndexError) as e:
                pass
        round_votes = dict(sorted(round_votes.items(), key=lambda item: item[1]))

        return round_votes

    #add bal_count marks for given candidate to unbound ballots
    def _add_ballots(self, candidate: int, bal_count: int,ballot_set: ballot.BallotSet):
        done = 0

        '''
        if candidate not in ballot_set.upper_bound:
            ballot_set.upper_bound[candidate] = 0

        
        #check if bal_count is within upper bound
        if (bal_count+ballot_set.upper_bound[candidate]) > self.missing*0.6:
            return done
        '''


        #ensure atomicity of adding bal_count marks
        if sum(ballot_set.in_pool) < bal_count:
            return done
        

        for idx, ballot in enumerate(ballot_set.artificial_bals):
            if done >= bal_count:
                break

            if ballot_set.in_pool[idx]:
                tmp = list(ballot)
                tmp.append(candidate)
                ballot_set.artificial_bals[idx] = tuple(tmp)
                ballot_set.in_pool[idx] = False
                done+=1

        #ballot_set.upper_bound[candidate] += done
        
        return done


    # eliminate candidate, and redistribute ballots for candidate
    def _redistribute(self, candidate: int, ballot_set: ballot.BallotSet):

        ret_ballots = 0
        
        ballot_set.active_cands.remove(candidate)
        for idx, ballot in enumerate(ballot_set.artificial_bals):
            if len(ballot) > ballot_set.artificial_idx[idx]:
                if ballot[ballot_set.artificial_idx[idx]] == candidate:
                    ballot_set.artificial_idx[idx]+=1
                    ballot_set.in_pool[idx] = True
                    ret_ballots+=1

        
        for ballot in ballot_set.ballots:
            while True:
                try:
                    if ballot[ballot_set.current_idx[ballot]] not in ballot_set.active_cands:
                        ballot_set.current_idx[ballot]+=1
                        continue
                except IndexError:
                    pass
                break
        return ret_ballots