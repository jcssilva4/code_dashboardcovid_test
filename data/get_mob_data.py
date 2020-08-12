import pandas as pd
import numpy as np
import math
import unicodedata
import pyproj
import os
from datetime import timedelta, date
import csv
from tools import strip_accents

def get_ODs(listNames):
	OD_matrices = dict([])
	_listNames_ = []
	matrices_types = ['max_after_inloco','a_pe','bicicleta','carro','motocicleta','outros','todos_modos','transporte_publico_coletivo','transporte_publico_individual']
	OD_assocIdxs = dict([])
	for matType in  matrices_types:
		# read the excel file
		#print ("reading " + matType + " matrix: ") # we use worldBank[year-1] data to predict label[year]
		DB = pd.ExcelFile("data/OD_matrices/Matrix_rec_" + matType + ".xlsx") #open the data base
		ODmat = DB.parse("Sheet1") #choose a sheet and parse it...
		if matType == 'max_after_inloco':
			ODmat = ODmat.replace({'Joana Bezerra':'Ilha Joana Bezerra'})
			ODmat = ODmat.replace({'Bairro do Recife':'Recife'})
			ODmat = ODmat.replace({'Santa Terezinha':'Alto Santa Terezinha'})
			ODmat = ODmat.replace({'Pau-Ferro':'Pau-Ferro'})
			_listNames_ = ODmat.columns[1:] # List of vertices names (cities names) - vertex attribute
			OD_matrices[matType] = ODmat
			assocIdxs = getAssocIdxs(listNames,_listNames_,matType)
			OD_assocIdxs[matType] = assocIdxs
		else:
			ODmat = ODmat.replace({'Ilha Joana Bezerra':'Joana Bezerra'})
			ODmat = ODmat.replace({'Recife':'Bairro do Recife'})
			ODmat = ODmat.replace({'Alto Santa Terezinha':'Santa Terezinha'})
			ODmat = ODmat.replace({'Pau Ferro':'Pau-Ferro'})
			ODmat = ODmat.fillna(0) # replace NaN values with 0
			_listNames_ = [s for s in ODmat.iloc[:,1]]
			assocIdxs = getAssocIdxs(listNames,_listNames_,matType)
			OD_assocIdxs[matType] = assocIdxs
			OD_matrices[matType] = ODmat

	return OD_matrices, OD_assocIdxs


def getAssocIdxs(listNames, _listNames_,matType):
	assocIdxs = []
	for i in listNames:
		i_detected = False
		count = 0
		for ii in _listNames_:
			if(strip_accents(ii).upper() == i):
				i_detected = True
				assocIdxs.append(count)
				break
			else:
				count += 1
		if not i_detected:
			print(i + " not found")

	return assocIdxs
