############################################################################################
#        Project : Fake(inactive) and Spam(advertisers) Account Detection of Facebook      # 
#        BY : Amit Khandelwal and Mehak Mehta                                              #
#        SBU ID : 109758198 and 109971470                                                  #
############################################################################################

import math
import json
import urllib2
import os
import csv;
from pprint import pprint
import csv;
import re;
import math;
import numpy as np;
import matplotlib.pyplot as plt
from numpy import linalg as LA
from scipy import linalg as SA
from sets import Set
import networkx as nx
from operator import itemgetter
from mcl.mcl_clustering import mcl


#name = "MehakMehta"
name = "AmitKhandelwal"


#Global Variables
edges= [];
spamTag=[];
cnt=0;
ver=0;
edg=0;

LIKES = 0
TAG = 1
COMMENT = 2
MSGTAG = 3

friends={}
interact = {}
activeFriends = Set([])
activeTag = Set([])
activeLikes =Set([])

with open(name+'/egoNetwork.txt', 'rb') as egonw:
	for line in egonw:
		cnt=cnt+1;
		if(cnt==1):
			ver=int(line);
		elif(cnt==2):
			edg=int(line);
		else:
			tedge=[int(i) for i in re.findall(r'\d+', line)];
			edges.append(tedge);

N={};

for t in range(1, ver+1):
    s=Set([])
    N[t]= s

for t in edges:
	N[t[0]].add(t[1]);
	N[t[1]].add(t[0]);
print N

def readFriendList():
    global friends
    with open(name+'/friendslist.csv', 'rb') as csvfile:
        frndreader = csv.reader(csvfile);
        for row in frndreader:
            print "id:" + row[1]
            print "name:"+row[0]
            friends[row[0]] = row[1]
            interact[row[0]] = [0,0,0,0]
    print interact

def dirwalk(path):
    # traverse root directory, and list directories as dirs and files as files
    for root, dirs, files in os.walk(path):
        path = root.split('/')
        print (len(path) - 1) *'---' , os.path.basename(root)
        for file in files:
            print len(path)*'---', file
            if file.endswith("json"):
                readFeed('/'.join(path)+"/"+file)

def increaseIndex(node, tag):
    if name == "AmitKhandelwal":
        node = node.replace(" ","")

    if node in interact:
        print node
        interact[node][tag]= interact[node][tag]+1
        nodeid = int(friends[node])
        activeFriends.add(nodeid)
        if(tag==TAG or tag==MSGTAG):
            activeTag.add(nodeid)
        if(tag==LIKES):
            activeLikes.add(nodeid)


def readFeed(filename):
#    print "FileName$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$: "+str(filename)
    with open(filename) as data_file:
        data = json.load(data_file)

    #print "length: " + str(len(data["feed"]["data"]))
    print "length: " + str(len(data["data"]))
    n = len(data["data"])
    for i in range(0, n):
        #print data["feed"]["data"][i]["from"];
        print data["data"][i]["id"];
        if(data["data"][i].get("message")):
            print data["data"][i]["message"];
        #if(data["feed"]["data"][i].get("story")):
            #print data["feed"]["data"][i]["story"];
        if(data["data"][i].get("type")):
            print data["data"][i]["type"];

        if(data["data"][i].get("likes")):
            for j in range(0, len(data["data"][i]["likes"]["data"])):
                print "Likes***************************"+str((data["data"][i]["likes"]["data"][j]["name"]).encode('ascii','ignore'))
                increaseIndex(str((data["data"][i]["likes"]["data"][j]["name"]).encode('ascii','ignore')), LIKES)

        # with_tags
        if(data["data"][i].get("with_tags")):
            for j in range(0, len(data["data"][i]["with_tags"]["data"])):
                print "with_tags***************************"+str((data["data"][i]["with_tags"]["data"][j]["name"]).encode('ascii','ignore'))
                increaseIndex(str((data["data"][i]["with_tags"]["data"][j]["name"]).encode('ascii','ignore')), TAG)

        if(data["data"][i].get("comments")):
            for j in range(0, len(data["data"][i]["comments"]["data"])):
                print "comments***************************"+str((data["data"][i]["comments"]["data"][j]["from"]["name"]).encode('ascii','ignore'))
                increaseIndex(str((data["data"][i]["comments"]["data"][j]["from"]["name"]).encode('ascii','ignore')), COMMENT)
                if(data["data"][i]["comments"]["data"][j].get("message_tags")):
                    for t in range(0, len(data["data"][i]["comments"]["data"][j]["message_tags"])):
                        print "message_tags***************************"+str((data["data"][i]["comments"]["data"][j]["message_tags"][t]["name"]).encode('ascii','ignore'))
                        increaseIndex(str((data["data"][i]["comments"]["data"][j]["message_tags"][t]["name"]).encode('ascii','ignore')), MSGTAG)


def createvector():
    A = np.zeros((ver, ver))
    for t in edges:
        #print "Vector: ",t[0],t[1]
        activeFSet1 = (N[t[0]] & activeFriends)
        activeFSet2 = (N[t[1]] & activeFriends)
        actFrnds = activeFSet1 & activeFSet2

        activePSet1 = (N[t[0]] & activeLikes)
        activePSet2 = (N[t[1]] & activeLikes)
        actLik = activePSet1 & activePSet2

        activeTSet1 = (N[t[0]] & activeTag)
        activeTSet2 = (N[t[1]] & activeTag)
        actTag = activeTSet1 & activeTSet2

        w = len(actFrnds) + len(actLik) + len(actTag)
        #if(w>0):
        #    print w
        #print "actFrnds", actFrnds
        A[t[0]-1][t[1]-1]=w
        A[t[1]-1][t[0]-1]=w
    return A




## How far you'd like your random-walkers to go (bigger number -> more walking)
EXPANSION_POWER = 2
## How tightly clustered you'd like your final picture to be (bigger number -> more clusters)
INFLATION_POWER = 2
## If you can manage 100 iterations then do so - otherwise, check you've hit a stable end-point.
ITERATION_COUNT = 100
def normalize(matrix):
    return matrix/np.sum(matrix, axis=0)

def expand(matrix, power):
    return np.linalg.matrix_power(matrix, power)

def inflate(matrix, power):
    for entry in np.nditer(matrix, op_flags=['readwrite']):
        entry[...] = math.pow(entry, power)
    return matrix

def run(matrix):
    np.fill_diagonal(matrix, 1)
    matrix = normalize(matrix)
    for _ in range(ITERATION_COUNT):
        matrix = normalize(inflate(expand(matrix, EXPANSION_POWER), INFLATION_POWER))
    return matrix

def drawGraph(spammers):
    for i in range(1, ver + 1):
        if i in spammers:
            spamTag.append('r')
        else:
            spamTag.append('b')

    nodes = []
    for t in range(1, ver + 1):
        nodes.append(t);
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    #G=nx.generators.barabasi_albert_graph(len(nodes),len(edges)
    # find node with largest degree
    node_and_degree = G.degree()
    (largest_hub, degree) = sorted(node_and_degree.items(), key=itemgetter(1))[-1]
    # Create ego graph of main hub
    hub_ego = nx.ego_graph(G, largest_hub)
    # Draw graph
    pos = nx.spring_layout(hub_ego)
    nx.draw(hub_ego, pos, node_color=spamTag, node_size=50, with_labels=False)
    # Draw ego as large and red
    nx.draw_networkx_nodes(hub_ego, pos, nodelist=[largest_hub], node_size=300, node_color='r')
    plt.savefig(name+"/"+ name+'_MCLGraph.png')
    plt.show()


if __name__ == '__main__':
    readFriendList()
    dirwalk(name+"/feeds")
    #for key in interact:
    #    print key, interact[key]

    print "interact: ",interact
    print "activeFriends: ",activeFriends
    print "activeTag: ",activeTag
    print "activeLikes: ",activeLikes
    #filename= './xplorer/feed.json'
    #readFeed(filename)
    Adj = createvector()

    M, clusters = mcl(Adj, expand_factor = 2, inflate_factor = 1.5, max_loop = 100, mult_factor = 2)
    print "clusters:", clusters

    for key in clusters:
        if(len(clusters[key])>=5 and len(clusters[key])<20):
            spammers = clusters[key]
            print spammers
    drawGraph(spammers)

    #MCL= run(Adj)

    #for i in xrange(ver):
    #    for j in xrange(ver):

            #print (MCL[i])


'''
with open('friendslist.csv', 'rb') as csvfile:
	frndreader = csv.reader(csvfile);
	for row in frndreader:
		print "name:"+row[0];
		print "id:" + row[1];
		print "tag:"+row[2];
		#commTag.append(getColorComm(row[3]));
		#socialTie.append(getColorSocialTie(row[2]));
		if(int(row[1])>=ver):
			break;
#print edges;
'''