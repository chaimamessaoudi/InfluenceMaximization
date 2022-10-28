import mesa
import networkx as nx
import numpy as np
class VoteManagerAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model,community_subgraph):
        super().__init__(unique_id, model)
        self.community_subgraph = community_subgraph
        self.listCandidates = []
        self.dict_voters_by_candidate = {}
        self.dict_voter_candidates={}
        self.dict_voter_decision={}
        self.list_leaders=[]
        self.results={}
        print(self.community_subgraph)
        candidates = self.compute_communities_candidates(self.compute_pr_for_community())    
        print("nbr of candidates "+str(len(candidates))) 
        self.dict_voters_by_candidate= self.voter_list_for_candidates(candidates,self.community_subgraph)
        self.dict_voter_candidates= self.voter_list_for_candidate(self.dict_voters_by_candidate)
        self.dict_voters_by_candidate = {}
    def aggregate_votes(self,votes):
        for cand in votes:
            if str(cand) not in self.results:
                self.results[str(cand)]={}
                self.results[str(cand)]['True'] = 0 
                self.results[str(cand)]['False'] = 0 
                self.results[str(cand)][str(votes[cand])]+=1
            else :   
                self.results[str(cand)][str(votes[cand])]+=1

    def step(self):
        # The agent's step will go here.
        # For demonstration purposes we will print the agent's unique_id
        
        print("Hi, I am Vote Manager Agent" + str(self.unique_id) + ".")
        print(self.results)
        for cand in self.results:
            nbr_yes = self.results[cand]['True']
            nbr_no = self.results[cand]['False']
            if nbr_yes >= (nbr_yes+nbr_no)/2:
                print(str(cand) +" is a leader")
                self.list_leaders.append(cand)
        #print(len(self.dict_voter_candidates))
        file = open("leaders.txt","w")
        for list in self.list_leaders:         
            file.write(str(list)+",")
        file.close()
        

    def voter_list_for_candidates(self,candidates,community):
        #return the list of voters of a candidate {candidate:[{voter:[distance,os]}]}, 
        list_voters_for_candidates = {}
        radius = 6
        for candidate in candidates:		  
            list_voters = {}
            
            neighbours = self.get_neighbours(candidate,community) 
            
            for neighbour in neighbours:
                list_voters[neighbour] = [1,[candidate]]
                            
            for depth in range(2,radius+1):
                #print("this step is done")
                
                for voter in list_voters.copy():
                    path = []
                    #print("maybe this one?...")
                    node_neighbours = self.get_neighbours(voter,community)		
                    #print(node_neighbours)			
                    for node_neighbour in node_neighbours: 
                        if node_neighbour not in list_voters : 
                            path = nx.algorithms.shortest_paths.generic.shortest_path(community,source=node_neighbour,target=candidate)
                            #print(path)
                            list_voters[node_neighbour] = [depth,path]
                            #print("am here")
            
                #print("no i am here")
            list_voters_for_candidates[candidate] = 	list_voters	
        return list_voters_for_candidates	#{candidate:{voter:[distance,os]}}

    #bech nkharjou biha el liste voters elli yvotiw el koll w mba3ed 3ala koll voter nkharjou el liste mta3 les candidats mte3ou
    #search for a unique voters for each candidate and then construct a dict {voter : {candidate,os,distance}}
    def voter_list_for_candidate(self,list_voters_for_candidates):		
        dict_voters ={}
        for candidate in list_voters_for_candidates:
            for voter in list_voters_for_candidates[candidate]:		
                if(voter not in dict_voters) :
                    dict_voters[voter] = {} 
                dict_voters[voter][candidate] = list_voters_for_candidates[candidate][voter]

        for voter in dict_voters:
            for candidate in dict_voters[candidate]:
                if voter == candidate:
                    dict_voters[voter][candidate]=[1,[candidate]]
        return dict_voters

    def compute_communities_candidates(self,community_pr):
        np_pagerank = np.fromiter(community_pr.values(), dtype=float)
        candidates_with_average = []
        average_pagerank = np.average(np_pagerank)
        for user,pagerank in community_pr.items():
            if pagerank >= average_pagerank : 
                candidates_with_average.append(user)
        #print("canditates for "+str(self.jid)+"  : "+str(candidates_with_average))
        return candidates_with_average	
    def get_neighbours(self,node,community):
        neighbours = community.predecessors(node) 
        return neighbours

        
    def compute_pr_for_community(self):
        return nx.pagerank(self.community_subgraph, alpha=0.9, max_iter=1000, personalization= dict(self.community_subgraph.nodes(data="weight")))
