import pandas as pd
from tools import strip_accents


def get_constant_data():

	# get neighborhoods names and codes
	code_neighborhoods = get_codes()

	try:
		print("loading neighborhood_const.xlsx")
		DB_raw = pd.ExcelFile("data/suplement_inputs/neighborhood_const.xlsx")
		print("file found! reading constant data")
		DB = DB_raw.parse("Sheet1") #choose a sheet and parse it...
		#print(DB)
		return DB, code_neighborhoods
		
	except FileNotFoundError:
			print("file not found... generating neighborhood_const.xlsx")
			generate_constant_data(code_neighborhoods)
			get_constant_data()


def generate_constant_data(code_neighborhoods):

	fixed_data_dict = dict([]) # keys: indicator_names, values: dict containing indicator values where the keys are neighborhood_name 
	fixed_data_dict["Name"] = [name for name in code_neighborhoods.keys()]
	fixed_data_dict["Code"] = [code_neighborhoods[name] for name in code_neighborhoods.keys()]
	fixed_data_dict = add_population(fixed_data_dict) 
	fixed_data_dict = add_geograph_socioeconom(fixed_data_dict) 
	fixed_data_dict = add_coords(fixed_data_dict)

	#write the data base
	df = pd.DataFrame(fixed_data_dict)
	df.to_excel("data/suplement_inputs/neighborhood_const.xlsx")

def add_population(fixed_data_dict):

	DB = pd.ExcelFile("data/suplement_inputs/pop_bairros_Rec_2019.xlsx") #open the data base
	popDB = DB.parse("Plan1") #choose a sheet and parse it...
	fixed_data_dict["population_2019"] = [] # initialize the new column
	for name in fixed_data_dict["Name"]:
		missingData = True
		for i in range(len(popDB)):
			if strip_accents(popDB.iloc[i,0]).upper() == name:
				missingData = False
				orig = str(popDB.iloc[i,1])
				fixed_data_dict["population_2019"].append(int(orig.replace("\xa0","")))
		if(missingData):
			fixed_data_dict["population_2019"].append(-1)

	return fixed_data_dict

def add_geograph_socioeconom(fixed_data_dict): 

	DB_indicator_ref = pd.ExcelFile("data/suplement_inputs/input_fixed.xlsx") #open the data base
	DB_ind = DB_indicator_ref.parse('Sheet1')
	idx = 0
	#initialize the new columns
	for j in DB_ind: # loop over each indicator
		if(idx > 0): # jump the name column of DB_ind
			fixed_data_dict[j] = []
		idx += 1
	# fill the new columns
	for name in fixed_data_dict["Name"]:
		idx = 0
		missingData = True
		for j in DB_ind:
			if(idx > 0):
				for i in range(len(DB_ind)): # search for 'name' row
					if strip_accents(DB_ind.iloc[i,0]).upper() == name:
						missingData = False
						fixed_data_dict[j].append(DB_ind.iloc[i,idx])
				if(missingData):
					fixed_data_dict[j].append(-1)
			idx += 1

	return fixed_data_dict
		
def get_codes():
	# read the file containing Recife's neighborhoods codes
	DB_PE = pd.read_csv("data/suplement_inputs/bairrosCod.csv", encoding = 'latin-1')
	col_raw = DB_PE['cod'] # get raw data...
	# initialize the code dict
	code_neighborhoods = dict([])
	for row in col_raw:
		row_split = row.split(',') # split this to get two columns: [code, name]
		name = row_split[1].replace('"','') # get name (key)
		code = row_split[0] # get code
		code_neighborhoods[strip_accents(name).upper()] = code

	return code_neighborhoods

def add_coords(fixed_data_dict):
	# source: inloco
	fixed_data_dict["lat"] = []
	fixed_data_dict["long"] = []
	DB = pd.read_csv("data/suplement_inputs/bairros_localizacao.csv", encoding='latin-1') #open the data base
	#print(DB)
	for name in fixed_data_dict["Name"]:
		hasValue = False
		for i in range(len(DB)):
			if strip_accents(DB.iloc[i,0]).upper() == name:
				fixed_data_dict["long"].append(float(DB.iloc[i,1]))
				fixed_data_dict["lat"].append(float(str(DB.iloc[i,2]).replace(";","")))
				hasValue = True
		if not hasValue:
			print(name + " coords not found")

	return fixed_data_dict