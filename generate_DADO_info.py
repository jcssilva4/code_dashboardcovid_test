import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import math as mth

from igraph import * # graph lib

from datetime import timedelta, date

# data
from data.googleDrive_data import update_covid_data_bairros
from constant_data import get_constant_data
# graphs
from graphs.network_core import generate_graph
# epidemic metrics
from epidem.compute_epidem_metrics import epidem_get_all

'''
from Input.math_epidem import calculateFOI
from Input.math_epidem import calculateFOI_diogo
from Input.math_epidem import get_vel_7over7
from Input.math_epidem import get_vel_1over7
from Input.transform_addData import transform_dat
from Input.get_mob_data import get_ODs
'''


# Get constant data dict
constant_db, code_neighborhoods = get_constant_data()

# update epidemic data
update_start_date = date(2020,5,6) # checkup starts from this period
update_end_date = update_covid_data_bairros(code_neighborhoods, update_start_date)

# compute epidemic metrics - Compute metrics assoacited with time varying data, writting the data base for each date
computing_metrics = True
delta = timedelta(days = 1)
current_date = update_start_date
g = []
graph_exists = False

while computing_metrics:

	print("checking epidem_data_" + str(current_date) + ".xlsx")

	try:
		# check if metrics were already computed for current_date
		DB_raw = pd.ExcelFile("data/data_repo/epidem_data_" + str(current_date) + ".xlsx")		

	except FileNotFoundError:

		if(current_date < update_end_date):

			print("new epidemic data avalilable, but not processed...UPDATE!")
			print("computing epidemic data for " + str(current_date))

			# initialize data dict
			epidem_data = dict([])
			epidem_data["Name"] = [name for name in constant_db["Name"]]
			epidem_data["Code"] = [code for code in constant_db["Code"]]
			epidem_data["latitude"] = [longi for longi in constant_db["long"]]
			epidem_data["longitude"] = [lat for lat in constant_db["lat"]]

			# generate graph
			if not graph_exists:
				g = generate_graph(constant_db)
				graph_exists = True

			# get epidemic metrics
			epidem_data = epidem_get_all(epidem_data, g, current_date)

			# write on disk
			#print(epidem_data)
			df = pd.DataFrame(epidem_data)
			df.to_excel("data/data_repo/epidem_data_" + str(current_date) + ".xlsx")
			current_date -= delta # you do this in order to check the file again...

		else:
			print("no new updates")
			computing_metrics = False

	current_date += delta






