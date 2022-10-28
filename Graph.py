import sknetwork as skn
#from cdlib import algorithms , viz , evaluation , readwrite , ensemble
import networkx as nx

radius = 3   # neighbourhood

''' Paramètres '''
path_graph = "mygraphClean.txt"
path_tweets = "allTweetsCSV.csv"
""" path_graph = "data/newGraph.txt"
path_tweets = "data/newTweets.csv" """
fr_graph = open(path_graph,"r",encoding="utf8")
''' Préparation des classes tweet & user '''
######### Class user #############################	
class Graph:
	def __init__(self) :  
		self.graphe=nx.DiGraph()
	
	def construct_graph(self,dusers):
		for idu, user in dusers.items():
			psi =  user.psi_user()
			self.graphe.add_node(user,weight =psi)
			#print("psi" + str(psi))


	#####youfa lahne el jdid####

	# Parcourir les lignes du fichier graphe pour remplir les relations (followers & followings) de chaque user
		for l in fr_graph:
			sp = l.rstrip().split("\t")

			# src (followee) dans position 0
			idu_dst = int(sp[0].strip('\n'))

			# src (follower) dans position 1
			idu_src = int(sp[1].strip('\n'))

			# un utilisateur n'est pas existe dans le dict d'objets users rempli par les tweets?
			if idu_src not in dusers or idu_dst not in dusers:
				# skip
				continue

			# ajouter le followee au dict de following du follower
			#print("------------")
			#print(dusers[idu_dst])
			#print(dusers[idu_src])
			#Na77it hedhi
			#dusers[idu_src].followings[dusers[idu_dst]]
			
			#id_src.followings[idu_dst] = dusers[idu_dst]
			#dusers[idu_dst].followings.append(dusers[idu_src])
			# ajouter le follower au dict de followers du followee
			#Na77it hedhi
			#dusers[idu_dst].followers[dusers[idu_src]]
			#id_dest.followings[idu_src] = dusers[idu_src]
			#dusers[idu_src].followings.append(dusers[idu_dest])
			dusers[idu_src].followings[idu_dst] = dusers[idu_dst]
			dusers[idu_dst].followers[idu_src] = dusers[idu_src]
			
			os= dusers[idu_dst].Opinion_Similarity(dusers[idu_dst].followers[idu_src].opinion())
			self.graphe.add_edges_from([(dusers[idu_dst].followers[idu_src],dusers[idu_dst])],weight = os)
			
			#print("------------")
		fr_graph.close()

		#print(self.graphesk)