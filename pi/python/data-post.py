########################################################################
# phant-raspi.py
# Raspberry Pi Phant Example
# Jim Lindblom @ SparkFun Electronics
# July 7, 2014
#
# This example demonstrates how to post data to a phant server (e.g.
#   data.sparkfun.com) using python on a Raspberry Pi.
#   The RPi.GPIO module is used to enable I/O reading and writing.
#   Before running this script, make sure to update your public and
#   private keys (publicKey and privateKey vars).
#
# Development environment specifics:
#   Raspberry Pi rev 2
#
# This code is beerware; if you see me (or any other SparkFun employee)
# at the local, and you've found our code helpful, please buy us a round!
# Distributed as-is; no warranty is given.
########################################################################

import RPi.GPIO as GPIO  # RPi.GPIO used for GPIO reading/writing
import time              # time used for delays
import httplib, urllib   # http and url libs used for HTTP POSTs
import socket            # socket used to get host name/IP

import re
import requests
import serial

#################
## Phant Stuff ##
#################
server = "data.sparkfun.com" # base URL of your feed
publicKey1 = "2Jx7myNzj6uD37jNYA1M" # public key1, everyone can see this
privateKey1 = "GPyXGl6Ne2idvZlGK12R"  # private key1, only you should know
publicKey2 = "8dxAKN9l8JUKJlZrpQg6" # public key2, everyone can see this
privateKey2 = "pzrWZbnDg7cMe24jXk10"  # private key2, only you should know
fields = ["ID","v_bat","temperature", "humidity", "acceleration_x", "acceleration_y", "acceleration_z", "pressure", "status"] # Your feed's data fields

######################
## I/O Stuff & Misc ##
######################
buttonPin = 22 # Active-low button connected to Broadcom pin 22
switchPin = 23 # SPST switch connected to Broadcom pin 23
myname = socket.gethostname() # Send local host name as one data field

##############
## I/O Setup #
##############
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Button pin set as input w/ pull-up
GPIO.setup(switchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Switch set as input w/ pull-up

##########
## Serial ##
##########
ser = serial.Serial(

	port='/dev/ttyAMA0',
	baudrate = 9600,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=100
)

##########
## Loop ##
##########
print("Here we go! Press CTRL+C to exit")
T = time.strftime("%A %B %d, %Y %H:%M:%S %Z")
print T
try:
    # Loop until CTRL+C is pressed
    while 1:

	data_stream = ser.readline()
	print "\r\n"
	print data_stream

	data = {} # Create empty set, then fill in with our three fields:
	
	inputdata = re.findall(r'[-+]?\d*\.\d+|\d+]',data_stream)
#	inputdata = re.findall(r'[-+]?\d\*|\d*\.\d+|\d+]',data_stream)
#	inputdata = re.findall(r'[-+]-?(\d+(\.\d*)?|\d*\.\d+)]',data_stream)
#	print("INPUTDATA")
#	print inputdata

	# don't post ID - for some reason the ID is not being picked up.  To investigate further
 	data[fields[0]] = inputdata[0]	# ID
	data[fields[1]] = inputdata[1]	# v_bat
	data[fields[2]] = inputdata[2]	# temperature
	data[fields[3]] = inputdata[3]	# humidity
	data[fields[4]] = inputdata[4]	# acceleration_x
	data[fields[5]] = inputdata[5]	# acceleration_y
	data[fields[6]] = inputdata[6]	# acceleration_z
	data[fields[7]] = inputdata[7]	# pressure
	data[fields[8]] = inputdata[8]	# status
	T = time.strftime("%A %B %d, %Y %H:%M:%S %Z")

	print T
	print inputdata
	print data

	
	params = urllib.urlencode(data)
	
	# Now we need to set up our headers:
	headers = {} # start with an empty set
	# These are static, should be there every time:
	headers["Content-Type"] = "application/x-www-form-urlencoded"
	headers["Connection"] = "close"
	headers["Content-Length"] = len(params) # length of data
	if inputdata[0] = 1:
		headers["Phant-Private-Key"] = privateKey1 # private key header1
		# Now we initiate a connection, and post the data
		c = httplib.HTTPConnection(server)
		# Here's the magic, our reqeust format is POST, we want
		# to send the data to data.sparkfun.com/input/PUBLIC_KEY1.txt
		# and include both our data (params) and headers
		c.request("POST", "/input/" + publicKey1 + ".txt", params, headers)

	if inputdata[0] = 2:
		headers["Phant-Private-Key"] = privateKey2 # private key header2
		# Now we initiate a connection, and post the data
		c = httplib.HTTPConnection(server)
		# Here's the magic, our reqeust format is POST, we want
		# to send the data to data.sparkfun.com/input/PUBLIC_KEY2.txt
		# and include both our data (params) and headers
		c.request("POST", "/input/" + publicKey2 + ".txt", params, headers)
		
	r = c.getresponse() # Get the server's response and print it
	print r.status, r.reason

except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    GPIO.cleanup() # cleanup all GPIO
