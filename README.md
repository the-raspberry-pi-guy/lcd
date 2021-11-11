# LCD
This repository contains all the code for interfacing with a **16x2 character I2C liquid-crystal display (LCD)**. This accompanies my **Youtube tutorial**: [Raspberry Pi - Mini LCD Display Tutorial](https://www.youtube.com/watch?v=fR5XhHYzUK0).

<p align="center">
  <a href="https://www.youtube.com/watch?v=fR5XhHYzUK0">
    <img src="imgs/thumb-yt-rpiguy-lcd-tutorial.png" width="80%">
  </a>
</p>

You can buy one of these great little I2C LCD on eBay or somewhere like [the Pi Hut](https://thepihut.com/search?type=product&q=lcd).

# Table of Contents
1. [Installation](#Installation)
2. [Demos](#demos)
   - [Backlight control](#backlight-control)
   - [Custom characters](#custom-characters)
   - [Extended strings](#extended-strings)
   - [Forex](#forex)
   - [IP address](#ip-address)
   - [LCD](#lcd)
   - [NetMonitor](#netmonitor)
   - [Progress bar](#progress-bar)
3. [Implementation](#Implementation)
   - [Systemd](#systemd)
4. [Contributions](#contributions)

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
A list of demonstration (demo) files that illustrate how to use the LCD driver.  Demos are ordered alphabetically.

## Backlight Control
- Author: [@Tomtom0201](https://github.com/Tomtom0201)

This demo showcases the backlight control of the LCD, which is available on some hardware:

<p align="center">
  <img src="imgs/demo_backlight.gif" width="50%">
</p>

## Custom characters
- Author: [@juvus](https://github.com/juvus)

It is possible to define in CG RAM memory up to 8 custom characters. These characters can be prompted on LCD the same way as any characters from the [characters table](imgs/characters_table.png). Codes for the custom characters are unique and as follows:

  1. `{0x00}`
  2. `{0x01}`
  3. `{0x02}`
  4. `{0x03}`
  5. `{0x04}`
  6. `{0x05}`
  7. `{0x06}`
  8. `{0x07}`

Please, see the comments and implementation in the [`demo_lcd_custom_characters.py`](demo_lcd_custom_characters.py) file for more details on how to use custom characters.

<p align="center">
  <img src="imgs/demo_custom_characters.jpg" width="50%">
</p>

## Extended strings
- Author: [@juvus](https://github.com/juvus)

This is demo showcases how extended strings could be used. Extended strings can contain special placeholders of form `{0xFF}`, that is, a hex code of the symbol wrapped within curly brackets. Hex codes of various symbols can be found in the following characters table:

<p align="center">
  <img src="imgs/characters_table.png" width="50%">
</p>

For example, the hex code of the symbol `ö` is `0xEF`, and so this symbol could be printed on the second row of the display by using the `{0xEF}` placeholder, as follows:

```Python
display.lcd_display_extended_string("{0xEF}", 2)
```

If you want to combine placeholder to write a symbol `{0xFF}` with the native Python placeholder `{0}` for inserting dome data into text, escape the non-native placeholders. Here is an example:

```Python
display.lcd_display_extended_string("Symbol:{{0xEF}} data:{0}".format(5), 2)
```

<p align="center">
  <img src="imgs/demo_extended_strings.jpg" width="50%">
</p>

## Forex
- Author: [@bariskisir](https://github.com/bariskisir)
- Additional Python package requirements: `pip`, `requests`, `bs4`

To install the requirements, follow this procedure:
  - Install `pip` and use it to install the remaining packages
    ```sh
    sudo apt install python-pip
    pip install requests bs4
    ```

<p align="center">
  <img src="imgs/demo_forex.gif" width="50%">
</p>

## IP Address
- Author: [@Sierra007117](https://github.com/Sierra007117)

Display your Pi's IP address, which is useful for `SSH` access and more!

<p align="center">
  <img src="imgs/demo_ip.jpg" width="50%">
</p>

## LCD
- Author: [@Tomtom0201](https://github.com/Tomtom0201)

This demo shows how simple strings could be displayed on the LCD.  For extended usage, take a look at [Extended strings](#extended-strings) demo instead.

<p align="center">
  <img src="imgs/demo_simple_strings.jpg" width="50%">
</p>

## NetMonitor
- Author: [@cgomesu](https://github.com/cgomesu)

This demo uses `ping` and `nc` (netcat) to monitor the network status of hosts and services, respectively. Hosts and services can be modified by editing their respective [dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries):

```Python
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

<p align="center">
  <img src="imgs/demo_netmonitor.gif" width="50%">
</p>

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

## Progress bar
- Author: [@juvus](https://github.com/juvus)

This is a demo of a graphical progress bar created with [custom characters](#custom-characters). This bar could be used, for example, for showing the current level of battery charge.

<p align="center">
  <img src="imgs/demo_progress_bar.jpg" width="50%">
</p>
