#!/usr/bin/env sh

# POSIX script to call setup.sh with the correct interpreter
# Created to maintain compatibility with the video tutorial and descriptions

##########################################################################
# Automated Installer Program For I2C 16x2 LCD Screens
#
# Cloned and adapted from: Ryanteck LTD
#
# Author: Matthew Timmons-Brown (the-raspberry-pi-guy)
# Contributors: https://github.com/the-raspberry-pi-guy/lcd/contributors
#
# Repo: https://github.com/the-raspberry-pi-guy/lcd
##########################################################################

# check if user root
if [ "$(id -u)" != "0" ]; then echo "Please re-run as sudo."; exit 1; fi

# execute the installation script using interpreter in the shebang
./setup.sh

exit 0