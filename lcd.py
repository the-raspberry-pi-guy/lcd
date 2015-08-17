import lcddriver
from time import *

lcd = lcddriver.lcd()

lcd.lcd_display_string("16X2 I2C Display", 1)
lcd.lcd_display_string("Buy@ Ryanteck.uk", 2)
