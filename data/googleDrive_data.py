import pandas as pd
import numpy as np
import math

import os
from datetime import timedelta, date
import csv

from tools import strip_accents


'''
1 - Check the last date we have from data_repo directory
2 - After this checkup, start reading from PCR's database at google drive
3 - collect new data and  write consolidated information for each neighborhood
'''
def update_covid_data_bairros(code_neighborhoods, start_date):

	# 1 - Check the last date we have on the data repository
	print("\nchecking the last date in which the repository was updated...")
	lastDate = check_data_last_date(start_date)
	update_start_date = lastDate

	# 2 - After this checkup, start reading from PCR's database from google drive
	print("updating data up to " + str(date.today()))
	update_ = False # assume that there is nothing to update...
	delta = timedelta(days = 1)
	end_date = []
	dist_with_confirmed_cases = dict([])
	dist_uti = dict([])
	dist_enf = dict([]) 
	dist_death = dict([])
	while lastDate <= date.today():
		DB_PE = []
		try:
			date_formt = str(lastDate.strftime("%Y_%m_%d")) # formatted date
			print("processing " + str(date_formt))
			DB_PE = pd.ExcelFile("data/PCR Dados Gonçalves/Base_Covid-19_" + date_formt + "_VF.xlsx")
		except FileNotFoundError:
			print(str(lastDate) + " file not found")
			return lastDate

		# update is needed...
		update_ = True
		# fix some district names in the raw data 
		DB_PE = DB_PE.parse("Dados") #choose a sheet and parse it...
		DB_PE = DB_PE.replace({'NMBAIRRO': {'ILHA JOANA BEZERRA':'JOANA BEZERRA'}})
		DB_PE = DB_PE.replace({'NMBAIRRO': {'RECIFE':'BAIRRO DO RECIFE'}})
		DB_PE = DB_PE.replace({'NMBAIRRO': {'ALTO SANTA TERESINHA':'SANTA TEREZINHA'}})
		DB_PE = DB_PE.replace({'NMBAIRRO': {'PAU FERRO':'PAU-FERRO'}})

		# 3 - collect new data and write consolidated information for each neighborhood
		# initialize the data base that will be filled with data from lastDate
		current_DB = dict([])
		current_DB["Name"] = []
		current_DB["Code"] = []#[code_neighborhoods[nm] for nm in code_neighborhoods.keys()]
		current_DB["Active_cases"] = []

		# gather new information
		cities = DB_PE.groupby(['NMBAIRRO','CSTATUS'])
		for name, group in cities:
			if(name[1] == 'CONFIRMADO' and strip_accents(name[0]).upper() in code_neighborhoods.keys()):
				total_active_cases = 0
				total_active_cases += np.sum(sum([group['NMEVOLUCAO'] == 'ISOLAMENTO DOMICILIAR'])) 
				total_active_cases += np.sum(sum([group['NMEVOLUCAO'] == 'INTERNADO LEITO DE ISOLAMENTO']))
				#dist_enf[strip_accents(name[0]).upper() + str(start_date)] = np.sum(sum([group['NMEVOLUCAO'] == 'INTERNADO LEITO DE ISOLAMENTO']))  
				total_active_cases += np.sum(sum([group['NMEVOLUCAO'] == 'INTERNADO UTI']))  
				#dist_uti[strip_accents(name[0]).upper() + str(start_date)] = np.sum(sum([group['NMEVOLUCAO'] == 'INTERNADO UTI']))  
				total_active_cases += np.sum(sum([group['NMEVOLUCAO'] == 'INTERNADO, MAS NÃO ESTÁ EM LEITO DE ISOLAMENTO']))
				#dist_with_confirmed_cases[strip_accents(name[0]).upper() + str(start_date)] = total_active_cases
				#dist_death[strip_accents(name[0]).upper() + str(start_date)] = np.sum(sum([group['NMEVOLUCAO'] == 'ÓBITO'])) 

				# add a row in the data base
				if strip_accents(name[0]).upper() in code_neighborhoods.keys():
					current_DB["Name"].append(strip_accents(name[0]).upper())	
					current_DB["Code"].append(code_neighborhoods[strip_accents(name[0]).upper()])		
					current_DB["Active_cases"].append(total_active_cases)		

		#write the new data base
		df = pd.DataFrame(current_DB)
		df.to_excel("data/data_repo/pcr_data_" + str(lastDate) + ".xlsx")

		lastDate += delta # next date

	
def check_data_last_date(start_date):
	checking = True
	date_ = start_date
	delta = timedelta(days = 1)
	while checking:
		try:
			DB_PE = pd.ExcelFile("data/data_repo/pcr_data_" + str(date_) + ".xlsx")
		except FileNotFoundError:
			print("Last available data from " + str(date_ - delta))
			return date_ # return the date to start the data update

		date_ += delta # next date









