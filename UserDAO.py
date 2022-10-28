''' Load users and their tweets '''
import pandas as pd
from User import User
from Tweet import Tweet
from User import User
path_graph = "mygraphClean.txt"
path_tweets = "allTweetsCSV.csv"
""" path_graph = "data/newGraph.txt"
path_tweets = "data/newTweets.csv" """


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
				# (*) Ajouter un objet user (s'il n'est pas déjà ajouté)
				#print(i)
				idu = int(sp[2])
				username = sp[3]
				nb_followings = sp[11]  
				nb_followers =  sp[12] 
				if idu not in self.dusers:
					# ici le constructeur "__init__" de user va être exécuté par ces arguments
					self.dusers[idu] = User(idu, username, nb_followings, nb_followers)
				# (*) Ajouter un objet tweet à l'user
				idt = sp[1]
				text = sp[4]
				pre = sp[17]
				lang = sp[5]
				t= sp[18] # plsr topics? peut être que ça necessite un .split(...)
				#print(t)
				topics = t.rstrip().split(",")
				opinion = sp[19]
				nb_likes = int(sp[6])
				#print(len(sp))
				#print(nb_likes)
				nb_replies =  int(sp[7])
				nb_retweets = int(sp[8]) 
				# ici le constructeur "__init__" de tweet va être exécuté par ces arguments
				self.dusers[idu].tweets[idt] = Tweet(idt, text, pre, lang, topics, nb_likes, nb_replies, nb_retweets, opinion)
		#print(dusers[idu].tweets[idt].opinion)
	
		del reader