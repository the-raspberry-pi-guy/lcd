import drivers
from datetime import date
from datetime import time
import socket
import time

# start the lcd driver
display = lcddriver.lcd()


# the date
today = date.today()

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

print(dir(lcddriver))
print(dir(lcddriver.lcd))
#display.lcd_backlight_off()

try:
    while True:
        # the date
        mytime=time.localtime()
        
        my_ip = get_ip()
        display.lcd_display_string("ip:" + my_ip[-2:] + " " + str(mytime.tm_mday).zfill(2) + str(mytime.tm_mon).zfill(2) + " " + str(mytime.tm_hour) + ":" + str(mytime.tm_min).zfill(2), 1)
        time.sleep(1)

except KeyboardInterrupt:
    print("Cleaning the display!")
    display.lcd_clear()
