# Demo program for the I2C 16x2 Display from Ryanteck.uk
# Created by Matthew Timmons-Brown for The Raspberry Pi Guy YouTube channel

# Import necessary libraries for commuunication and display use
import lcddriver
from time import *

# Load the driver and set it to "lcd"
lcd = lcddriver.lcd()

# Remember that your sentences can only be 16 characters long!
lcd.lcd_display_string("Greetings Human!", 1) # Write line of text to first line of display
lcd.lcd_display_string("Demo Pi Guy code", 2) # Write line of text to second line of display
