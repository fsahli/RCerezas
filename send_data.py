#!/usr/bin/env python

import json
from datetime import datetime,timedelta
import random
import urllib2
import csv
from csv_gspread import *
import time

path = '/home/pi/RCerezas_v1/'
def send_data():

	fo = open(path+"data/IDlastbin_uploaded.txt", "r")
	IDlastbin_uploaded = int(fo.read())
	fo.close()
	print IDlastbin_uploaded
	fo = open(path+"data/IDlastbin.txt", "r")
	IDlastbin = int(fo.read())
	fo.close()
	print IDlastbin

	while IDlastbin_uploaded<IDlastbin:
		if internet_on():
			print "Internet on"
			filename= path+'data/Bin%d.csv' % (IDlastbin_uploaded+1)
			fcsv = open(filename)
			reader = csv.reader(fcsv)
			binID = reader.next()[0][4:]
			data = []

			for row in reader:
				    data.append({
					    'log_date':row[0],
					    'cardID':row[1],
					    'RUT':row[2],
					    'binID':binID,
					    'loggerID':1,
				    	    'weight':row[3]})

			req = urllib2.Request('http://web.ing.puc.cl/~fsahli1/api.php')
			req.add_header('Content-Type','application/json')

			response = urllib2.urlopen(req, json.dumps(data))

			print response.read()
			fo = open(path+"data/IDlastbin_uploaded.txt", "w")
			fo.write(str(IDlastbin_uploaded+1))
			fo.close()
			IDlastbin_uploaded+=1;
		else:
			print "Internet off"
		time.sleep(1)
								                              
