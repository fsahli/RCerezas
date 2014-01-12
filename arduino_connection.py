import serial

slope = 0.038107675647276
intercept = -1.42243458142442
def connect_to_Arduino():
	
	ser = serial.Serial('/dev/ttyUSB0',9600)
	return ser

def read_weight(ser):
	ser.write('1')
	adc = int(ser.readline().rstrip())
	weight = slope*adc+intercept
	return weight
