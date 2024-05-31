import serial
import ast

port = '/dev/ttyS0'
baud = 115200

ser = serial.Serial(port,baud, timeout=1)

while True:
	data = ser.readline()
	data = data.decode("utf-8").replace('\r','')
	data = data.replace('\n','')
	if len(data) > 2:
		data = ast.literal_eval(data)
		print(data)
	
