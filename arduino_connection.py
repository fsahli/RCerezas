import serial
import time
path = '/home/pi/RCerezas_v1/'
class Arduino:
	def __init__(self):
		fo = open(path+'data/intercept.txt','r')
		self.intercept = float(fo.read())
		fo.close()
		self.slope = 0.038107675647276
		self.ser = serial.Serial('/dev/ttyUSB0',9600)
		self.ser.write('1')
		self.asking = False
		self.last_weight = 0
	def read_weight(self):
#		self.asking=True
		self.ser.write('1')
		adc = int(self.ser.readline().rstrip())
#		self.asking = False
		weight = self.slope*adc+self.intercept
		print weight
		self.last_weight = weight
		return weight
	def set_zero(self):
#		self.asking=True
		self.ser.write('1')
		adc = int(self.ser.readline().rstrip())
#		self.asking=False
		self.intercept = -self.slope*adc
		fo = open(path+"data/intercept.txt", "w")
		fo.write(str(self.intercept))
		fo.close()
