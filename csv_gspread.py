import csv
import gspread
import urllib2
username = "francisco.sahli@gmail.com"
password = ""
	
def internet_on():
	try:
	        response=urllib2.urlopen('http://74.125.228.100',timeout=1)
		return True
	except urllib2.URLError as err: pass
	return False

def dowloadNombreTarjeta():	
	docid = "0AjXcKR-LHUJqdHhESGI5M0tDTnMyNk10WkUyV2pJNVE"
	client = gspread.login(username, password)
	spreadsheet = client.open_by_key(docid)

	worksheet=spreadsheet.get_worksheet(0)
	filename = 'NombreTarjeta.csv'
	with open(filename, 'wb') as f:
		writer = csv.writer(f) 
		writer.writerows(worksheet.get_all_values())


def create_cardID_Name_dict():
        with open('NombreTarjeta.csv', 'rb') as csvfile:
                NT = csv.reader(csvfile, delimiter=',', quotechar='|')
                dict={}
                for row in NT:
                        dict['000'+row[0]]=row[2]+' '+row[3]

        return dict

def create_cardID_RUT_dict():
        with open('NombreTarjeta.csv', 'rb') as csvfile:
                NT = csv.reader(csvfile, delimiter=',', quotechar='|')
                dict={}
                for row in NT:
                        dict['000'+row[0]]=row[1]

        return dict





