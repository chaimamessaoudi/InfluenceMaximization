from cmath import e
import mesa
import statistics
from statistics import mean

alpha_0=1 #A voir !!!!
alpha_1=2
alpha_2=2
alpha_3=4
alpha_max = alpha_3


class UserAgent(mesa.Agent):

	def __init__(self, unique_id, model,isCandidate,isVoter,user,candidates):
		super().__init__(unique_id, model)
		self.user=user
		self.isCandidate=isCandidate
		self.isVoter=isVoter
		self.user.listCandidates = candidates
		self.dict_vote={}
		self.compute_cv()
		self.dict_vote = self.user.local_vote_majority()

		#self.dict_vote = self.stratgey_same_ops()
		#self.dict_vote = self.stratgey_candidate_actions_topic_best_tweet()
		#self.dict_vote = self.stratgey_candidate_actions_topic_all_tweets()
		#self.dict_vote = self.stratgey_candidate_actions_topic_all_tweets_and_cv(0.3)# weight CV_distance + (1-weight) CV_topics
		

	def step(self):
		# The agent's step will go here.
		# For demonstration purposes we will print the agent's unique_id
		print("Hi, I am User agent " + str(self.unique_id) )
		#print(self.dict_vote)


    #cv = sum(OS)/distance  
	def compute_cv(self):
		#get the list of the candidates for the voter
		for candidate in self.user.listCandidates:
			self.user.dict_os_vote[candidate]=0
			# os = 1 if the voter is the candidate
			if candidate.idu == self.user.idu:
				self.user.dict_os_vote[candidate] = 1
			# compute os with candidate
			if candidate.idu != self.user.idu:
				self.user.dict_os_vote[candidate] = self.user.Opinion_Similarity(candidate.opinion())
			# if the voter is not a direct neighbour the path will be [idVoter, idFirst, ....,idCandidate]
			if(len(self.user.listCandidates[candidate][1])) > 1:
				#remove idVoter and idCandidate from the path
				self.user.listCandidates[candidate][1] = self.user.listCandidates[candidate][1][1:-1]
				#foreach user in the path compute his OS with the leader and add it to the total os OS		
				for index in range(0,len(self.user.listCandidates[candidate][1])): 
					self.user.dict_os_vote[candidate] += self.user.listCandidates[candidate][1][index].Opinion_Similarity(candidate.opinion())   
		# foreach candidate compute cv = sum(os) / distance
		for candidate in self.user.listCandidates:
			self.user.dict_cv[candidate] = self.user.dict_os_vote[candidate] /self.user.listCandidates[candidate][0]

	def stratgey_same_ops(self): 
		#used to store the maximum value of similarity of opinion by topic
		max_similarity_by_ops = {}
		#used to store the list of chosen candidates
		list_of_yes = {}
		#get my opinions for each topic
		mine = self.user.opinion()
		for topic in mine:
			max_similarity_by_ops[topic] = 0
		sim_by_op_by_candidate={ }
		#foreach candidate : get his opinions , foreach common topic : compute the similarity 
		#and store it in sim_by_op_by_candidate[candidate]
		for candidate in self.user.listCandidates:
			sim_by_op_by_candidate[candidate]={}
			for topic1 in mine:
				other = candidate.opinion()
				for topic2 in other:
					if topic1 == topic2 :
						if (int(mine[topic1]) == 0) and (int(other[topic2]) > 0) :
							sim_by_op_by_candidate[candidate][topic1] = alpha_1/alpha_max
						elif (int(mine[topic1]) == 0) and (int(other[topic2]) < 0) :
							sim_by_op_by_candidate[candidate][topic1] =  alpha_1/alpha_max
						elif (int(mine[topic1]) == 0) and (int(other[topic2]) == 0) :
							sim_by_op_by_candidate[candidate][topic1] = alpha_0/alpha_max
						elif (int(mine[topic1]) > 0) and (int(other[topic2]) > 0) :
							sim_by_op_by_candidate[candidate][topic1] =  alpha_2/alpha_max
						elif (int(mine[topic1]) > 0) and (int(other[topic2]) == 0) :
							sim_by_op_by_candidate[candidate][topic1] =  alpha_3/alpha_max
						elif (int(mine[topic1]) > 0) and (int(other[topic2]) < 0) :
							sim_by_op_by_candidate[candidate][topic1] = alpha_1/alpha_max
						elif (int(mine[topic1]) < 0) and (int(other[topic2]) > 0) :
							sim_by_op_by_candidate[candidate][topic1] = alpha_0/alpha_max
						elif (int(mine[topic1]) < 0) and (int(other[topic2]) == 0) :
							sim_by_op_by_candidate[candidate][topic1] =  alpha_1/alpha_max
						elif (int(mine[topic1]) < 0) and (int(other[topic2]) < 0) :
							sim_by_op_by_candidate[candidate][topic1] = alpha_0/alpha_max
		# foreach topic get the candidates who have the colsest opinion to mine
		for topic in mine:
			for cand in sim_by_op_by_candidate:
				if topic in sim_by_op_by_candidate[cand]:
					if sim_by_op_by_candidate[cand][topic] > max_similarity_by_ops[topic]:
						max_similarity_by_ops[topic] = sim_by_op_by_candidate[cand][topic]
						list_of_yes[topic] = cand
		list_vote = {}
		for candidate in self.user.listCandidates:
			for topic in list_of_yes:
				if list_of_yes[topic].idu == candidate.idu:
					list_vote[str(candidate)] = True
				if list_of_yes[topic].idu != candidate.idu:
					list_vote[str(candidate)] = False 	
		return list_vote


	def stratgey_candidate_actions_topic_best_tweet(self): 
		max_action_by_topic = {}
		actions_by_candidate_by_topic ={}
		list_of_yes = {}
		mine = self.user.opinion()
		for topic in mine:
			max_action_by_topic[topic] = 0
		actions_by_candidate_by_topic={ }
		mine = self.user.opinion()
		for candidate in self.user.listCandidates:
			actions_by_candidate_by_topic[candidate]={}
			for topic in mine :		
				actions_by_candidate_by_topic[candidate][topic]= 0
				tweets = candidate.tweets
				for tweet in tweets:
					if topic in tweets[tweet].topics:
						sum_act = tweets[tweet].nb_likes +tweets[tweet].nb_replies +tweets[tweet].nb_retweets
						if sum_act != 0:
							new_val = (0.15*tweets[tweet].nb_likes +0.35*tweets[tweet].nb_replies +0.5*tweets[tweet].nb_retweets)/sum_act
							if actions_by_candidate_by_topic[candidate][topic] < new_val:
								actions_by_candidate_by_topic[candidate][topic] = new_val						
		for topic in mine:
			for cand in actions_by_candidate_by_topic:
				if topic in actions_by_candidate_by_topic[cand]:
					if actions_by_candidate_by_topic[cand][topic] > max_action_by_topic[topic]:
						max_action_by_topic[topic] = actions_by_candidate_by_topic[cand][topic]
						list_of_yes[topic] = cand
		list_vote = {}
		for candidate in self.user.listCandidates:
			for topic in list_of_yes:
				if list_of_yes[topic].idu == candidate.idu:
					list_vote[str(candidate)] = True
				if list_of_yes[topic].idu != candidate.idu:
					list_vote[str(candidate)] = False 	
		return list_vote
		""" 	def stratgey_candidate_actions_topic_all_tweets(self): 
		max_similarity_by_ops = {}
		sim_by_op_by_candidate ={}
		list_of_yes = {}
		mine = self.user.opinion()
		for topic in mine:
			max_similarity_by_ops[topic] = 0
		sim_by_op_by_candidate={ }
		nbr_by_op_by_candidate={ }
		mine = self.user.opinion()
		for candidate in self.user.listCandidates:
			sim_by_op_by_candidate[candidate]={}
			nbr_by_op_by_candidate[candidate]={}
			for topic in mine :			
				tweets = candidate.tweets
				sim_by_op_by_candidate[candidate][topic] = 0
				nbr_by_op_by_candidate[candidate][topic] = 0
				for tweet in tweets:
					if topic in tweets[tweet].topics:
						sum_act = tweets[tweet].nb_likes +tweets[tweet].nb_replies +tweets[tweet].nb_retweets
						if sum_act != 0:
							sim_by_op_by_candidate[candidate][topic] += (0.15*tweets[tweet].nb_likes +0.35*tweets[tweet].nb_replies +0.5*tweets[tweet].nb_retweets)/sum_act
						nbr_by_op_by_candidate[candidate][topic] += 1
		for candidate in sim_by_op_by_candidate:
			for topic in sim_by_op_by_candidate[candidate]:
				if nbr_by_op_by_candidate[candidate][topic] !=0:
					sim_by_op_by_candidate[candidate][topic] = sim_by_op_by_candidate[candidate][topic] / nbr_by_op_by_candidate[candidate][topic]
				else : 
					sim_by_op_by_candidate[candidate][topic] = 0
		for topic in mine:
			for cand in sim_by_op_by_candidate:
				if topic in sim_by_op_by_candidate[cand]:
					if sim_by_op_by_candidate[cand][topic] > max_similarity_by_ops[topic]:
						max_similarity_by_ops[topic] = max_similarity_by_ops[topic]
						list_of_yes[topic] = cand
		list_vote = {}
		
		for candidate in self.user.listCandidates:
			for topic in list_of_yes:
				if list_of_yes[topic].idu == candidate.idu:
					list_vote[str(candidate)] = True
				if list_of_yes[topic].idu != candidate.idu:
					list_vote[str(candidate)] = False 	
		return list_vote
		 """
	def stratgey_candidate_actions_topic_all_tweets(self): 
		max_similarity_by_ops = {}
		sim_by_op_by_candidate ={}
		list_of_yes = {}
		mine = self.user.opinion()
		for topic in mine:
			max_similarity_by_ops[topic] = 0
		sim_by_op_by_candidate={ }
		nbr_by_op_by_candidate={ }
		mine = self.user.opinion()
		for candidate in self.user.listCandidates:
			sim_by_op_by_candidate[candidate]={}
			nbr_by_op_by_candidate[candidate]={}
			for topic in mine :			
				tweets = candidate.tweets
				sim_by_op_by_candidate[candidate][topic] = 0
				nbr_by_op_by_candidate[candidate][topic] = 0
				for tweet in tweets:
					if topic in tweets[tweet].topics:
						sum_act = tweets[tweet].nb_likes +tweets[tweet].nb_replies +tweets[tweet].nb_retweets
						if sum_act != 0:
							sim_by_op_by_candidate[candidate][topic] += (0.15*tweets[tweet].nb_likes +0.35*tweets[tweet].nb_replies +0.5*tweets[tweet].nb_retweets)/sum_act
						nbr_by_op_by_candidate[candidate][topic] += 1
		for candidate in sim_by_op_by_candidate:
			for topic in sim_by_op_by_candidate[candidate]:
				if nbr_by_op_by_candidate[candidate][topic] !=0:
					sim_by_op_by_candidate[candidate][topic] = sim_by_op_by_candidate[candidate][topic] / nbr_by_op_by_candidate[candidate][topic]
				else : 
					sim_by_op_by_candidate[candidate][topic] = 0
		mean_cv = {}
		topic_cv = {}
		for topic in mine:
			topic_cv[topic] = []
			list_of_yes[topic] = []
		for topic in mine:
			for candidate in sim_by_op_by_candidate:
				if topic in sim_by_op_by_candidate[candidate]:
					
					topic_cv[topic].append(sim_by_op_by_candidate[candidate][topic])
		for topic in topic_cv : 
			mean_cv[topic] = statistics.median(topic_cv[topic])

		for topic in mine:
			for candidate in sim_by_op_by_candidate:
				if topic in sim_by_op_by_candidate[candidate]:
					if sim_by_op_by_candidate[candidate][topic] > mean_cv[topic]:
						list_of_yes[topic].append(candidate)
		list_vote = {}
		
		for candidate in self.user.listCandidates:
			for topic in list_of_yes:
				for cand in list_of_yes[topic]:
					if cand.idu == candidate.idu:
						list_vote[str(candidate)] = True
					if cand.idu != candidate.idu:
						list_vote[str(candidate)] = False 	
		return list_vote


#need to check it
	def stratgey_candidate_actions_topic_all_tweets_and_cv(self,weight): 
		self.compute_cv()
		max_similarity_by_ops = {}
		sim_by_op_by_candidate ={}
		list_of_yes = {}
		mine = self.user.opinion()
		for topic in mine:
			max_similarity_by_ops[topic] = 0
		sim_by_op_by_candidate={ }
		nbr_by_op_by_candidate={ }
		mine = self.user.opinion()
		for candidate in self.user.listCandidates:
			sim_by_op_by_candidate[candidate]={}
			nbr_by_op_by_candidate[candidate]={}
			for topic in mine :			
				tweets = candidate.tweets
				sim_by_op_by_candidate[candidate][topic] = 0
				nbr_by_op_by_candidate[candidate][topic] = 0
				for tweet in tweets:
					if topic in tweets[tweet].topics:
						sum_act = tweets[tweet].nb_likes +tweets[tweet].nb_replies +tweets[tweet].nb_retweets
						if sum_act != 0:
							sim_by_op_by_candidate[candidate][topic] += (0.15*tweets[tweet].nb_likes +0.35*tweets[tweet].nb_replies +0.5*tweets[tweet].nb_retweets)/sum_act
						nbr_by_op_by_candidate[candidate][topic] += 1
		for candidate in sim_by_op_by_candidate:
			for topic in sim_by_op_by_candidate[candidate]:
				if nbr_by_op_by_candidate[candidate][topic] !=0:
					sim_by_op_by_candidate[candidate][topic] = sim_by_op_by_candidate[candidate][topic] / nbr_by_op_by_candidate[candidate][topic]
				else : 
					sim_by_op_by_candidate[candidate][topic] = 0
		cumulated = {}
		for candidate in sim_by_op_by_candidate:
			cumulated[candidate] = {}
			for topic in sim_by_op_by_candidate[candidate]:
				cumulated[candidate][topic] = (1-weight) * sim_by_op_by_candidate[candidate][topic] + weight * self.user.dict_cv[candidate]
		
		for topic in mine:
			for cand in cumulated:
				if topic in cumulated[cand]:
					if cumulated[cand][topic] > 0.5:
						list_of_yes[topic] = cand
		list_vote = {}
		
		for candidate in self.user.listCandidates:
			for topic in list_of_yes:
				if list_of_yes[topic].idu == candidate.idu:
					list_vote[str(candidate)] = True
				if list_of_yes[topic].idu != candidate.idu:
					list_vote[str(candidate)] = False 	
		return list_vote
			
			

	    

class User():
	def __init__(self, idu, username, nb_followings, nb_followers):
		self.dict_os_vote={}
		self.voteAgent=""
		self.dict_cv={}
		self.sender = {}
		self.dict_os_inter={}
		self.listCandidates={}
		self.listLeaders=[]
		self.isleader=False
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
			psi = 0
		else :
			psi=(actions[0]*0.15+actions[1]*0.35+actions[2]*0.5)/(actions[0]+actions[1]+actions[2])
		return psi	
	#opinions de l'utilisateur à propos de ses topics(lkol)	
	def opinion(self):
		#dtopic{"topic":opinion}
		dtopics = {}	
		for idt, tweet in self.tweets.items():
			for topic in tweet.topics:
				if not (topic == '0'):
					if topic not in dtopics:
						dtopics[topic] = tweet.opinion
					else :
						dtopics[topic] = dtopics[topic] + tweet.opinion
		return dtopics
	
	def local_vote_majority(self):
		sorted_list_candidates = {}
		cvs = []
		for candidate in self.dict_cv:
			cvs.append(self.dict_cv[candidate])

		for candidate in self.dict_cv:
			cv = self.dict_cv[candidate]
			sorted_list_candidates[str(candidate)] = cv> statistics.median(self.dict_cv.values())	
		return sorted_list_candidates
	def Opinion_Similarity(self,user2opinions):
            #kol marra na3mlou lproduit binet'hom: lproduit 7asb les règles d'influence: 
            # No influence: <0.1
            # low Influence : [0.1,0.5]
            # Medium Influence: [0.5,0.9]
            #  High Influence: > 0.9
            os = 0
            user1opinions=self.opinion()
            
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
		
