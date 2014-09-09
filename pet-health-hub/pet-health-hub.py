import sys
import serial
import Queue
import time
import thread

import Tkinter as tk

from simple_salesforce import Salesforce

raw_data = ''

def usage():
	print 'usage:   pet-health <serial-device> <baud-rate>'
	print 'example1: pet-health /dev/tty 9600'
	print 'example2: python pet-health.py /dev/tty.usbmodemfd13111 9600'
	quit()

def read_data():
	print 'Read data...'
	print_output('Read data')
	serArduino.write('D\n')

def upload_data():
	global raw_data
	print 'Upload data...'
	print_output('Upload data')
	print_output('Logging into Saleforce')
	sf = Salesforce(username='oliver@pet.app', password='China!2015', security_token='lCvQJCBw4eRMA3qxXZxOKcxK')
	print_output('Creating daylog')
	result = sf.Daylog__c.create({'Device__c':'a01w0000029IwHZ','Raw__c':raw_data})
	print_output(result)
	raw_data = ''
	# Go to SFDC

def reset_device():
	print 'Reset device...'
	print_output('Reset device')
	serArduino.write('R\n')

# Main
if len(sys.argv) != 3:
	usage()

try:
	baudRate = int(sys.argv[2])
	pass
except Exception, e:
	usage()

serArduino = serial.Serial(sys.argv[1], sys.argv[2])
serArduino.flushInput()
qOutput = Queue.Queue()

# Example <log message='Writing message to SD card'/>
def extract_payload(trimmedline):
	startPosition = trimmedline.find('=')
	return trimmedline [startPosition+1:-2]

def receive():
	global raw_data
	while 1:
		line = serArduino.readline()
		trimmedline = line[:-2]
		print 'Arduino ' + trimmedline
		if trimmedline.startswith('<log'):
			qOutput.put('LOG: '+extract_payload(trimmedline))
		else:
			qOutput.put('RAW: '+trimmedline)
			raw_data += line

def receive_dummy():
	counter = 1
	while 1:
		qOutput.put('Message ' + str(counter))
		print 'Message ' + str(counter)
		counter = counter + 1
		time.sleep(2)

def log():
	try:
		while 1:
			line = qOutput.get_nowait()
			print_output(line)
	except Queue.Empty:
		pass
	txtOutput.after(200, log)

def print_output(line):
	txtOutput.config(state=tk.NORMAL)
	txtOutput.insert(tk.END, str(line) + '\n')
	txtOutput.see(tk.END)
	txtOutput.config(state=tk.DISABLED)

# Create UI
root = tk.Tk()
frmMain = tk.Frame(root)
frmMain.pack(expand=1, fill=tk.BOTH)
btnForward = tk.Button(frmMain, text='Read Data', command=read_data, padx=10, pady=5, width=20)
btnForward.pack(anchor=tk.S)
btnForwardStep = tk.Button(frmMain, text='Upload Data', command=upload_data, padx=10, pady=5, width=20)
btnForwardStep.pack(anchor=tk.S)
btnStop = tk.Button(frmMain, text='Reset Device', command=reset_device, padx=10, pady=5, width=20)
btnStop.pack(anchor=tk.S)
txtOutput = tk.Text(frmMain, takefocus=0, state=tk.DISABLED, bd=0, padx=5, pady=5)
txtOutput.pack(anchor=tk.S, fill=tk.BOTH, expand=tk.YES)

root.title('Pet Health Hub');

log()

thread.start_new_thread(receive, ());
tk.mainloop();
