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
		time.sleep(2)
		self.asking = False
		self.last_weight = 0
		self.time = time.time() 
	def read_weight(self):
#		self.asking=True
		self.ser.write('1')
		adc = int(self.ser.readline().rstrip())
#		self.asking = False
		weight = self.slope*adc+self.intercept
#		print weight
		self.last_weight = weight
		return weight
	def set_zero(self):
#		self.asking=True
#		self.ser.write('1')
#		adc = int(self.ser.readline().rstrip())
#		self.asking=False
		if (time.time()-self.time>1):
			print "entre"
			self.time = time.time()
#			print self.intercept
			new_intercept = -(self.last_weight-self.intercept)
			self.intercept = new_intercept
#			print self.intercept
			fo = open(path+"data/intercept.txt", "w")
			fo.write(str(self.intercept))
			fo.close()
		else:
			print "no pude entrar"
