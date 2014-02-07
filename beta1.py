#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pcd8544.lcd as lcd
import time, os, sys
from datetime import datetime
from readtest import readCard
from csv_gspread import *
import os.path
from  arduino_connection import Arduino
import thread
import RPi.GPIO as GPIO

delay = 30
path='/home/pi/RCerezas_v1/'
if not os.geteuid() == 0:
    sys.exit('Script must be run as root')

ON, OFF = [1, 0]

asking_serial = False

def Int_shutdown(channel):  
	print "Shutdown"
	ard.ser.write('2')
	os.system("sudo shutdown -h now")
	lcd.cls()
	lcd.gotorc(1,0)
	lcd.text("Apagando")
	sys.exit("Apagando")
def Int_shutdown2(channel):
	print "Zero"
	while ard.asking:
		time.sleep(0.05)
	ard.set_zero()

def retrieve_weight(ard):
	print "Retrive Weight thread"
	while 1:
		ard.read_weight()
		time.sleep(0.1)
def display_weight(ard,lcd):
	print "Display Weight Thread"
	time.sleep(1)
	while 1:
		if not ard.asking:
			lcd.gotorc(5,0)
			lcd.text("%.2f kgs" % ard.last_weight)
			time.sleep(0.5)

try:
	try:
		print 'Iniciando botones'
		GPIO.setmode(GPIO.BCM) 
		GPIO.setup(25, GPIO.IN, pull_up_down = GPIO.PUD_UP)  
		GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)  
		GPIO.add_event_detect(25, GPIO.FALLING, callback = Int_shutdown, bouncetime = 2000)
		GPIO.add_event_detect(22, GPIO.FALLING, callback = Int_shutdown2, bouncetime = 1000)
	except:
		print 'Error al iniciar botones'
	try:
		print 'Iniciando LCD'
		lcd.init()
		lcd.cls()
		lcd.set_contrast(180)
		lcd.backlight(OFF)
	except:
		print 'Error al iniciar LCD'

	lcd.centre_text(0,"Verificando Internet...")
	print "Verificando Internet"
	if internet_on():
		lcd.cls()
		lcd.centre_text(0,"Bajando Registro de nombres...")
		print "Bajando registro de nombres"
		try:
			dowloadNombreTarjeta()
		except:
			print "No se pudo bajar registro"
	else:
		lcd.cls()
		lcd.centre_text(0,"No hay internet...")
		print "No hay internet"
	if os.path.isfile(path+'data/NombreTarjeta.csv'):
		lcd.cls()
		lcd.centre_text(0,"Ocupando registro...")
		print "Ocupando registro"
		cardID_Name = create_cardID_Name_dict()
		cardID_RUT = create_cardID_RUT_dict()
	else:
		lcd.cls()
		lcd.centre_text(0,"No hay registro de nombres")
		sys.exit('No hay registro de nombres')
#Verifica si el existe el archivo IDlastbin.txt y si no lo crea con un cero
	if not os.path.isfile(path+'data/IDlastbin.txt'):
		fo = open(path+"data/IDlastbin.txt", "w")
		fo.write("0")
		fo.close()
#Verifica si el existe el archivo IDlastbin_uploaded.txt y si no lo crea con un cero
	if not os.path.isfile(path+'data/IDlastbin_uploaded.txt'):
		fo = open(path+"data/IDlastbin_uploaded.txt", "w")
		fo.write("0")
		fo.close()
#Se conecta al arduino		
	try:
		ard=Arduino()	
		print ard.ser
		thread.start_new_thread( retrieve_weight ,(ard, ) )
		thread.start_new_thread( display_weight ,(ard, lcd, ) )
	except Exception,e:
		print 'Error al iniciar conexion serial'
		print str(e)
	while 1:
	#Lee desde el archivo la variable IDlastbin	
		fo = open(path+"data/IDlastbin.txt", "r")
		IDbin = int(fo.read())+1
		fo.close()
	#Lee desde el archivo la variable IDlastbin_uploaded	
		fo = open(path+"data/IDlastbin_uploaded.txt", "r")
		IDlastbin_uploaded = int(fo.read())
		fo.close()
#Verifica si es quedo un archivo temp sin guardar en bin.
		if os.path.isfile(path+'data/temp.csv'):
			os.rename(path+'data/temp.csv',path+'data/Bin%d.csv' % IDbin)
			fo = open(path+"data/IDlastbin.txt", "w")
			fo.write(str(IDbin))
			fo.close()
			IDbin+=1
	#Crea el archivo temp.csv
		ftemp = open(path+"data/temp.csv", "w")
		ftemp.write("Bin %d\n" % IDbin)
		ftemp.close()
		registro = []
		lcd.cls()
		lcd.gotorc(0,0)
		lcd.text("Listo para leer")
		nroCajas = 0
		while nroCajas<=24:
#Espera hasta leer la tarjeta
			cardID=readCard()
#Si es que la tarjeta es para renovar el bin, sale del while y empieza de nuevo
			if cardID_RUT[cardID]=='nuevobin':
				break
#Verifica que no hayan pasado menos de dos minutos desde la ultima marca			
			cajas = [[registro[i][0],registro[i][3]] for i in range(len(registro)) if registro[i][1]==cardID]
			print cajas
			if len(cajas)>0:
				last_caja_timestamp = datetime.strptime(cajas[-1][0].split(',')[0],"%Y-%m-%d %H:%M:%S")
				ahora = datetime.now()
				diff=(ahora-last_caja_timestamp).total_seconds()
				kgs=sum([cajas[i][1] for i in range(len(cajas))])
			else:
				diff=delay+10
				kgs=0
			if diff<delay:
				lcd.cls()
				lcd.centre_text(0,"Tienes que esperar %d seg antes de la proxima caja" % delay)
#Registra la marca en la lista registro y en el archivo temp.
			else:
				weight_aux=0.0
				weight = ard.last_weight
				while (abs(weight-weight_aux)>0.1 and weight<2.0):
					weight_aux=weight
					weight = ard.last_weight
					time.sleep(0.12)
				#	lcd.gotorc(5,0)
				#	lcd.text("%.2f kgs" % ard.read_weight())
				timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

				registro.append([timestamp,cardID,cardID_RUT.get(cardID,'No asignado'),weight])
				ftemp = open(path+"data/temp.csv", "a")
				ftemp.write(timestamp+","+cardID+","+cardID_RUT.get(cardID,'No asignado')+","+str(weight)+"\n")
				ftemp.close()
				user_count = len(cajas)+1
				print user_count
				lcd.cls()
				lcd.gotorc(0,0)
				lcd.text(cardID_Name.get(cardID,'No asignado'))
				lcd.gotorc(3,0)
				lcd.text("Cajas: "+str(user_count))
				nroCajas+=1
				lcd.gotorc(4,0)
				lcd.text("kg: %.2f" % (kgs+weight))
#				lcd.centre_text(4,"%d/24 cajas" % nroCajas)
				print cardID
				print nroCajas
#Cuando se termina el bin o se pone la tarjeta nuevobin se mueve el archivo temp.csv a BinXX.csv. Se actualiza el ID del ultimo bin.
		os.rename(path+'data/temp.csv',path+'data/Bin%d.csv' % IDbin)
		fo = open(path+"data/IDlastbin.txt", "w")
		fo.write(str(IDbin))
		fo.close()
		
except KeyboardInterrupt:
  pass
except Exception,e: 
	print str(e)
finally:
	lcd.cls()
	lcd.backlight(OFF)
	try:
		ard.ser.close()
	except:
		print "No se pudo cerrar con. serial"
