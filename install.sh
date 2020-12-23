#!/usr/bin/env sh

# POSIX script to call setup.sh with the correct interpreter
# Created to maintain compatibility with the video tutorial and descriptions

# check if user root
if [ "$(id -u)" != "0" ]; then echo "Please re-run as sudo."; exit 1; fi

# execute the installation script using interpreter in the shebang
./setup.sh

exit 0