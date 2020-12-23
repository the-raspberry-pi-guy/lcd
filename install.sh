#!/bin/bash

apt_install () {
  echo '#######'
  apt update && apt install python-smbus -y
  echo '#######'
}

# find line that contains $1 from file $2 and delete it permanently
delete_line () {
  sed -i '/'"$1"'/d' "$2" 2> /dev/null
}

# parse /boot/config.txt and append i2c config if missing
i2c_boot_config () {
  local config='/boot/config.txt'; local line; local i2c_reconfig; local i2c_reconfig_line
  while read -r line; do
    if [[ "$line" =~ ^dtparam=i2c(_arm){0,1}(=on|=1){0,1}$ ]]; then
      i2c_reconfig='false'; break
    elif [[ "$line" =~ ^dtparam=i2c(_arm){0,1}(=off|=0){1}$ ]]; then
      i2c_reconfig='true'; i2c_reconfig_line="$line"; break
    fi
  done < "$config"
  if [[ "$i2c_reconfig" == 'true' ]]; then
    # backup config.txt
    cp "$config" "$config".backup
    # delete i2c=off config and append i2c=on config
    delete_line "$i2c_reconfig_line" "$config"
    echo "dtparam=i2c" | tee -a "$config" > /dev/null
  elif [[ -z "$i2c_reconfig" ]]; then
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
  if [[ -z "${list[@]}" ]]; then return 1; fi
}

# takes path to an old modules file as first argument ($1) and a new file as second arg ($2).
# it parses new and old files, appending missing modules to the old file instead of overwriting
modules () {
  if [[ -z "$1" || -z "$2" ]]; then return 1; fi
  local old_file="$1"; local new_file="$2"
  if [[ ! -f "$old_file" || -z $(cat "$old_file") ]]; then
    cp "$new_file" "$old_file"
  else
    if line_to_list "$new_file"; then
      for m in "${list[@]}"; do
        if [[ ! $(cat "$old_file") =~ $m ]]; then
          echo "$m" | tee -a "$old_file" > /dev/null
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

echo "Automated Installer Program For I2C LCD Screens."
echo "Installer by Ryanteck LTD. Cloned and tweaked by Matthew Timmons-Brown for The Raspberry Pi Guy YouTube tutorial. Edited by cgomesu."

echo "Updating APT & Installing python-smbus, if password is asked by sudo please enter it."
apt_install
echo "Should now be installed, now checking revision."

# global directory for the config files
config_dir="installConfigs"
rpi_revision
echo "I2C Library setup for this revision of Raspberry Pi. If you change revision, a modification will be required to i2c_lib.py."

echo "Checking modules & blacklist. This will enable i2c Pins."
#check modules
if modules /etc/modules "$config_dir"/modules; then
  echo "Updated required modules in /etc/modules."
else
  echo "There was an error while updating /etc/modules. i2c might not work."
fi
#check raspi-blacklist.conf
if modules /etc/modprobe.d/raspi-blacklist.conf "$config_dir"/raspi-blacklist.conf; then
  echo "Updated required modules in /etc/modprobe.d/raspi-blacklist.conf."
fi

echo "Enabling i2c on boot."
i2c_boot_config

echo "Should be now all finished. Please press any key to reboot now or Ctrl+C to abort."
echo "After rebooting, run 'sudo python demo_lcd.py' from this directory."
read -n1 -s
sudo reboot
