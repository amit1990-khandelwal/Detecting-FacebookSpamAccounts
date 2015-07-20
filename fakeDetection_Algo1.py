############################################################################################
#        Project : Fake(inactive) and Spam(advertisers) Account Detection of Facebook      # 
#        BY : Amit Khandelwal and Mehak Mehta                                              #
#        SBU ID : 109758198 and 109971470                                                  #
############################################################################################


import math
import json
from pprint import pprint
import numpy as np
import os
import xlwt
import xlrd
from heapq import nlargest
from operator import itemgetter
import csv;
import re;
import matplotlib.pyplot as plt
from numpy import linalg as LA
from scipy import linalg as SA
from sets import Set
import networkx as nx
from os import listdir
from os.path import isfile, join
import itertools
import scipy
from scipy.sparse import *
from operator import itemgetter
import sys


#name = "MehakMehta"
#my_Name = "Mehak Mehta"
name = "AmitKhandelwal"
my_Name = "Amit Khandelwal"


#Global variables
No_friends = 0                                          #Number of friends
Uid_Id_Map = {}                                         #Dictionary for Friends<->UID mapping
Id_Name_Map = {}                                        #Mapping of Number (ID) to Friend Name
Name_Id_Map = {}                                        #Mapping of Name to Number (ID)
fake_factor = {}
interact = {}
maxscorers = []

#Constants
LIKES = 0
TAG = 1
COMMENT = 2
MSGTAG = 3

## interaction data global variables
##Interation_Score
#Number :
# 1 : Number of two-sided communications
# 2 : Number of one-sided communications
# 3 : Number of fromMe communications in case of one-sided
# 4 : Number of toMe communications in case of one-sided

No_interactions = 0
No_oneSided = 0
No_fromMe = 0
Flag_fromMe = 0
No_toMe = 0
Flag_toMe = 0
No_twoSided = 0


def fakescore(data):
    global No_friends
    global Uid_Id_Map
    global Id_Name_Map
    global Name_Id_Map
    #global fake_factor
 
    fake_score = [set() for i in range(0,No_friends)]       #Score matrix of All friends to be considered as Fake account
    for i in range(No_friends):
        fake_value = 0
        Uid_Id_Map[data[i]["uid"]] = i
        Id_Name_Map[i] = data[i]["name"]
        Name_Id_Map[data[i]["name"]] = i
        fake_score[i].add(data[i]["name"])
        interact[data[i]["name"]] = [0,0,0,0]
        # Girls having their email-id mentioned publically : score value 7  : Fake Factor +8
        if data[i]["sex"] == "female" and data[i]["email"] != None:
            fake_score[i].add(7)
            fake_value += 8

        # Friends having Birth-Date mentioned as 1-Jan, 31-Dec or 1-April can potentially be fake : score value 6 : Fake Factor +3
        if data[i]["birthday"] != None:
            if data[i]["birthday"].split(",")[0] == "January 1" or data[i]["birthday"].split(",")[0] == "December 31" or data[i]["birthday"].split(",")[0] == "April 1":
                fake_score[i].add(6)
                fake_value += 3
        # if current_location and hometown location are missings : can be supporting factor for fake accounts : score value 5 : Fake Factor +3
        if data[i]["current_location"] == None and data[i]["hometown_location"] == None and data[i]["email"] == None:
            fake_score[i].add(5)
            fake_value += 3
        # Friends having education, work mentioned in their profiles are definitely not fake accounts : Fake Factor +2
        if data[i]["affiliations"] != None:
            fake_score[i].add(11)
            fake_value += 2
        # if the last profile update time is more than 1 year's back, it most probably be a fake account : score value 9 : Fake Factor +9
        if data[i]["profile_update_time"] < 1400000000:    ## Tue May 13 12:53:20 EDT 2014
            fake_score[i].add(9)
            fake_value +=9
        fake_factor[i] = fake_value


def increaseIndex(name, tag):
    #global interact
    #print interact
    if name in interact:
        interact[name][tag]= interact[name][tag]+1


def readInterFeed(filename):
    with open(filename) as data_file:
        data = json.load(data_file)

    n = len(data["data"])
    for i in range(0, n):

        if(data["data"][i].get("likes")):
            for j in range(0, len(data["data"][i]["likes"]["data"])):
                #print "Likes***************************"+str((data["data"][i]["likes"]["data"][j]["name"]).encode('ascii','ignore'))
                increaseIndex(str((data["data"][i]["likes"]["data"][j]["name"]).encode('ascii','ignore')), LIKES)

        # with_tags
        if(data["data"][i].get("with_tags")):
            for j in range(0, len(data["data"][i]["with_tags"]["data"])):
                #print "with_tags***************************"+str((data["data"][i]["with_tags"]["data"][j]["name"]).encode('ascii','ignore'))
                increaseIndex(str((data["data"][i]["with_tags"]["data"][j]["name"]).encode('ascii','ignore')), TAG)

        if(data["data"][i].get("comments")):
            for j in range(0, len(data["data"][i]["comments"]["data"])):
                #print "comments***************************"+str((data["data"][i]["comments"]["data"][j]["from"]["name"]).encode('ascii','ignore'))
                increaseIndex(str((data["data"][i]["comments"]["data"][j]["from"]["name"]).encode('ascii','ignore')), COMMENT)
                if(data["data"][i]["comments"]["data"][j].get("message_tags")):
                    for t in range(0, len(data["data"][i]["comments"]["data"][j]["message_tags"])):
                        increaseIndex(str((data["data"][i]["comments"]["data"][j]["message_tags"][t]["name"]).encode('ascii','ignore')), MSGTAG)


#reading the whole chat folder of the any friend
def readFeed(filename, Interaction_Score):
    global No_interactions
    global No_oneSided
    global No_fromMe
    global Flag_fromMe
    global No_toMe
    global Flag_toMe
    global No_twoSided
    global Name_Id_Map
    global Id_Name_Map


    with open(filename) as chat_file:    
        chat = json.load(chat_file)
    
    No_interactions = len(chat["data"])
    for i in range(0,No_interactions):
        No_fromMe = 0
        Flag_fromMe = 0
        No_toMe = 0
        Flag_toMe = 0
        friend_id = 0
        No_oneSided = 0
        No_twoSided = 0

        if chat["data"][i]["to"]["data"][0]["name"] != my_Name:
            if (Name_Id_Map.has_key(chat["data"][i]["to"]["data"][0]["name"])):
                friend_id = Name_Id_Map[chat["data"][i]["to"]["data"][0]["name"]]
            else:
                continue
        else :
            if len(chat["data"][i]["to"]["data"]) == 2:
                if (Name_Id_Map.has_key(chat["data"][i]["to"]["data"][1]["name"])):
                    friend_id = Name_Id_Map[chat["data"][i]["to"]["data"][1]["name"]]
                else:
                    continue
            else:
                continue

        for j in range(len(chat["data"][i]["comments"]["data"])):
            if chat["data"][i]["comments"]["data"][j]["from"]["name"] == my_Name:
                Flag_fromMe = 1
                No_fromMe += 1
            elif chat["data"][i]["comments"]["data"][j]["from"]["name"] != my_Name:
                Flag_toMe = 1
                No_toMe += 1
        
        if Flag_fromMe == 1 and Flag_toMe == 1:
            No_twoSided = 1
        else:
            No_oneSided = 1       
        
        Interaction_Score[friend_id][0] += No_twoSided
        Interaction_Score[friend_id][1] += No_oneSided
        if No_oneSided == 1 :
            Interaction_Score[friend_id][2] += No_fromMe
            Interaction_Score[friend_id][3] += No_toMe

        if( friend_id == 424):
            print str(Interaction_Score[friend_id][0]) + " " + str(No_twoSided)  + " " + Id_Name_Map[friend_id]    



def dirInterwalk(path):
    # traverse root directory, and list directories as dirs and files as files
    for root, dirs, files in os.walk(path):
        path = root.split('/')
        for file in files:
        #    print len(path)*'---', file
            if file.endswith("json"):
                readInterFeed('/'.join(path)+"/"+file)



def dirwalk(path, Interaction_Score):
# traverse root directory, and list directories as dirs and files as files
    global No_friends
    for root, dirs, files in os.walk(path):
        path = root.split('/')
        #print (len(path) - 1) *'---' , os.path.basename(root)
        for file in files:
            #print len(path)*'---', file
            if file.endswith("json"):
                #print file
                #readFeed('/'.join(path)+"/"+file
                readFeed('/'.join(path)+"/"+file, Interaction_Score)

    return  Interaction_Score                


#Taking all the friends data
def readFriendData(name):
    global No_friends
    global my_Name
    print "./"+name+"/friends_data.json"
    with open("./"+name+"/friends_data.json") as data_file:
        data = json.load(data_file)
    No_friends = len(data)
    if my_Name == "Amit Khandelwal":
        No_friends = 200
    fakescore(data)


def interactionData(name):
    ''' No_interactions = 0
        No_oneSided = 0
        No_fromMe = 0
        Flag_fromMe = 0
        No_toMe = 0
        Flag_toMe = 0
        No_twoSided = 0
    '''
    global No_friends
    global my_Name
    print No_friends

    Interaction_Score = np.zeros((No_friends,4), dtype=np.int)      #Interaction matrix of All friends  
    print "./"+ str(name) + "/data"
    Interaction_Score = dirwalk("./"+ str(name) + "/data", Interaction_Score)
    dirInterwalk("./"+ str(name) + "/feeds")

    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('Names_toFakeValue')

    for i in range(No_friends):
        fake_value = 0
        fake_value = -Interaction_Score[i][0]*2 + Interaction_Score[i][1]*3 - Interaction_Score[i][2]*0.1 + Interaction_Score[i][3]*0.3
        fake_value += interact[Id_Name_Map[i]][LIKES]*2 + interact[Id_Name_Map[i]][TAG]*3 - interact[Id_Name_Map[i]][COMMENT]*3 - interact[Id_Name_Map[i]][MSGTAG]*1 
        fake_factor[i] += fake_value
        print str(i) + " " + Id_Name_Map[i] + " " + str(Interaction_Score[i]) + " [" + str(interact[Id_Name_Map[i]][LIKES]) +","+str(interact[Id_Name_Map[i]][TAG])+","+str(interact[Id_Name_Map[i]][COMMENT])+","+str(interact[Id_Name_Map[i]][MSGTAG])+"]"
        worksheet.write(i,0,Id_Name_Map[i])
        worksheet.write(i,1,fake_factor[i])
    workbook.save(name +'/Friends_fakeValue.xls')

    print "Maximum score people :-"
    for i, score in nlargest(10, fake_factor.iteritems(), key=itemgetter(1)):
        print Id_Name_Map[i], score
        if my_Name == "Amit Khandelwal":
            maxscorers.append(Id_Name_Map[i].replace(" ",""))
        else:
            maxscorers.append(Id_Name_Map[i])

edges = [];
commTag = [];
socialTie = [];
cnt = 0;
ver = 0;
edg = 0;

name_id = {}

def colorNodes():
    global cnt
    global ver
    global edg    
    global No_friends

#    print maxscorers
    with open(name+'/friendslist.csv', 'rb') as csvfile:
        frndreader = csv.reader(csvfile);
        for row in frndreader:
            if row[0] in maxscorers:
                socialTie.append('r')
            else:
                socialTie.append('b')


def egoNetwork():
    global cnt
    global ver
    global edg

    with open(name+'/egoNetwork.txt', 'rb') as egonw:
        for line in egonw:
            cnt = cnt + 1;
            if (cnt == 1):
                ver = int(line);
            elif (cnt == 2):
                edg = int(line);
            else:
                tedge = [int(i) for i in re.findall(r'\d+', line)];
                edges.append(tedge);


def drawGraph():
    nodes = []
    for t in range(No_friends):
        nodes.append(t);
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    # find node with largest degree
    node_and_degree = G.degree()
    (largest_hub, degree) = sorted(node_and_degree.items(), key=itemgetter(1))[-1]
    # Create ego graph of main hub
    hub_ego = nx.ego_graph(G, largest_hub)
    # Draw graph
    pos = nx.spring_layout(hub_ego)
    nx.draw(hub_ego, pos, node_color=socialTie, node_size=50, with_labels=False)
    # Draw ego as large and red
    nx.draw_networkx_nodes(hub_ego, pos, nodelist=[largest_hub], node_size=300, node_color='r')
    plt.savefig(name+"/"+ name+'_egoGraph.png')
    plt.show()


if __name__ == '__main__':
    readFriendData(name)
    interactionData(name)
    egoNetwork()
    colorNodes()
    drawGraph()