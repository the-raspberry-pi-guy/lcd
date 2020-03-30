#!/bin/bash
if [ "$(id -u)" != "0" ]; then
	echo "Please re-run as sudo."
	exit 1
fi

echo "Automated Installer Program For I2C LCD Screens"
echo "Installer by Ryanteck LTD. Cloned and tweaked by Matthew Timmons-Brown for The Raspberry Pi Guy YouTube tutorial"
echo "Updating APT & Installing python-smbus, if password is asked by sudo please enter it"
apt-get update
apt-get install python-smbus -y
echo "Should now be installed, now checking revision"
revision=`python -c "import RPi.GPIO as GPIO; print GPIO.RPI_REVISION"`

if [ $revision = "1" ]
then
echo "I2C Pins detected as 0"
cp installConfigs/i2c_lib_0.py ./i2c_lib.py
else
echo "I2C Pins detected as 1"
cp installConfigs/i2c_lib_1.py ./i2c_lib.py
fi
echo "I2C Library setup for this revision of Raspberry Pi, if you change revision a modification will be required to i2c_lib.py"
echo "Now overwriting modules & blacklist. This will enable i2c Pins"
cp installConfigs/modules /etc/
cp installConfigs/raspi-blacklist.conf /etc/modprobe.d/
printf "dtparam=i2c_arm=1\n" >> /boot/config.txt


echo "Should be now all finished. Please press any key to now reboot. After rebooting run"
echo "'sudo python demo_lcd.py' from this directory"
read -n1 -s
sudo reboot
