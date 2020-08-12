import pandas as pd
from igraph import * # graph lib

def epidem_get_all(epidem_data, g, current_date):

	# get active cases
	DB_raw = pd.ExcelFile("data/data_repo/pcr_data_" + str(current_date) + ".xlsx")
	DB = DB_raw.parse("Sheet1") #choose a sheet and parse it...
	epidem_data["Active_cases"] = []
	for name in epidem_data["Name"]:
		row = DB.loc[DB["Name"] == name]
		if len(row):
			epidem_data["Active_cases"].append(int(row["Active_cases"]))
		else:
			epidem_data["Active_cases"].append(0)
	active_cases = epidem_data["Active_cases"]

	# get Force of Infection
	FOI = []
	for v in range(len(active_cases)): # loop over graph's vertices
		if(active_cases[v]>0):
			FOI.append(calculateFOI_singletonONLY(g, [v], active_cases))
		else:
			FOI.append(0)
	epidem_data["FOI"] = FOI

	return epidem_data


def calculateFOI_singletonONLY(g, vertices, active_cases):
	pop = g.vs["population"]
	Y = 0
	N = 0 
	if len(vertices) > 1:
		Y = sum([active_cases[v] for v in vertices])
		N = sum([pop[v] for v in vertices])
	else:
		Y = active_cases[vertices[0]]
		N = pop[vertices[0]]
	strength = g.strength(vertices = vertices, mode = "all", weights = g.es["weight"])
	mean_str = mean(strength)
	#print(mean_str)
	#print(mean_str*(Y/N))
	return mean_str*(Y/N)