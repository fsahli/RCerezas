import csv

def create_cardID_Name_dict():
	with open('NombreTarjeta.csv', 'rb') as csvfile:
		NT = csv.reader(csvfile, delimiter=',', quotechar='|')
		dict={}
		for row in NT:
			dict['000'+row[0]]=row[2]+' '+row[3]

	return dict
