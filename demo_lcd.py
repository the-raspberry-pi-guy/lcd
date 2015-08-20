# Demo program for the I2C 16x2 Display from Ryanteck.uk
# Created by Matthew Timmons-Brown for The Raspberry Pi Guy YouTube channel

# Import necessary libraries for commuunication and display use
import lcddriver
from time import *

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = lcddriver.lcd()

try:
    while True:
        # Remember that your sentences can only be 16 characters long!
        print("Writing to your display!")
        display.lcd_display_string("Greetings Human!", 1) # Write line of text to first line of display
        display.lcd_display_string("Demo Pi Guy code", 2) # Write line of text to second line of display
        time.sleep(5)
        display.lcd_clear()
        time.sleep(2)

except KeyboardInterrupt:
    print("Cleaning up!")
    display.lcd_clear()
