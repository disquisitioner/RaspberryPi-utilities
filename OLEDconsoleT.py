#!/usr/bin/env python
# OLEDconsoleT.py
#
# Display key system info (hostname, IP address, etc.) on an OLED display
#
# Author: David Bryant (djbryant@gmail.com)
# Version: 1.0
# Date: 12 June 2014
#
# This variant of OLEDconsole displays current temperature as read from a DS18B20 sensor,
# but sacrifices having the clock update every second given the additional overhead
# of reading the sensor (and waiting for it to have a valid value), plus needing
# room on the display to show the temperature in large digits too
#
# Depends on Guy Carpenter's Python library that supports interfacing a variety of hardware with
# the Raspberry Pi including rotary encoders, switches, and especially SSD1306 displays.
# See https://github.com/guyc/py-gaugette for the library, samples, and more details

# Imports all of the necessary modules
import os
import glob
import gaugette.ssd1306
import time
import sys
import socket
import fcntl
import struct
from time import sleep

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

# This function allows us to grab any of our IP addresses
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

# This sets 'ipaddr' equal to whatever your IP address is, or isn't
NOIPADDR = ('NO INTERNET')
def set_ipaddr():
	try:
	    # WiFi address of WiFi adapter. NOT ETHERNET
	    return get_ip_address('wlan0')
	except IOError:
	    try:
		# WiFi address of Ethernet cable. NOT ADAPTER
		return get_ip_address('eth0')
	    except IOError:
		return NOIPADDR

# Set configuration parameters for the OLED, both as to how it is wired
# (RESET and DC pins) and how large it is (ROWS x COLS).
RESET_PIN = 15
DC_PIN    = 16
ROWS      = 64
COLS      = 128

# Create the OLED object with the proper settings
led = gaugette.ssd1306.SSD1306(reset_pin=RESET_PIN, dc_pin=DC_PIN,
	rows=ROWS, cols=COLS)
led.begin()
led.clear_display() # Will clear display when led.display() is called

width = COLS
height = ROWS

ipaddr = set_ipaddr()
hostname = socket.gethostname()

# Calculate boot time based on uptime kept in /proc/uptime
with open('/proc/uptime','r') as f:
	uptime_seconds = float(f.readline().split()[0])
	f.close()
	now = time.time()
	boot = now - uptime_seconds
	bootlocal = time.localtime(boot)
	boottime_string = time.strftime("%H:%M %b-%d-%y",bootlocal)

# The actual printing of TEXT
led.clear_display()
led.draw_text2(0, 0,'Name: '+hostname,1)
led.draw_text2(0,10,'IP  : '+ipaddr,1)
led.draw_text2(0,20,'Boot: '+boottime_string,1)

while True:
	if ipaddr == NOIPADDR :
		ipaddr = set_ipaddr()
		led.draw_text2(0,10,'IP  : '+ipaddr,1)

	# Display current clock time
        text = time.strftime("%H:%M")
        led.draw_text2(0,47,text,2)

	# Display current temperature reading
	tempF = "{:.1f}".format(read_temp())
	led.draw_text2(82,47,tempF,2)

	led.display()
        time.sleep(4)
