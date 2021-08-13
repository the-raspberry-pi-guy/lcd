import drivers
from datetime import date
from datetime import time
import time
import get_ip
import threading
import requests
import random

# start the lcd driver
display = drivers.Lcd()

# Global variables go here
api_tss_catlist_json=""
tss_quote_string=""

### HERE WE GET THE INFO WE NEED FROM EITHER THE SYSTEM OR THE APIS ###
def thread_get_theysaidso_catlist():
    ''' get the category list from theysaidso.com '''
    while True:
        api_tss_catlist_req=requests.get("http://quotes.rest/qod/categories.json") # get the category list
        global api_tss_catlist_json
        api_tss_catlist_json=api_tss_catlist_req.json() # convert it to json
        time.sleep(172800) # sleep for 48 hours since it does not update that often

def get_theysaidso_randomcat():
    '''pick a random category from the category list'''
    tss_list_cats=list(api_tss_catlist_json['contents']['categories'].items())
    random_category=random.choice(tss_list_cats)
    return random_category[0]

def thread_get_theysaidso_qod():
    '''We create a base url with the space for the category. Then we format it by get_theysaidso_randomcat . We then convert the response to json and return the string we need to display'''
    tss_base_url="https://quotes.rest/qod?category={}"
    while True:
        api_tss_quote_request=requests.get(tss_base_url.format(get_theysaidso_randomcat()))
        quote_json=api_tss_quote_request.json()
        global tss_quote_string
        tss_quote_string=quote_json['contents']['quotes'][0]['quote'] + " - " + quote_json['contents']['quotes'][0]['author']
        time.sleep(1800)

def get_dollar_conversion():
    # get the 1 usd to cop conversion
    pass

def get_weather_info():
    # get the weather info for my city
    pass

# the date
today = date.today()

print(dir(drivers))
print(dir(drivers.Lcd))

try:
    while True:
        # the date
        mytime=time.localtime()
        
        # Turn off the backlight from 0600 to 1800
        if mytime.tm_hour>=6 and mytime.tm_hour<=18:
            # turn off the backlight
            display.lcd_backlight(0)
        else:
            # turn on the backlight
            display.lcd_backlight(1)


        # This shows the last 3 characters of our IP, the day and the month, and lastly the hour, a semicolon and the minutes.
        my_ip = get_ip.get_ip()
        display.lcd_display_string("i:" + my_ip[-3:] + " " + str(mytime.tm_mday).zfill(2) + str(mytime.tm_mon).zfill(2) + " " + str(mytime.tm_hour) + ":" + str(mytime.tm_min).zfill(2), 1)
        time.sleep(1)

except KeyboardInterrupt:
    print("\nCleaning the display!")
    display.lcd_clear()
