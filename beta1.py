#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pcd8544.lcd as lcd
import time, os, sys
from datetime import datetime
from readtest import readCard
from csv_gspread import *
import os.path
if not os.geteuid() == 0:
    sys.exit('Script must be run as root')

ON, OFF = [1, 0]


try:
	lcd.init()
	lcd.cls()
	lcd.set_contrast(180)
	lcd.backlight(OFF)
	lcd.centre_text(0,"Verificando Internet...")
	if internet_on():
		lcd.cls()
		lcd.centre_text(0,"Bajando Registro de nombres...")
		dowloadNombreTarjeta()
		cardID_Name = create_cardID_Name_dict()
		cardID_RUT = create_cardID_RUT_dict()
	else:
		lcd.cls()
		lcd.centre_text(0,"No hay internet...")
		if os.path.isfile('NombreTarjeta.csv'):
			lcd.cls()
			lcd.centre_text(0,"Ocupando registro antiguo...")
			cardID_Name = create_cardID_Name_dict()
			cardID_RUT = create_cardID_RUT_dict()
		else:
			lcd.cls()
			lcd.centre_text(0,"No hay registro de nombres")
			sys.exit('No hay registro de nombres')
#Verifica si el existe el archivo IDlastbin.txt y si no lo crea con un cero
	if not os.path.isfile('IDlastbin.txt'):
		fo = open("IDlastbin.txt", "w")
		fo.write("0")
		fo.close()
#Verifica si el existe el archivo IDlastbin_uploaded.txt y si no lo crea con un cero
	if not os.path.isfile('IDlastbin_uploaded.txt'):
		fo = open("IDlastbin_uploaded.txt", "w")
		fo.write("0")
		fo.close()
	while 1:
	#Lee desde el archivo la variable IDlastbin	
		fo = open("IDlastbin.txt", "r")
		IDbin = int(fo.read())+1
		fo.close()
	#Lee desde el archivo la variable IDlastbin_uploaded	
		fo = open("IDlastbin_uploaded.txt", "r")
		IDlastbin_uploaded = int(fo.read())
		fo.close()
#Verifica si es quedo un archivo temp sin guardar en bin.
		if os.path.isfile('temp.csv'):
			os.rename('temp.csv','Bin%d.csv' % IDbin)
			IDbin+=1
	#Crea el archivo temp.csv
		ftemp = open("temp.csv", "w")
		ftemp.write("Bin %d\n" % IDbin)
		ftemp.close()
		registro = []
		lcd.cls()
		lcd.centre_text(0,"Listo para leer")
		nroCajas = 0
		while nroCajas<=24:
#Espera hasta leer la tarjeta
			cardID=readCard()
#Si es que la tarjeta es para renovar el bin, sale del while y empieza de nuevo
			if cardID_RUT[cardID]=='nuevobin':
				break
#Verifica que no hayan pasado menos de dos minutos desde la ultima marca			
			cajas = [registro[i][0] for i in range(len(registro)) if registro[i][1]==cardID]
			if len(cajas)>0:
				last_caja_timestamp = datetime.strptime(cajas[-1].split(',')[0],"%Y-%m-%d %H:%M:%S")
				ahora = datetime.now()
				diff=(ahora-last_caja_timestamp).total_seconds()
			else:
				diff=130
			if diff<120:
				lcd.cls()
				lcd.centre_text(0,"Tienes que esperar 2 min. antes de la proxima caja")
#Registra la marca en la lista registro y en el archivo temp.
			else:
				timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
				registro.append([timestamp,cardID,cardID_RUT.get(cardID,'No asignado')])
				ftemp = open("temp.csv", "a")
				ftemp.write(timestamp+","+cardID+","+cardID_RUT.get(cardID,'No asignado')+"\n")
				ftemp.close()
				user_count = len(cajas)+1
				print user_count
				lcd.cls()
				lcd.centre_text(0,cardID_Name.get(cardID,'No asignado'))
				lcd.centre_text(3,"Cajas: "+str(user_count))
				nroCajas+=1
				lcd.centre_text(4,"%d/24 cajas" % nroCajas)
				print cardID
				print nroCajas
#Cuando se termina el bin o se pone la tarjeta nuevobin se mueve el archivo temp.csv a BinXX.csv. Se actualiza el ID del ultimo bin.
		os.rename('temp.csv','Bin%d.csv' % IDbin)
		fo = open("IDlastbin.txt", "w")
		fo.write(str(IDbin))
		fo.close()
		
except KeyboardInterrupt:
  pass
finally:
  lcd.cls()
  lcd.backlight(OFF)

