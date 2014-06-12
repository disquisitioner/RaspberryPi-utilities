#!/bin/sh

### BEGIN INIT INFO
# Provides:          myservice
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Put a short description of the service here
# Description:       Put a long description of the service here
### END INIT INFO

# Template for creating init scripts that can start/stop services.
# Based on an excellent example and explanation by Stephen Phillips at
# http://blog.scphillips.com/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/
# Detailed instructions are there, but the shorthand approach is:
#  1. Modify this file as instructed in the various comments
#  2. Make sure your service script ('myservice.py') is executable
#     (e.g., mode 755) and starts with the line that'll let it run 
#      directly from the shell (e.g., #!/usr/bin/env python)
#  3. Copy this script into /etc/init.d and make
#     sure it is executable there
#  4. Test the script with 'sudo /etc/init.d/myservice.sh stop' and 
#     'sudo /etc/init.d/myservice.sh stop'
#  5. When you're comfortable everything works correctly then enable the 
#     script for use at boot time with 'sudo update-rc.d myservice.sh defaults'
#  6. Confirm installation with 'ls /etc/rc?.d/*myservice.sh'
# (Note that you'll almost certainly call your service something other than
# 'myservice.sh' so pick a suitable name and then substitute that in the 
# instructions above as well as everywhere 'myservice' is used in this file.)

# Change the next 3 lines to suit where you install your script and what you want to call it
DIR=/usr/local/bin/myservice
DAEMON=$DIR/myservice.py
DAEMON_NAME=myservice

# This next line determines what user the script runs as.
# Root generally not recommended but necessary if you are using the Raspberry Pi GPIO from Python.
DAEMON_USER=root

# The process ID of the script when it runs is stored here:
PIDFILE=/var/run/$DAEMON_NAME.pid

. /lib/lsb/init-functions

do_start () {
    log_daemon_msg "Starting system $DAEMON_NAME daemon"
    start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --chuid $DAEMON_USER --startas $DAEMON
    log_end_msg $?
}
do_stop () {
    log_daemon_msg "Stopping system $DAEMON_NAME daemon"
    start-stop-daemon --stop --pidfile $PIDFILE --retry 10
    log_end_msg $?
}

case "$1" in

    start|stop)
        do_${1}
        ;;

    restart|reload|force-reload)
        do_stop
        do_start
        ;;

    status)
        status_of_proc "$DAEMON_NAME" "$DAEMON" && exit 0 || exit $?
        ;;
    *)
        echo "Usage: /etc/init.d/$DAEMON_NAME {start|stop|restart|status}"
        exit 1
        ;;

esac
exit 0