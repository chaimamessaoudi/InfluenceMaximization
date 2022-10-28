from enum import unique
from wsgiref.util import request_uri
import sknetwork as skn
from cmath import e
from sknetwork.clustering import Louvain, get_modularity
from statistics import mean 
from sknetwork.clustering import PropagationClustering, get_modularity
from sknetwork.clustering import KMeans, get_modularity
from sknetwork.embedding import GSVD
#from cdlib import algorithms , viz , evaluation , readwrite , ensemble
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from operator import itemgetter
import sys
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc

''' Paramètres '''
'''
from scipy import sparse
path_graph = "mygraphclean.txt"
path_tweets = "allTweetsCSV.csv"
'''
path_graph  = "mygraphClean.txt"
path_tweets = "allTweetsCSV.csv"
osfile = []
alpha_0=1 #A voir !!!!
alpha_1=2
alpha_2=2
alpha_3=4
alpha_max = alpha_3
radius = 3   # neighbourhood
''' Préparation des fichiers '''
from networkx import edge_betweenness_centrality as betweenness
def most_central_edge(G):

    centrality = betweenness(G, weight="weight")

    return max(centrality, key=centrality.get)

fr_graph = open(path_graph,"r",encoding="utf8")
 
''' Préparation des classes tweet & user '''

######### Class tweet #############################

class tweet:
	def __init__(self, idt, text, pre, lang, topics, nb_likes, nb_replies, nb_retweets, opinion):
		self.idt = idt
		self.text = text
		self.pre = pre
		self.lang = lang
		self.topics = topics
		self.nb_likes = nb_likes
		self.nb_replies = nb_replies
		self.nb_retweets = nb_retweets
		self.opinion=opinion 
	
######### Class user #############################	

class user:
	def __init__(self, idu, username, nb_followings, nb_followers):
	
		self.idu = idu
		self.username = username
		self.nb_followings = nb_followings
		self.nb_followers = nb_followers
		
		self.tweets = {}
		self.followings = {}
		self.followers = {}
	def __str__(self):
		return str(self.idu)
	def __repr__(self):
		return str(self.idu)
	def __gt__(self, other):
		if(self.psi_user()>other.psi_user()):
			return True
		else:
			return False
	def __lt__(self, other):
		if(self.psi_user()<other.psi_user()):
			return True
		else:
			return False

	
	def psi_user(self):
		a,b,c=0,0,0
		actions=[]

		for idt, tweet in self.tweets.items():

			a+=tweet.nb_likes
			b+=tweet.nb_replies
			c+=tweet.nb_retweets


		actions=[a,b,c]

		#The importance of actions (weights) are as follow: αlike = 0.15, αreply = 0.35 et αretweet = 0.50. 
		if(actions[0]+actions[1]+actions[2]) == 0:
			psi = e-2
		else :
			psi=(actions[0]*0.15+actions[1]*0.35+actions[2]*0.5)/(actions[0]+actions[1]+actions[2])
		return psi
		

	
	#opinions de l'utilisateur à propos de ses topics(lkol)	
	def opinion(self):

		#dtopic{"topic",opinion}
		dtopics = {}
		
		for idt, tweet in self.tweets.items():
			for topic in tweet.topics:
				#print(tweet.opinion )

				if not (topic == '0'):
					if topic not in dtopics:
						dtopics[topic] = tweet.opinion
					else :
						dtopics[topic] = dtopics[topic] + tweet.opinion
		#print(dtopics)
		return dtopics


	def Opinion_Similarity(self,user2):
            #kol marra na3mlou lproduit binet'hom: lproduit 7asb les règles d'influence: 
            # No influence: <0.1
            # low Influence : [0.1,0.5]
            # Medium Influence: [0.5,0.9]
            #  High Influence: > 0.9
            os = 0
            user1opinions=self.opinion()
            user2opinions=user2.opinion()
            #print(user1opinions)
            #print(user2opinions)
            #Nchouf 
            ntps = 0
            for topic1,opinion1 in user1opinions.items() : 
                for topic2,opinion2 in user2opinions.items():                    
                    if topic1 == topic2 :
                        ntps += 1
                        if (int(opinion1) == 0) and (int(opinion2) > 0) :
                            os = os + alpha_1/alpha_max
                        elif (int(opinion1) == 0) and (int(opinion2) < 0) :
                            os = os + alpha_1/alpha_max
                        elif (int(opinion1) == 0) and (int(opinion2) == 0) :
                            os = os +alpha_0/alpha_max
                            
                        elif (int(opinion1) > 0) and (int(opinion2) > 0) :
                            os = os + alpha_2/alpha_max
                        elif (int(opinion1) > 0) and (int(opinion2) == 0) :
                            os = os + alpha_3/alpha_max
                        elif (int(opinion1) > 0) and (int(opinion2) < 0) :
                            os = os + alpha_1/alpha_max
                            
                        elif (int(opinion1) < 0) and (int(opinion2) > 0) :
                            os = os + alpha_0/alpha_max
                        elif (int(opinion1) < 0) and (int(opinion2) == 0) :
                            os = os + alpha_1/alpha_max
                        elif (int(opinion1) < 0) and (int(opinion2) < 0) :
                            os = os + alpha_0/alpha_max
            if ntps == 0:
                return os                
            return os/ntps


##############################################################Pagerank###########################

''' Load users and their tweets '''

# dict vide pour stocker les users (clé: idu, value: objet user)
class UserDao:
	def __init__(self) :
		self.dusers = {}	
	def getAllUsers(self):
	# Parcourir les lignes du fichier tweets pour remplir le dict dusers (idu: objet user)
		i=0
		reader = pd.read_csv(path_tweets,skiprows=3).fillna('0') 
		reader = 	reader.iterrows()
		for index, sp in reader:
			idu = int(sp[2])
			username = sp[3]					
			nb_followings = sp[11] 
			nb_followers =  sp[12] 					
			if idu not in self.dusers:
				self.dusers[idu] = user(idu, username, nb_followings, nb_followers)			
					
class Graph:
	def __init__(self) :  
		self.graphe=nx.DiGraph() 
	
	def construct_graph(self,dusers):
		for idu, user in dusers.items():
			self.graphe.add_node(user)
 			#print("psi" + str(psi))
		for l in fr_graph:
			sp = l.rstrip().split("\t")
			# src (followee) dans position 0
			idu_dst = int(sp[0].strip('\n'))
			# src (follower) dans position 1
			idu_src = int(sp[1].strip('\n'))
			if idu_src not in dusers or idu_dst not in dusers:
				# skip
				continue
			dusers[idu_src].followings[idu_dst] = dusers[idu_dst]
			dusers[idu_dst].followers[idu_src] = dusers[idu_src]			
			os= dusers[idu_dst].Opinion_Similarity(dusers[idu_dst].followers[idu_src])
			osfile.append(os)
			self.graphe.add_edges_from([(dusers[idu_dst],dusers[idu_dst].followers[idu_src])])
 			 
		 



	def influence_count(self, seeds, threshold):
		''' Calculate influent result
		Args:
			nodes (list) [#node]: nodes list of the graph;
			edges (list of list) [#edge, 2]: edges list of the graph;
			seeds (list) [#seed]: selected seeds;
			threshold (float): influent threshold, between 0 and 1;
		Return:
			final_actived_node (list): list of influent nodes;
		'''
		in_degree = {}
		inactive_nodes = []
		active_nodes = []
		nodes_status = {}

		for edge in list(self.graphe.edges): 
			if edge[0] in seeds:
				active_nodes.append(edge[0])
			else:
				inactive_nodes.append(edge[0])
			if edge[1] in seeds:
				active_nodes.append(edge[1])
			else:
				inactive_nodes.append(edge[1])
			if edge[1] in in_degree:
				in_degree[edge[1]] += 1
			else:
				in_degree[edge[1]] = 1

		active_nodes = list(set(active_nodes))
		inactive_nodes = list(set(inactive_nodes))

		for node in list(self.graphe.nodes):
			nodes_status[node] = 0
		for node in active_nodes:
			nodes_status[node] = 1
				
		while(active_nodes):
			new_actived_nodes = []
			for edge in list(self.graphe.edges):
				if nodes_status[edge[0]] == 1:
					if nodes_status[edge[1]] == 0:
						p = np.array([1 - threshold / in_degree[edge[1]], threshold / in_degree[edge[1]]])
						flag = np.random.choice([0, 1], p=p.ravel())
						if flag:
							new_actived_nodes.append(edge[1])
			for node in active_nodes:
				nodes_status[node] = 2
			for node in new_actived_nodes:
				nodes_status[node] = 1
			active_nodes = new_actived_nodes

		final_actived_node = 0
		for node in list(self.graphe.nodes):
			if nodes_status[node] == 2:
				final_actived_node += 1
		return final_actived_node  
def Convert(string):
	li = list(string.split(","))
	li = li[0:-1]
	return li

#try :    

f = open("propagationoutput.txt","w")
leaders = []
leaders_file = open("cands.csv","r")
for l in leaders_file:
	leaders.append(l.strip("\n"))
print('--------------- Results of Strategy ------------------')
dao = UserDao()
dao.getAllUsers()
g = Graph() 
g.construct_graph(dao.dusers)
	
	#leaders = ['1676', '648', '988', '41', '380', '586', '414', '2152', '57', '107', '1371', '277', '681', '888', '17', '409', '985', '1497', '418', '1173', '58', '292', '2493', '346', '188', '2185', '2483', '150', '880', '1974', '2294', '1929'] #strategie 1
	#leaders = ['292', '2518', '2294'] #strategie 2
	#leaders= ['12801'] #strategie 3



pl = []
largest_cc = list(max(nx.connected_components(g.graphe.to_undirected()), key=len))
#print(largest_cc)
g.graphe=g.graphe.subgraph(largest_cc)

""" subgraph = []
nodes_file = open("data/nodes.txt","r")
for l in nodes_file:
	subgraph = Convert(l)
nodes =[]
for user in list(g.graphe.nodes):
	for id in subgraph:
		if user.idu == int(id):
			nodes.append(user)
g.graphe=g.graphe.subgraph(nodes) """
	
print("number of users " + str(len(g.graphe.nodes)))


# Linear threshold model
pl = []
for user in list(g.graphe.nodes):
	for id in leaders:
		if user.idu == int(id):
			pl.append(user)
print("number of leaders " + str(len(pl)))
prop=[]
for i in range (10):
	prop.append(g.influence_count(pl,1))	
print("number of infected " + str(max(prop)))
print(str(max(prop)/len(g.graphe.nodes)*100)+"%")


	# Cascade model


""" model = ep.IndependentCascadesModel(g.graphe)

	# Model Configuration
	config = mc.Configuration()
	config.add_model_initial_configuration("Infected", pl)

	# Setting the edge parameters
	threshold = 1
	for e in g.graphe.edges():
		config.add_edge_configuration("threshold", e, threshold)

	model.set_initial_status(config)

	# Simulation execution
	iterations = model.iteration_bunch(200)
	trends = model.build_trends(iterations)
	from ndlib.viz.mpl.DiffusionTrend import DiffusionTrend
	# Visualization
	viz = DiffusionTrend(model, trends)
	viz.plot("diffusion.pdf") """
""" except Exception as e:
    err = open('propagation.log', 'w')
    err.write(str(e))
    err.close()
 """
