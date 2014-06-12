RaspberryPi-utilities
=====================

Assorted programs, scripts and general-purpose applications for use on Raspberry Pi devices.

Current contents:

*) MySensors.py -- Python program to read data from locally-attached sensors and report them
   to the cloud. Intended to be installed and used as a system service (i.e., from /etc/init.d)
   via a seperate shell script ('MySensors.sh')

*) MySensors.sh -- init script for starting/stopping MySensors.py as a system service
