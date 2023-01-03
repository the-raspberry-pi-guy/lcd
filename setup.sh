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

# lcd repo directory that contains the config files
LCD_CONFIG_DIR="configs"
# full path to RPi's boot config file
RPI_CONFIG='/boot/config.txt'

start () {
  echo "############################################"
  echo "# Automated installer for the I2C 16x2 LCD #"
  echo "############################################"
  echo ""
}

# takes msg ($1) and status ($2) as args
end () {
  echo ""
  echo "############################################"
  echo "# Finished the setup script"
  echo "# Message: $1"
  echo "############################################"
  exit "$2"
}

# takes message ($1) and level ($2) as args
message () {
  echo "[LCD] [$2] $1"
}

apt_install () {
  if ! apt update; then
    message "Unable to update APT." "ERROR"
    end "Check your Internet connection and try again." 1
  fi

  message "Installing I2C-Tools." "INFO"
  if ! apt install i2c-tools -y; then
    message "Unable to install pkg 'i2c-tools'. You'll need to enter the LCD address manually." "WARNING"
  fi

  message "Installing the 'smbus' pkg for Py2 and Py3." "INFO"
  if ! apt install python-smbus -y; then
    message "Unable to install pkg 'python-smbus'." "WARNING"
  fi
  if ! apt install python3-smbus -y; then
    message "Unable to install pkg 'python3-smbus'." "WARNING"
  fi
}

# takes a package ($1) as arg
dpkg_check_installed () {
  if dpkg -l "$1" > /dev/null 2>&1; then return 0; else return 1; fi
}

# find line that contains $1 from file $2 and delete it permanently
delete_line () {
  sed -i '/'"$1"'/d' "$2" 2> /dev/null
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
        if [[ ! $(cat "$old_file") =~ $m ]]; then echo "$m" | tee -a "$old_file" > /dev/null; fi
      done
    fi
  fi
}

# parse /boot/config.txt and append i2c config if missing
i2c_boot_config () {
  local line; local i2c_reconfig; local i2c_reconfig_line

  while read -r line; do
    if [[ "$line" =~ ^dtparam=i2c(_arm){0,1}(=on|=1){0,1}$ ]]; then
      i2c_reconfig='false'; break
    elif [[ "$line" =~ ^dtparam=i2c(_arm){0,1}(=off|=0){1}$ ]]; then
      i2c_reconfig='true'; i2c_reconfig_line="$line"; break
    fi
  done < "$RPI_CONFIG"

  # backup config.txt
  cp "$RPI_CONFIG" "$RPI_CONFIG".backup

  if [[ "$i2c_reconfig" == 'true' ]]; then
    # delete i2c=off config and append i2c=on config
    delete_line "$i2c_reconfig_line" "$RPI_CONFIG"
    echo "dtparam=i2c" | tee -a "$RPI_CONFIG" > /dev/null
  elif [[ -z "$i2c_reconfig" ]]; then
    # i2c config not found, append to file
    echo "dtparam=i2c" | tee -a "$RPI_CONFIG" > /dev/null
  fi

  message "Your $RPI_CONFIG was edited but there is a backup of the original file in $RPI_CONFIG.backup" 'INFO'
}


############
# Main logic
start

# check again if user is root in case user is calling this script directly
if [[ "$(id -u)" -ne 0 ]]; then message "User is not root." 'ERROR'; end 'Re-run as root or append sudo.' 1; fi

trap "end 'Received a signal to stop.' 1" INT HUP TERM

message 'Installing packages via APT.' 'INFO'; apt_install

message "Checking Py 'smbus' installation." 'INFO'
if dpkg_check_installed 'python-smbus' && dpkg_check_installed 'python3-smbus'; then
  message "You may use either 'python' or 'python3' to interface with the lcd." 'INFO'
elif ! dpkg_check_installed 'python-smbus' && dpkg_check_installed 'python3-smbus'; then
  message "Use 'python3' to interface with the lcd." 'INFO'
elif dpkg_check_installed 'python-smbus' && ! dpkg_check_installed 'python3-smbus'; then
  message "Use 'python' to interface with the lcd." 'INFO'
elif ! dpkg_check_installed 'python-smbus' && ! dpkg_check_installed 'python3-smbus'; then
  # exit on lack of the 'smbus' pkg
  message "Unable to find either 'python-smbus' or 'python3-smbus' installed." 'ERROR'
  end 'Missing required Python package.' 1
fi

message "Checking enabled and blacklisted modules." 'INFO'
if modules /etc/modules "$LCD_CONFIG_DIR"/modules; then
  message "Updated required modules in '/etc/modules.'" 'INFO'
else
  message "There was an error while updating '/etc/modules. I2C might not work.'" 'WARNING'
fi
if modules /etc/modprobe.d/raspi-blacklist.conf "$LCD_CONFIG_DIR"/raspi-blacklist.conf; then
  message "Updated required modules in '/etc/modprobe.d/raspi-blacklist.conf.'" 'INFO'
fi

message "Enabling I2C on boot." 'INFO'; i2c_boot_config

echo "#################################################################"
echo "# All finished! Press any key to REBOOT now or Ctrl+c to abort. #"
echo "#################################################################"

read -n1 -s; reboot now
