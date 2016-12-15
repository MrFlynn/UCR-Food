#!/bin/bash

# Check if script is run as root. If not, run again as root and prompt
# user for password.
if [[ $(id -u) != "0"]]; then
	exec sudo "$0" "$@"
	exit $?
fi

# Check if systemd exist. If it does, move service and timer into proper
# dir. Otherwise, add a cronjob.
if [[ $(pidof systemd) ]]; then
	mv # something here
else
	cat # something else here
fi
