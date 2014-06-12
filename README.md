# RaspberryPi-utilities

Assorted programs, scripts, and general-purpose applications for use on Raspberry Pi devices.  Current contents 
are as follows:

**Read, process and upload sensor data**

* MySensors.py -- Python program to read data from locally-attached sensors and report them
  to the cloud.  Intended to be installed and used as a system service (i.e., from /etc/init.d)
  via a separate shell script ('MySensors.sh') but can also be run as an application.
* MySensors.sh -- init script for starting/stopping MySensors.py as a system service.

**Display useful information on an OLED display**

* OLEDconsole.py -- Python program to display basic system information (hostname, IP address,
  boot date/time, and current local time) on an OLED display
* OLEDconsoleT.py -- Variant of OLEDconsole.py that shows current temperature as read from
  an attached DS18B20 digital temperature sensor but simplifies the current local time display
  in order to have room on the OLED for the temperature data.
* OLEDconsole.sh -- Init script for starting/stopping OLEDconsole.py (in any form) as a system
  service.

**Easily construct init scripts to start/stop Python applications as system services**

* myservice.sh -- Template shell script containing instructions for creating an init
  script you can install via /etc/init.d to start/stop any Python application as a 
  system service and have it invoked automatically at boot time and run in the background.
