#! /usr/bin/env python

# Extended strings program. Writes and updates special (extended) strings
# with placeholders "{}" so, that it is possible to draw any character from the 
# characters table using a caharcter code.
# Demo program for the I2C 16x2 Display from Ryanteck.uk
# Created by Matthew Timmons-Brown for The Raspberry Pi Guy YouTube channel

# Import necessary libraries for communication and display use
import drivers
from time import sleep

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = drivers.Lcd()

# Main body of code
try:
    while True:
        # Remember that your sentences can only be 16 characters long!
        print("Writing simple string")
        display.lcd_display_string("Simple string", 1)  # Write line of text to first line of display
        display.lcd_display_extended_string("Ext. str:{0xEF}{0xF6}{0xA5}{0xDF}{0xA3}", 2)  # Write line of text to second line of display
        sleep(2) # Give time for the message to be read
except KeyboardInterrupt:
    # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    display.lcd_clear()
