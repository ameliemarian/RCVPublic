import sys
sys.path.append('../src')
import make_tree
import ballot
import pydot
import helpers
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'
from distinctipy import distinctipy
import math

file = "../data/NY_dem_city_council_16.json"
num_cands = 4
missing = 2508
compress_graph = True
remove = []

spots = min(5,num_cands)

num_cands -= len(remove)
ballotset = ballot.BallotSet(num_cands)
data = helpers.load_data_NYC(file,spots,remove) #spots: 5 NYC (always) or 7 SF or 5 fake


for ballot in data:
    ballot = np.array(ballot)
    ballotset.add_ballot(ballot)
    
t = make_tree.MakeTree(missing,ballotset)


#t.brute_force()
print(t.get_tree(all_bound=False))

print("Number of Possible Winner: ", len(t.min_bound))
min_names = {}
for cand in t.min_bound:
    min_names[helpers.lookup_NYC(cand)] = t.min_bound[cand]

print("Minimum Bound: ", min_names)

#dont need this for sample ballots since no names exist
candidates = {}
local_lookup = {}
for node in t.tree.all_nodes():
    if node.tag!="Root":
        if int(node.tag) in local_lookup:
            node.tag = local_lookup[int(node.tag)]
        else:
            #local_lookup[int(node.tag)] = t.get_initials(helpers.lookup_NYC(int(node.tag)).replace(" ","\n"))
            local_lookup[int(node.tag)] = helpers.lookup_NYC(int(node.tag)).replace(" ","\n")
            node.tag = local_lookup[int(node.tag)]

        if node.tag not in candidates:
            candidates[node.tag] = 0
    else:
        node.tag = "R"

num_cands = len(candidates)
#clrs = distinctipy.get_colors(20)
clrs = [(0, 1, 0), (1, 0, 1), (0, 0.5, 1), (1, 0.5, 0), (0.5, 0.75, 0.5), (0.5800093713375801, 0.16478271170089775, 0.4301399554184866), (0.22162042352583133, 0.9989483387198071, 0.9956347226130852), (0.13118627414056694, 0.5057096596864245, 0.015541987908465837), (0.7511002637749555, 0.4576933900482424, 0.9857277925631447), (0.9540626514476586, 0.9989447017735341, 0.14947423333670107), (0.09459801019916891, 0.008096762244952482, 0.8024141859326779), (1, 0, 0), (0, 1, 0.5), (0.007109406335641499, 0.43929173318217185, 0.5012316719282135), (0.9985248284870453, 0.642012536002821, 0.6119787391089742), (0.5, 0, 0), (0.5, 1, 0), (0.5614135080918716, 0.12086114055056485, 0.9395941427675572), (0.6229258324121627, 0.34282118538031336, 0.037366011047648806), (0.9602031977907703, 0.2652246355235427, 0.644081788913095)]
clrs = clrs[:num_cands]


for key in candidates:
    candidates[key] = clrs.pop()

    
G,labeldict = t.tree2graph(compress=compress_graph,initials=False)

color_map = [(0.9,0.9,0.9)]
max_len = 0
for node in G:
    for cand in candidates:
        if len(cand) > max_len:
            max_len = len(cand)
        if cand in labeldict[node]:
            color_map.append(candidates[cand])


h_w = math.log(len(G))*18

plt.rcParams['figure.figsize'] = [h_w, h_w]
pos=nx.nx_pydot.graphviz_layout(G, prog="dot")

nsize = 300*max_len
nx.draw_networkx_nodes(
    G,
    pos=pos,
    node_size=nsize,
    node_color=color_map,
    edgecolors="blue",
    alpha=1,
    linewidths=6,
    node_shape="o"
)

nx.draw_networkx_labels(
    G,
    pos=pos,
    labels=labeldict,
    font_family = "sans-serif",
    font_color="black",
    font_size=10,
    font_weight="bold"
)
nx.draw_networkx_edges(
    G,
    pos,
    width=nsize/1500,
    alpha=1,
    edge_color="tab:blue",
    connectionstyle="arc3,rad=0.1",
    arrows=True,
    arrowsize=nsize/400,
    node_size = nsize
)

labels = nx.get_edge_attributes(G,'weight')
#nx.draw_networkx_edge_labels(G,pos,edge_labels=labels,font_size=35)

plt.box(False)

plt.savefig('output.eps', format='eps')
plt.show()