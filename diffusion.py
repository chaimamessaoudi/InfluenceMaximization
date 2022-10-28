from statistics import mean, median, median_low
from UserDAO import UserDao
from Graph import Graph
import networkx as nx
from User import User
import numpy as np
import sys
import logging
import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics as ep

def Convert(string):
	li = list(string.split(","))
	li = li[0:-1]
	return li

#try :    

leaders = []
leaders_file = open("leaders.txt","r")
for l in leaders_file:
	leaders = Convert(l)
print(len(leaders))


print('--------------- Results of Strategy ------------------')
dao = UserDao()
dao.getAllUsers()
g = Graph() 
g.construct_graph(dao.dusers)
pl = []
largest_cc = list(max(nx.connected_components(g.graphe.to_undirected()), key=len))
#print(largest_cc)
g.graphe=g.graphe.subgraph(largest_cc)
pl = []
for user in list(g.graphe.nodes):
	for id in leaders:
		if user.idu == int(id):
			pl.append(user)
print("number of leaders " + str(len(pl)))

# Linear threshold model

g.graphe = g.graphe.reverse()    

condition = [0,1,2,3]

for cond in condition:
    all_nodes = {}
    all_edges = {}
    
    for node in list(g.graphe.nodes):
        all_nodes[node] = 0
        if node in pl:
            all_nodes[node] = 1

    for edge in list(g.graphe.edges):    
        if edge[0] not in all_edges:
            all_edges[edge[0]] = {}
        all_edges[edge[0]][edge[1]] = g.graphe.get_edge_data(edge[0], edge[1],'weight')      
    if cond == 0:
        print('----------------- cond psi * cond os ------------------')
    if cond == 1:
        print('----------------- cond psi + cond os ------------------')
    if cond == 2:
        print('----------------- cond psi  ------------------')
    if cond == 3:
        print('-----------------  cond os ------------------')
    for node in all_nodes:
        if all_nodes[node] == 1:
            if node in all_edges:
                neighbours = all_edges[node]
                neighbours_os = []
                for neighbour in neighbours:
                    neighbours_os.append(neighbours[neighbour]['weight'])
                for neighbour in neighbours:
                    if all_nodes[neighbour] == 0:
                        if cond == 0:
                            if (neighbours[neighbour]['weight'] >= median(neighbours_os)) and (neighbour.psi_user() <= node.psi_user()):
                                all_nodes[neighbour] = 1
                        elif cond == 1:
                            if (neighbours[neighbour]['weight'] >= median(neighbours_os)) or (neighbour.psi_user() <= node.psi_user()):
                                all_nodes[neighbour] = 1
                        elif cond == 2:
                            if (neighbour.psi_user() <= node.psi_user()):
                                all_nodes[neighbour] = 1
                        elif cond == 3:
                            if (neighbours[neighbour]['weight'] >= median(neighbours_os)):
                                all_nodes[neighbour] = 1
                        

    i = 0
    j = 0
    for node in all_nodes:
        if all_nodes[node] == 1:
            i += 1
        else :
            j += 1
    print("linear threshold model")
    print("number of nodes " + str(len(all_nodes)))
    print("infected " + str(i))
    print("not infected " + str(j))
    print('percentage of infected nodes ' + str(100*(i)/len(all_nodes))+'%')

    print("infected nodes")
    for node in all_nodes:
        if all_nodes[node] == 1:
            print(node.idu)
    print("not infected nodes")
    for node in all_nodes:
        if all_nodes[node] == 0:
            print(node.idu)
""" # Independent Cascade model
all_nodes = {}
all_edges = {}
for node in list(g.graphe.nodes):
    all_nodes[node] = 0
    if node in pl:
        all_nodes[node] = 1

for edge in list(g.graphe.edges):    
    if edge[0] not in all_edges:
        all_edges[edge[0]] = {}
    all_edges[edge[0]][edge[1]] = g.graphe.get_edge_data(edge[0], edge[1],'weight')
    

 
for node in all_nodes:
    if all_nodes[node] == 1:
        if node in all_edges:                
            neighbours = all_edges[node]
            for neighbour in neighbours:
                neighbours_os.append(neighbours[neighbour]['weight'])
            for neighbour in neighbours:
                if all_nodes[neighbour] == 0:
                    if (neighbours[neighbour]['weight'] >= median_low(neighbours_os)) * (neighbour.psi_user() <= node.psi_user()):
                        all_nodes[neighbour] = 1
            all_nodes[node] = 2
  
                

i = 0
k = 0
j = 0
for node in all_nodes:
    if all_nodes[node] == 2:
        i += 1
    elif all_nodes[node] == 1:
        k += 1
    else :
        j += 1
print("indepedent cascade model")
print("number of nodes " + str(len(all_nodes)))
print("activated/removed " + str(i))
print("infected but not activated " + str(k))
print("not infected " + str(j))
print('percentage of activated/removed nodes ' + str(100*i/len(all_nodes))+'%')
print('percentage of infected nodes ' + str(100*(i+k)/len(all_nodes))+'%') """
 


 
