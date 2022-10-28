import mesa

from UserDAO import UserDao
from Graph import Graph
import networkx as nx
from VoteAgent import VoteManagerAgent
from User import UserAgent

import sys
import logging


class VoteModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self):
        print("here we go")
        self.schedule = mesa.time.SimultaneousActivation(self)
        dao = UserDao()
        dao.getAllUsers()
        g = Graph() 
        g.construct_graph(dao.dusers)
        del dao.dusers
        largest_cc = list(max(nx.connected_components(g.graphe.to_undirected()), key=len))
        #print(largest_cc)
        g.graphe=g.graphe.subgraph(largest_cc)
        #print(g.graphe)
        self.useragents =[]
        # Create agents
        self.manager = VoteManagerAgent("VoteManager",self,g.graphe)
        print("here")
        del g
        for user in self.manager.dict_voter_candidates:
            #print(user)
            a = UserAgent(str(user), self,False,False,user,self.manager.dict_voter_candidates[user])
            self.schedule.add(a)
            self.useragents.append(a)
            self.manager.aggregate_votes(a.dict_vote)            
        self.schedule.add(self.manager)

        

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
       
#try :    
f = open("output.txt","w")

process_model = VoteModel()
process_model.step()
""" except Exception as e:
    err = open('run.log', 'w')
    err.write(str(e))
    err.close() """