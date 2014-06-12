#!/usr/bin/env python
#
# RaspberryPi daemon to interact with locally-attached sensors and help them send/receive data
#
# Author: David Bryant (djbryant@gmail.com)
# Version: 1.0
# Date: 12 June 2014
#
# Current version supports just one sensor -- a DS18B20 digital temperature sensor via the OneWire protocol.
# As such it needs to load the OneWire kernel module and use the filesystem-based model (via /sys) to 
# access data from the device (via GPIO)
#
# Data reporting currently provided includes:
#    1. Sending data to the Nemo cloud via a websocket interface
#    2. Posting data to dweet.io (using the 'dweepy' module)


import os
import glob
import websocket
import json
import datetime
import time
import threading
import logging
import dweepy


# URL for our websocket access point, which combines host, authentication token (00022), event
# data type ("temperature"), and 'update' to indicate we want to subscribe for updates
URI_SUB = "ws://stg.nemo2.nokiaconnect.net:8081/client/a5e5c5f4-8cd2-4710-f176-8deb05f86038/00022/temperature/update"

# How often (in seconds) do we want to send a temperature value to the cloud
UPDATE_TIME = 300

# Open file for output and seek to the end
LOG_FILE = '/opt/Sensors/MySensors.log'
logfile = open(LOG_FILE,'a+')
logfile.seek(2)
def logstring(s):
	logfile.write(s)
	logfile.flush()
	os.fsync(logfile.fileno())



# Data payload sent looks like:
{
    "device": {
        "IP": {
            "DBryantOffice": {
                "temperature": {
                    ".update": {
                        "unit": "degrees F",
                        "value": 61.000000000000014,
                        "time": "2014-04-18T20:20:58Z",
			"name": "Office Temperature"
                    }
                }
            }
        }
    }
}

# Update message received from server via subscription looks like:
{
    "/client/a5e5c5f4-8cd2-4710-f176-8deb05f86038/device/IP/officeTempF/temperature": {
        "value": 62.30000000000003,
        "unit": "degree F",
        "time": "2014-04-18T20:24:13Z",
	"name": "Office Temperature"
    }
}

# ---------------------------------------------------------------------------------------
# Setup, utility functions and whatnot

logging.basicConfig()

# Make sure the OneWire kernel modules are loaded
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Configuration parameters for the OneWire interface for the DS18B20 temperature sensor
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# Functions to read the current temperature from the OneWire interface
def read_temp_raw():
	f = open(device_file,'r')
	lines = f.readlines()
	f.close()
	return lines

def read_temp():
	lines = read_temp_raw()
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_temp_raw()
	equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
	temp_c = float(temp_string) / 1000.0
	temp_f = (temp_c * 9.0 / 5.0) + 32.0
	return temp_f

# ---------------------------------------------------------------------------------------
# Methods used by our websocket so we can send data to the cloud and also
# subscribe for events

# We're sending, not listening so don't really want to do anything with messages
def on_message(ws, message):
    # print "got raw message: " + message
    # event = json.loads(message)
    # print "received msg: ", json.dumps(event, indent=4)
    pass

def on_error(ws, error):
    # print "### error" + error
    logstring("### error" + error)

def on_close(ws):
    # print "### websocket closed ### --\n"
    logstring("### websocket closed ### --\n")

# Will create an independent thread to run our data reporting function
# as an infinite loop
def on_open(ws):
    # print ('### connected ###')
    logstring('### connected ###\n')

    t = threading.Thread(target=sendSensorLoop, args= (ws,))
    t.start()


# The actual main loop, which reads the sensor, sends the value, then sleeps
def sendSensorLoop(ws):
    while True:
	# Read a value from the temperature sensor
        tempF = read_temp()

	# Call the function that'll format the temperature & send it to the cloud
        sendTemperature("DBryantOffice", tempF, ws)

	# Wait the desired interval between reports
        time.sleep(UPDATE_TIME)


# Function to properly formulate the JSON data packet we use to send data to
# the cloud. 
def sendTemperature(id, t, ws):
	value = {}
	update = {}
	temperature = {}
	sensorID = {}
	connectionType = {}
	device = {}

	# Generate an ISO 8601 timestamp for the data packet
	lognow = time.gmtime(time.time())
	timestamp = ( '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}Z'.
			format(lognow.tm_year,lognow.tm_mon,lognow.tm_mday,
			lognow.tm_hour,lognow.tm_min,lognow.tm_sec) )

	value["value"] = t
	value["unit"] = "degrees F"
	value["time"] = timestamp
	value["name"] = id
	update[".update"] = value
	temperature["temperature"] = update
	sensorID[id] = temperature
	connectionType["IP"] = sensorID
	device["device"] = connectionType

	# DEBUG: print "sending msg: ", json.dumps(device, indent=4)
	
	# Output what we sent (for logging purposes) 
	# print "{0},{1:.3f}".format(timestamp,t)
	logstring(timestamp + "," + str(t) + "\n")

	# Send the value to the server via our websocket
	ws.send(json.dumps(device))

	# Oh, and dweet the data while we're at it (for fun)
	dweepy.dweet_for('orangemoose-thingy', {
		'sensor': id,
		'value': t,
		'unit': "degrees F",
		'time': timestamp,
	});


	

# ---------------------------------------------------------------------------------------
# Main routine, which creates the websocket with the proper methods and then lets them
# do all the work
if __name__ == "__main__":    

	websocket.enableTrace(False)

	while True:
		lognow = time.gmtime(time.time())
		timestamp = ( '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}Z'.
				format(lognow.tm_year,lognow.tm_mon,lognow.tm_mday,
				lognow.tm_hour,lognow.tm_min,lognow.tm_sec) )
		# print "(re)starting Temperature Sensor service at {}".format(timestamp)
		logstring("(re)starting Sensor Service at " + timestamp + '\n')
		ws = websocket.WebSocketApp(URI_SUB,
					on_message = on_message,
					on_error = on_error,
					on_open = on_open,
					on_close = on_close)
		logstring("start run_forever\n")
		try:
			ws.run_forever()
		except Exception, e:
			print e
		time.sleep(10)
