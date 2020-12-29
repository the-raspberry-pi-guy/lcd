#!/usr/bin/env python

import drivers
from time import sleep
from os import devnull
from subprocess import call, check_output


def cleanup():
    display.lcd_clear()


def end(msg=None, status=0):
    cleanup()
    display.lcd_display_string('{:^16}'.format('# Bye message: #'), 1)
    display.lcd_display_string('{:^16}'.format(msg), 2)
    exit(status)


# Returns True if host responds to a ping request within the timeout interval
def ping(host, timeout=3):
    return call(['ping', '-c', '1', '-W', str(timeout), str(host)],
                stdout=open(devnull, 'w'),
                stderr=open(devnull, 'w')) == 0


# Returns True if host has given port open
def nc(host, port, timeout=3):
    return call(['nc', '-z', '-w', str(timeout), str(host), str(port)], stderr=open(devnull, 'w')) == 0


# assumes that running 16x2 LCD
def lcd_print(top=None, bottom=None, delay=5):
    display.lcd_clear()
    display.lcd_display_string('{:^16}'.format(top), 1)
    # scroll second line if more than 16 chars
    if len(bottom) > 16:
        display.lcd_display_string(bottom[:16], 2)
        for i in range(len(bottom) - 15):
            display.lcd_display_string(bottom[i:i+16], 2)
            sleep(0.5)
    else:
        display.lcd_display_string('{:^16}'.format(bottom), 2)
    sleep(delay)


def main():
    try:
        lcd_print(top="## Welcome to ##", bottom="## NetMonitor ##", delay=20)
        lcd_print(top="# Who am I?? #",
                  bottom="I am {0} at {1}".format(check_output(['hostname']).split()[0],
                                                  check_output(['hostname', '-I']).split()[0]),
                  delay=10)
        while True:
            # use ping for hosts
            for host, address in hosts.items():
                lcd_print(top="# NetMonitor #",
                          bottom="{} is UP".format(host) if ping(address) else "{} is DOWN".format(host))
            # use netcat for services
            for service, address in services.items():
                lcd_print(top="# NetMonitor #",
                          bottom="{} is UP".format(service) if nc(address['ip'], address['port']) else "{} is DOWN".format(service))
    except KeyboardInterrupt:
        end('Signal to stop', 0)
    except (RuntimeError, IOError):
        end('I2C bus error', 1)


if __name__ == "__main__":
    # create a display object from the Lcd class
    display = drivers.Lcd()
    # customizable dict of unique, pingable hosts
    hosts = {
        'Internet': '8.8.8.8',
        'Firewall': '192.168.1.1',
        'NAS': '192.168.1.2'
    }
    # customizable dict of unique, netcatable services
    services = {
        'Cameras': {'ip': '192.168.1.2', 'port': '8000'},
        'Plex': {'ip': '192.168.1.2', 'port': '32400'}
    }
    main()
