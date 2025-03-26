#! /usr/bin/env python

# Just a 16x2 LCD screen simulator using Tkinter, allowing for easy testing and
# visualization of LCD displays without physical hardware. This simulator helps
# in developing and debugging LCD-based projects directly from a computer.

# Import necessary libraries for communication and display use
import emulators
from time import sleep
from datetime import datetime


# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = emulators.LcdEmulator()

# Create object with custom characters data
cc = emulators.CustomCharactersEmulator(display)

# Redefine the default characters:
# Custom caracter #1. Code {0x00}.
cc.char_1_data = ["01010", "11111", "10001", "10101", "10001", "11111", "01010", "00000"]

# Load custom characters data to CG RAM:
cc.load_custom_characters_data()

# Main body for code
try:
    i = 0
    while True:
        display.lcd_clear()

        display.lcd_display_string(' Hello, World !', line=1)
        if i < 1:
            display.lcd_backlight(1)
            text = "This is a simulation of a 16x2 LCD"
            for j in range(len(text) - 14):
                text2 = "{0x00}" + text[j:j + 15]
                display.lcd_display_extended_string(text2, 2)
                sleep(0.15)
            i += 1

        elif 1 <= i <= 10:
            display.lcd_backlight(0)
            display.lcd_display_string(str(datetime.now().time()), 2)
            i += 1

        elif 11 <= i <= 20:
            display.lcd_display_string("    ENJOY :)    ", line=2)
            i += 1

        if i > 20:
            i = 0

        sleep(0.5)

except KeyboardInterrupt:
    # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    display.lcd_clear()



