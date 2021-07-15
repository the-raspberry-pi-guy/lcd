# LCD
This repository contains all the code for interfacing with a **16x2 character I2C liquid-crystal display (LCD)**. This accompanies my **Youtube tutorial**: [Raspberry Pi - Mini LCD Display Tutorial](https://www.youtube.com/watch?v=fR5XhHYzUK0). 

You can buy one of these great little I2C LCD on eBay or somewhere like [the Pi Hut](https://thepihut.com/search?type=product&q=lcd).

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
## Simple strings
This is a demo developed by user @Tomtom0201, showing how simple text stings could be displayed on LCD:

<p align="center">
  <img src="imgs/demo_simple_strings.jpg" width="300">
</p>


## Extended strings
This is a demo debeloped by @juvus, showing how extended strings could be used. Extended strings can contain special placeholders `{0xFF}` - hex code of the symbol wrapped with curly bracers. Hex code of the symbol can be found in characters table. For example code of the symbol `ö` is 0xEF, and so this symbol could be printed by using `{0xEF}` placeholder in string. Table can be found in `/imgs/characters_table.png`.
If you want to combine placeholder to write a symbol {0xFF} with native python placeholder {0} for inserting dome data into text, escape those placeholders that is using to write a symbol. This is an example:
 `display.lcd_display_extended_string("Symbol:{{0xEF}} data:{0}".format(5), 2)` 

<p align="center">
  <img src="imgs/demo_extended_strings.jpg" width="300">
</p>

## Custom characters
It is possible to define in CG RAM memory 8 absolutelly custom characters. This characters can be pronted on LCD the same way as any characters from the character table. Codes of the custom characters are unique and the following: 1st - {0x00}, 2nd - {0x01}, 3rd - {0x02}, 4th - {0x03}, 5th - {0x04}, 6th - {0x05}, 7th - {0x06} and 8th - {0x07}. Please, see the `demo_lcd_custom_characters.py` file for more details, how it is possible to define you own characters. This demo was debeloped by @juvus.

<p align="center">
  <img src="imgs/demo_custom_characters.jpg" width="300">
</p>

## Progress bar
This is a demo of graphical progress bar created with custom characters. This bar could be used, for example, for showing the current level of battery charge. This demo was debeloped by @juvus.

<p align="center">
  <img src="imgs/demo_progress_bar.jpg" width="300">
</p>

## Backlight Control
This is a demo developed by user and watcher @Tomtom0201, showcasing backlight control of the LCD (available on some hardware): 

<p align="center">
  <img src="imgs/demo_backlight.gif">
</p>

## Forex
This is a demo developed by user and watcher @bariskisir.  It requires `python-pip` and the packages `requests` and `bs4` (BeautifulSoup) because it parses web content.

* Install `pip`
  ```
  sudo apt install python-pip
  ```
* Then install `requests` and `bs4`
  ```
  pip install requests bs4
  ```
* Now you should be able to run `demo_forex.py`:

<p align="center">
  <img src="imgs/demo_forex.gif">
</p>

I haven't been able to test it myself personally, but it looks like a cool Forex stream. If you run into any bugs with it, please feel free to reach out to bariskisir and submit a PR.

## IP Address
Another demo developed by @Sierra007117:

<p align="center">
  <img src="imgs/demo_ip.jpg" width="640" height="480">
</p>

Display your Pi's IP address - useful for SSH'ing and more!


## NetMonitor
A demo created by [@cgomesu](https://github.com/cgomesu) that uses `ping` and `nc` (netcat) to monitor the network status of hosts and services, respectively.  This demo uses built-in tools, so nothing new needs to be installed.

<p align="center">
  <img src="imgs/demo_netmonitor.gif">
</p>

Hosts and services can be modified by editing their respective [dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries):

```python
hosts = {
    'Internet': '8.8.8.8',
    'Firewall': '192.168.1.1',
    'NAS': '192.168.1.2'
}
services = {
    'Cameras': {'ip': '192.168.1.2', 'port': '8000'},
    'Plex': {'ip': '192.168.1.2', 'port': '32400'}
}
```

After editing the hosts and services dictionaries, you can run this demo in the background (as a service) as follows:
1. Create a new service file in `/lib/systemd/system/` called `rpi-netmonitor.service`:
```commandline
nano /lib/systemd/system/rpi-netmonitor.service
```
2. Copy and paste the following in the new service file:
```
[Unit]
Description=A RPi network monitor for a 16x2 LCD

[Service]
Type=simple
User=pi

ExecStart=/usr/bin/python /home/pi/rpi-lcd/demo_netmonit.py

Restart=always
RestartSec=5

KillMode=process
KillSignal=SIGINT

[Install]
WantedBy=multi-user.target
```
3. Enable the service and start it:
```commandline
sudo systemctl enable rpi-netmonitor.service
sudo systemctl start rpi-netmonitor.service
```
4. Check that the LCD is displaying the correct information; otherwise, check the service status
```commandline
sudo systemctl status rpi-netmonitor.service
```