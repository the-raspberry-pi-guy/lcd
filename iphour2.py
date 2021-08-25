import drivers
from datetime import date
from datetime import time
from datetime import datetime
import time
import get_ip
import threading
import requests
import random

# start the lcd driver
display = drivers.Lcd()

# Global variables go here
api_tss_catlist_json=""
disp_string_tss_quote=""
disp_string_usd2cop_value=""
disp_string_weatherInfo=""

### HERE WE GET THE INFO WE NEED FROM EITHER THE SYSTEM OR THE APIS ###
def thread_get_theysaidso_catlist():
    ''' 
    This is a thread that gets the category list from theysaidso.com
    and puts it in the global variable api_tss_catlist_json
    Then it sleeps for 48 hours to save on requests to tss
    '''
    while True:
        api_tss_catlist_req=requests.get("http://quotes.rest/qod/categories.json") # get the category list
        global api_tss_catlist_json
        api_tss_catlist_json=api_tss_catlist_req.json() # convert it to json
        print("thr1_catlist got a category list update")
        time.sleep(172800) # sleep for 48 hours since it does not update that often

def get_theysaidso_randomcat():
    '''
    Function that picks a random category from the category list
    It is used by the thread_get_theysaidso_qod
    '''
    global api_tss_catlist_json
    try:
        print("\npicking a random from these:")
        print(api_tss_catlist_json['contents']['categories'])
        tss_list_cats=list(api_tss_catlist_json['contents']['categories'].items())
        random_category=random.choice(tss_list_cats)
        print("the random category is: " + random_category[0] + "\n")
        return random_category[0]
    except KeyError:
        print(api_tss_catlist_json['error']['message'])

def thread_get_theysaidso_qod():
    '''
    We create a base url with the space for the category.
    Then we format it and get a random category with get_theysaidso_randomcat.
    We then convert the response to json and return the string we need to display
    We get a quote every half an hour
    '''
    tss_base_url="https://quotes.rest/qod?category={}"
    while True:
        api_tss_quote_request=requests.get(tss_base_url.format(get_theysaidso_randomcat()))
        quote_json=api_tss_quote_request.json()
        global disp_string_tss_quote
        disp_string_tss_quote=quote_json['contents']['quotes'][0]['quote'] + " - " + quote_json['contents']['quotes'][0]['author']
        print("thr2_get_tssqod got a quote update")
        time.sleep(1800)

def thread_get_dollar_conversion():
    ''' 
    This thread gets the 1 usd to cop conversion. 
    Using ExchangeRate API (ERA) as first option. 
    Using Free Currency Convert (FCC) as fallback, 
    Even though FCC updates every hour, it is slow.
    ERA updates once every day. 
    We are prioritizing ERA over FCC. 
    '''
    print(str(datetime.now()) + " " + "debug: starting the usd2cop request")
    while True:
        global disp_string_usd2cop_value
        try:
            api_ExchangeRateAPI_request=requests.get("https://v6.exchangerate-api.com/v6/e737393710effa1bc6705aa0/pair/USD/COP")
            api_ExchangeRateAPI_json=api_ExchangeRateAPI_request.json()
            disp_string_usd2cop_value="1USD:" + str(round(api_ExchangeRateAPI_json['conversion_rate'])) + "COP"
            print(str(datetime.now()) + " " + "thr3_dollarconv got an update from ERA")
            time.sleep(86400) 
        except:
            api_freeCurrConv_request=requests.get("https://free.currconv.com/api/v7/convert?q=USD_COP&compact=ultra&apiKey=a252cb255d5e022f74e3")
            api_freeCurrConv_json=api_freeCurrConv_request.json()
            disp_string_usd2cop_value="1USD:" + str(round(api_freeCurrConv_json['USD_COP'])) + "COP"
            print(str(datetime.now()) + " " + "thr3_dollarconv got an update from FCC")
            time.sleep(3600) 
        finally:
            pass
            # disp_string_usd2cop_value="ERROR"
            # We have to find the possible errors that can happen. Remember the "finally:" section always runs, so putting ERROR in the variable is not appropriate
            
def thread_get_weather_info():
    '''
    get the weather info for my city
    '''
    while True:
        api_OpenWeather_request=requests.get('https://api.openweathermap.org/data/2.5/weather?q=Cali,co&units=metric&appid=9e85305f83b9cf3a5424d8a120072db7')
        api_OpenWeather_json=api_OpenWeather_request.json()
        global disp_string_weatherInfo
        disp_string_weatherInfo=str(round(api_OpenWeather_json['main']['temp'])) + "C - " + api_OpenWeather_json['weather'][0]['description'] + " - " + api_OpenWeather_json['name']
        print("thr4_weatherinfo got an update")
        time.sleep(300)

# Taken from the raspberry pi guy's sample, demo_scrollingtext.py
def long_string(display, text='', num_line=2, num_cols=16, speed=0.1):
    """ 
    Parameters: (driver, string to print, number of line to print, number of columns of your display)
    Return: This function send to display your scrolling string.
    """
    if len(text) > num_cols:
        display.lcd_display_string(text[:num_cols], num_line)
        time.sleep(3)
        for i in range(len(text) - num_cols + 1):
            text_to_print = text[i:i+num_cols]
            display.lcd_display_string(text_to_print, num_line)
            time.sleep(0.1)
        time.sleep(1)
    else:
        display.lcd_display_string(text, num_line)

def first_line():
    '''
    The instruction that displays the info in the first line.
    I put it in this function to avoid repeating it. 
    lcd_clear cleans the display so we need to repeat it.
    '''
    # the date
    mytime=time.localtime()
    
    # This shows the last 3 characters of our IP, the day and the month, and lastly the hour, a semicolon and the minutes.
    my_ip = get_ip.get_ip()
    display.lcd_display_string("i:" + my_ip[-3:] + " " + str(mytime.tm_mday).zfill(2) + str(mytime.tm_mon).zfill(2) + " " + str(mytime.tm_hour) + ":" + str(mytime.tm_min).zfill(2), 1)


print(dir(drivers))
print(dir(drivers.Lcd))

# CREATING AND CALLING THREADS STARTS HERE
if __name__=="__main__":
    # Start by declaring all these threads
    thr1_catlist=threading.Thread(target=thread_get_theysaidso_catlist, daemon=True)
    thr2_get_tssqod=threading.Thread(target=thread_get_theysaidso_qod, daemon=True)
    thr3_dollarconv=threading.Thread(target=thread_get_dollar_conversion, daemon=True)
    thr4_weatherinfo=threading.Thread(target=thread_get_weather_info, daemon=True)
    
    # Then we start the threads that populate the variables
    thr1_catlist.start()

    while api_tss_catlist_json == "":
        # we wait for the categories info, then load thread 2
        pass
    else:
        thr2_get_tssqod.start()

    while disp_string_tss_quote == "":
        # we wait for the quotes string to start the next thread
        pass
    else:
        thr3_dollarconv.start()

    while disp_string_usd2cop_value == "":
        # we wait for the conversion variable to get populated to start the next thread
        pass
    else:
        thr4_weatherinfo.start()

    # let's see what do we have
    while disp_string_weatherInfo == "":
        pass
    else:
        print("\nINFO TO DISPLAY:")
        print(disp_string_tss_quote)
        print(disp_string_usd2cop_value)
        print(disp_string_weatherInfo + "\n")

    # THIS IS WHERE WE SEND THE INFO TO THE DISPLAY
    try:
        while True:
            first_line() 
            long_string(display, disp_string_tss_quote, 2)
            time.sleep(2)
            display.lcd_clear()
            
            first_line() 
            long_string(display, disp_string_weatherInfo, 2)
            time.sleep(2)
            display.lcd_clear()

            first_line() 
            long_string(display, disp_string_usd2cop_value, 2)
            time.sleep(4)
            display.lcd_clear()

    except KeyboardInterrupt:
        print("\nCleaning the display!")
        display.lcd_clear()
