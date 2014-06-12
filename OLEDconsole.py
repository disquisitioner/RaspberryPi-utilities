# OLEDconsole.py

# Display key system info (hostname, IP address, etc.) on an OLED display
#
# Author: David Bryant (djbryant@gmail.com)
# Version: 1.0
# Date: 12 June 2014
#
# This is a basic OLEDconsole for Raspberry Pi derived from examples in the Adafruit Tutorial at
# https://learn.adafruit.com/adafruit-oled-displays-for-raspberry-pi.  It combines display
# of hostname, IP address, boot date/time, and time-of-day clock.
#
# Depends on Guy Carpenter's Python library that supports interfacing a variety of hardware with
# the Raspberry Pi including rotary encoders, switches, and especially SSD1306 displays.
# See https://github.com/guyc/py-gaugette for the library, samples, and more details

# Imports all of the necessary modules
import gaugette.ssd1306
import time
import sys
import socket
import fcntl
import struct
from time import sleep

# This function allows us to grab any of our IP addresses
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

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

ipaddr = ''

# This sets 'ipaddr' equal to whatever your IP address is, or isn't
try:
    # WiFi address of WiFi adapter. NOT ETHERNET
    ipaddr = get_ip_address('wlan0')
except IOError:
    try:
	# WiFi address of Ethernet cable. NOT ADAPTER
        ipaddr = get_ip_address('eth0')
    except IOError:
        ipaddr = ('NO INTERNET!')

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
led.draw_text2(0,0,hostname,2)
led.draw_text2(0,16,'IP: '+ipaddr,1)
led.draw_text2(0,26,'Boot: '+boottime_string,1)

while True:
        text = time.strftime("%X")
        led.draw_text2(0,40,text,2)
	led.display()
        time.sleep(1)
