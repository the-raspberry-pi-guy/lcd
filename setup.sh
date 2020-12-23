#!/usr/bin/env bash

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


apt_install () {
  echo "####### APT #######"
  apt update && apt install python-smbus i2c-tools -y
  echo "###################"
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
  if [[ -z "${list[*]}" ]]; then return 1; fi
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


############
# Main logic

# check again if user is root in case user is calling this script directly
if [[ "$(id -u)" -ne 0 ]]; then echo "Please re-run as sudo."; exit 1; fi

echo "###################################################"
echo "# Automated Installer Program For I2C LCD Screens #"
echo "###################################################"

echo "Updating apt pkg list and installing python-smbus. Enter the password if asked."
apt_install

config_dir="configs"  # global directory for the config files
echo "Checking enabled and blacklisted modules."
if modules /etc/modules "$config_dir"/modules; then
  echo "Updated required modules in /etc/modules."
else
  echo "There was an error while updating /etc/modules. I2C might not work."
fi
if modules /etc/modprobe.d/raspi-blacklist.conf "$config_dir"/raspi-blacklist.conf; then
  echo "Updated required modules in /etc/modprobe.d/raspi-blacklist.conf."
fi

echo "Enabling I2C on boot."
i2c_boot_config

echo "#############################################################"
echo "All finished! Press any key to REBOOT now or Ctrl+C to abort."
echo "#############################################################"

read -n1 -s
reboot
