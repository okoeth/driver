import sys
import serial

def usage():
	print ('usage:   speedy-bell.py <serial-device> <baud-rate>')
	print ('example1: python speedy-bell.py COM5 9600')
	quit()

# Main
if len(sys.argv) != 3:
	usage()

try:
	baudRate = int(sys.argv[2])
	pass
except Exception:
	usage()

ser = serial.Serial(sys.argv[1], sys.argv[2])
ser.flushInput()

print ('Start reading bytes\n')

while 1:
	byte = ser.read()
	print (byte)
