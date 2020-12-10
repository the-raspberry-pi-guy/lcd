#!/bin/bash

apt_install () {
  apt update && apt install python-smbus -y
}

# find line that contains $1 from file $2 and delete it permanently
delete_line () {
  sed -i '/'"$1"'/d' "$2" 
}

# parse /boot/config.txt and append i2c config if missing
i2c_boot_config () {
  local line; local i2c_config='false'; local config='/boot/config.txt'
  while read -r line; do
    if [[ "$line" =~ ^dtparam=i2c(_arm){0,1}(=on|=1){0,1}$ ]]; then
      i2c_config='true'; break
    elif [[ "$line" =~ ^dtparam=i2c(_arm){0,1}(=off|=0){1}$ ]]; then
      # backup config.txt
      cp "$config" "$config".backup
      # delete i2c=off config and append i2c=on config
      delete_line "$line" "$config"
      echo "dtparam=i2c" | tee -a "$config" > /dev/null
      echo "append new line"
      echo "break 3"; i2c_config='true'
      break
    fi
  done < "$config"
  if [[ "$i2c_config" == 'false' ]]; then
    # backup config.txt
    cp "$config" "$config".backup
    # i2c config not found, append to file
    echo "dtparam=i2c" | tee -a "$config" > /dev/null
  fi
}

# takes path to a file as first argument ($1) and creates a global 
# $list array with non-empty and non-commented out lines as elements
line_to_list () {
  if [[ -z "$1" || ! -f "$1" ]]; then return 1; fi
  unset list; list=(); local file="$1"; local line
  while read -r line; do
    if [[ -n "$line" && ! "$line" =~ ^\# ]]; then list+=("$line"); fi
  done < "$file"
  if [[ -z "$list" ]]; then return 1; fi
}

modules_load () {
  #check /etc/modules
  if [[ ! -f /etc/modules || -z $(cat /etc/modules) ]]; then
    cp "$config_dir"/modules /etc/
  else
    if line_to_list "$config_dir"/modules; then
      for mod in "${list[@]}"; do
        if [[ ! "$(cat /etc/modules)" =~ $mod ]]; then
          echo "$mod" | tee -a /etc/modules > /dev/null
        fi
      done
    fi
  fi
}

modules_blacklist () {
  #check /etc/moddprobe.d/raspi-blacklist.conf
  if [[ ! -f /etc/modprobe.d/raspi-blacklist.conf || -z $(cat /etc/modprobe.d/raspi-blacklist.conf) ]]; then
    cp "$config_dir"/raspi-blacklist.conf /etc/modprobe.d/
  else
    if line_to_list "$config_dir"/raspi-blacklist.conf; then
      for blacklisted in "${list[@]}"; do
        if [[ ! "$(cat /etc/modprobe.d/raspi-blacklist.conf)" =~ $blacklisted ]]; then
          echo "$blacklisted" | tee -a /etc/modprobe.d/raspi-blacklist.conf > /dev/null
        fi
      done
    fi
  fi
}

rpi_revision () {
  revision=$(python -c "import RPi.GPIO as GPIO; print GPIO.RPI_REVISION")
  if [[ "$revision" -eq 1 ]]; then
    echo "I2C Pins detected as 0"
    cp "$config_dir"/i2c_lib_0.py ./i2c_lib.py
  else
    echo "I2C Pins detected as 1"
    cp "$config_dir"/i2c_lib_1.py ./i2c_lib.py
  fi
}


##############
# Start script

if [ "$(id -u)" != "0" ]; then
  echo "Please re-run as sudo."
  exit 1
fi

echo "Automated Installer Program For I2C LCD Screens"
echo "Installer by Ryanteck LTD. Cloned and tweaked by Matthew Timmons-Brown for The Raspberry Pi Guy YouTube tutorial"

echo "Updating APT & Installing python-smbus, if password is asked by sudo please enter it"
apt-install
echo "Should now be installed, now checking revision"
# global directory for the config files
config_dir="installConfigs"
rpi_revision
echo "I2C Library setup for this revision of Raspberry Pi. If you change revision, a modification will be required to i2c_lib.py"

echo "Checking modules & blacklist. This will enable i2c Pins"
modules_load
modules_blacklist

echo "Enabling i2c on boot"
i2c_boot_config

echo "Should be now all finished. Please press any key to now reboot. After rebooting run"
echo "'sudo python demo_lcd.py' from this directory"
read -n1 -s
sudo reboot
