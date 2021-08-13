# -*- coding: utf-8 -*-
# Example: Scrolling text on display if the string length is major than columns in display.
# Created by Dídac García.

# Import necessary libraries for communication and display use
import lcddriver
import time

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = lcddriver.lcd()

# Main body of code
try:
	print("Press CTRL + C for stop this script!")

	def long_string(display, text = '', num_line = 1, num_cols = 16):
		""" 
		Parameters: (driver, string to print, number of line to print, number of columns of your display)
		Return: This function send to display your scrolling string.
		"""
		if(len(text) > num_cols):                                           # if the text length is greater than the number of columns in the display
			display.lcd_display_string(text[:num_cols],num_line)        # display the text string using all the columns (from position 0 to num_cols) at the display line specified by num_line
			time.sleep(1)                                               # Sleeps the execution for 1 second
			for i in range(len(text) - num_cols + 1):                   # The number of iterations is given by the lenght of the text minus the number of columns plus 1
				text_to_print = text[i:i+num_cols]                  # Is it me or does python increase the control variable on its own? What's this sorcery! text_to_print is a range of the text that gets updated on each iteration. This is what makes the text scroll!
				display.lcd_display_string(text_to_print,num_line)  # And this is what displays the text!
				time.sleep(0.05)                                     # This is the pause between each "text push". Will a smaller value make the scroll softer or more or less readable?
			time.sleep(1)                                               # After the text has been displayed completely, make a pause.
		else:
			display.lcd_display_string(text,num_line)                   # if the text is smaller than the number of columns, just display it.


	# Example of short string
	#long_string(display, "Nietzche", 1)
	#time.sleep(1)

	# Example of long string
	#long_string(display, "All things are subject to interpretation. Whichever interpretation prevails at a given time is a function of power and not truth.", 2)

	#display.lcd_clear()
	#time.sleep(1)

	while True:
		# An example of infinite scrolling text
		long_string(display, "F. Nietzche",2)
		long_string(display, "All things are subject to interpretation. Whichever interpretation prevails at a given time is a function of power and not truth.", 1)

except KeyboardInterrupt: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
	print("Cleaning up!")
	display.lcd_clear()
