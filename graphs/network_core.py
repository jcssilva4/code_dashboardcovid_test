from igraph import * # graph lib
import pandas as pd
from data.get_mob_data import get_ODs


def generate_graph(const_db):

	print("Generating the network through mobility data...")
	listNames = [name for name in const_db["Name"]]
	OD_matrices, OD_assocIdxs = get_ODs(listNames) #dict
	# create the network
	nVertices = len(listNames) # get number of vertices
	u = 1
	l = 1 # initial l
	listEdges, listEdges_weights = get_edges_and_weights(nVertices, OD_matrices['max_after_inloco'], OD_assocIdxs['max_after_inloco'])
	g = Graph(directed = True)
	g.add_vertices(nVertices)
	g.add_edges(listEdges)
	# add node attributes
	g.vs["population"] =  [pop for pop in const_db["population_2019"]]
	g.vs["name"] = listNames
	g.vs["idx"] = range(nVertices)
	g.es["weight"] = listEdges_weights # set weights associated with each edge

	return g

def get_edges_and_weights(nVertices, ODmat, assoc_idxs):

	listEdges = [] # List of connections. 
	listEdges_weights = [] # Each connection is a weight representing the flux between two cities: the origin and the destination
	# get weighted edge list
	for orig in range(nVertices): # loop over all origins
		for dest in range(nVertices): # loop over all destinations
			listEdges.append([orig,dest])
			listEdges_weights.append(ODmat.iloc[assoc_idxs[orig],assoc_idxs[dest]])

	return listEdges, listEdges_weights