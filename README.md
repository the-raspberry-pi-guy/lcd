# LCD
This repository contains all the code for interfacing with a **16x2 character I2C LCD display**. This accompanies my **Youtube tutorial**: [Raspberry Pi - Mini LCD Display Tutorial](https://www.youtube.com/watch?v=fR5XhHYzUK0). 

You can buy one of these great little I2C LCD displays on eBay or somewhere like [the Pi Hut](https://thepihut.com/search?type=product&q=lcd).

# Installation
* Install git
``` 
sudo apt install git
```

* Clone the repo in your `pi` home directory
``` 
cd /home/pi/
git clone https://github.com/the-raspberry-pi-guy/lcd.git
cd lcd/
```

* Run the automatic installation script with `sudo` permission
``` 
sudo ./install.sh
```

* After rebooting, try one of the [**demos**](#demos)
``` 
cd /home/pi/lcd/
./demo_clock.py
```

# Demos

## Backlight Control
This is a demo developed by user and watcher @Tomtom0201, showcasing backlight control of the LCD (available on some hardware): 

<p align="center">
  <img src="imgs/demo_backlight.gif">
</p>

## Forex
* Requires PIP (`sudo apt install python-pip`)
* Then install `requests` and `bs4` (`pip install requests bs4`)

This is a demo developed by user and watcher @bariskisir:

<p align="center">
  <img src="imgs/demo_forex.gif">
</p>

I haven't been able to test it myself personally, but it looks like a cool Forex stream. If you run into any bugs with it, please feel free to reach out to bariskisir and submit a PR.

## IP Address
Another demo developed by Sierra007117:

<p align="center">
  <img src="imgs/demo_ip.jpg" width="640" height="480">
</p>

Display your Pi's IP address - useful for SSH'ing and more!
