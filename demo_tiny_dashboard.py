#!/usr/bin/env python
import drivers
from datetime import date
from datetime import time
from datetime import datetime
import time
import threading
import requests
import random
import socket

'''
This is a script that takes info from some apis and shows it in the 16*2 display.
It uses the following apis:

THEYSAIDSO.COM
Free public API that provides famous quotes from well known people.

EXCHANGERATE-API.COM / FREE.CURRENCYCONVERTERAPI.COM
There are a lot of currency apis but these ones offer free currency exchange info

OPENWEATHERMAP.ORG
Weather info, forecasts, etc.

It also shows the last three characters from your ip address, the date in DDMM format
and the hour in HH:MM format
'''

#------------------------------USER VARIABLES---------------------------------------

# Get your api tokens from each site, then put them here, between the quotes. At the time of coding, 
# theysaidso can be freely used without the need of a token, given we respect their restrictions.
api_OpenWeather_token=""
api_freeCurrConv_token=""
api_ExchangeRateAPI_token=""

# api_OpenWeather_yourCity : Search for your city in openweathermap.org, then put the <city,country> code here with no space in between.
api_OpenWeather_yourCity="London,gb"

# Put the currency pair here to see the exchange rate. An amount of 1 curr1 will be converted to curr2
# refer to each api for the list of supported currencies
curr1="USD"
curr2="GBP"

#------------NOTHING ELSE NEEDS TO BE CHANGED BEYOND THIS POINT---------------------

# start the lcd driver
display = drivers.Lcd()

# Global variables go here. These store the info from the apis that we want to display. Do not put anything here.
api_tss_catlist_json=""
disp_string_tss_quote=""
disp_string_convCur_value=""
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
        print("thr1_catlist got response code: " + str(api_tss_catlist_req.status_code))
        global api_tss_catlist_json
        api_tss_catlist_json=api_tss_catlist_req.json() # convert it to json
        print(str(datetime.now()) + " " + "thr1_catlist got a category list update")
        time.sleep(172800) # sleep for 48 hours since it does not update that often

        # need to handle exceptions for this! what happens if the api limit is exceeded?

def get_theysaidso_randomcat():
    '''
    Function that picks a random category from the category list
    It requires api_tss_catlist_json to be already populated 
    It is used by the thread_get_theysaidso_qod
    '''
    global api_tss_catlist_json
    try:
        print("\n" + str(datetime.now()) + " picking a random from these:\n" + str(api_tss_catlist_json['contents']['categories']))
        tss_list_cats=list(api_tss_catlist_json['contents']['categories'].items())
        random_category=random.choice(tss_list_cats)
        print(str(datetime.now()) + " " + "the random category is: " + random_category[0] + "\n")
        return random_category[0]
    except KeyError:
        print(str(datetime.now()) + api_tss_catlist_json['error']['message'])
        # to do: got an error so the quote string should show something about it

def thread_get_theysaidso_qod():
    '''
    We create a base url with the space for the category.
    Then we format it and get a random category with get_theysaidso_randomcat.
    We then convert the response to json and return the string we need to display
    We get a quote every half an hour
    '''
    tss_base_url="https://quotes.rest/qod?category={}"
    while True:
        global disp_string_tss_quote
        try:
            api_tss_quote_request=requests.get(tss_base_url.format(get_theysaidso_randomcat()))
            print("thr2_get_tssqod got response code: " + str(api_tss_quote_request.status_code))
            quote_json=api_tss_quote_request.json()
            disp_string_tss_quote=quote_json['contents']['quotes'][0]['quote'] + " - " + quote_json['contents']['quotes'][0]['author']
            print(str(datetime.now()) + " " + "thr2_get_tssqod got a quote update:\n" + "\t\t" + disp_string_tss_quote)
            time.sleep(2700)
        except KeyError:
            disp_string_tss_quote=quote_json['error']['message']
            print(str(datetime.now()) + " " + "thr2_get_tssqod got an API error:\n" + "\t\t" + disp_string_tss_quote)
            time.sleep(300)
        except ConnectionError:
            disp_string_tss_quote="Connection Error while getting the quote. Will try again in 10 seconds."
            print(str(datetime.now()) + " " + "thr2_get_tssqod got a ConnectionError. will try again in 10 seconds.")
            time.sleep(10)
        except ValueError:
            disp_string_tss_quote="JSON Decode Error while getting the quote. Will try again in 20 seconds."
            print(str(datetime.now()) + " " + "thr2_get_tssqod got a ValueError. will try again in 20 seconds.")
            time.sleep(20)

def thread_get_dollar_conversion(tokenERA=api_ExchangeRateAPI_token, tokenFCC=api_freeCurrConv_token, c1=curr1, c2=curr2):
    ''' 
    This thread gets the 1 usd to cop conversion. 
    Using ExchangeRate API (ERA) as first option. 
    Using Free Currency Convert (FCC) as fallback, 
    Even though FCC updates every hour, it is slow.
    ERA updates once every day. 
    We are prioritizing ERA over FCC. 
    '''
    print(str(datetime.now()) + " " + "starting the currency conversion request")
    while True:
        global disp_string_convCur_value
        try:
            try:
                base_url="https://free.currconv.com/api/v7/convert?q={}_{}&compact=ultra&apiKey={}"
                api_freeCurrConv_request=requests.get(base_url.format(c1, c2, tokenFCC))
                api_freeCurrConv_json=api_freeCurrConv_request.json()
                fcc_rate= c1 + "_" + c2
                disp_string_convCur_value="1" + c1 + ":" + str(round(api_freeCurrConv_json[fcc_rate],2)) + c2
                print(str(datetime.now()) + " " + "thr3_dollarconv got an update from FCC: " + disp_string_convCur_value)
                time.sleep(3600) 
            except (ConnectionError, KeyError, ValueError) as e:
                base_url="https://v6.exchangerate-api.com/v6/{}/pair/{}/{}"
                api_ExchangeRateAPI_request=requests.get(base_url.format(tokenERA, c1, c2))
                api_ExchangeRateAPI_json=api_ExchangeRateAPI_request.json()
                disp_string_convCur_value="1"+ c1 + ":" + str(round(api_ExchangeRateAPI_json['conversion_rate'],2)) + c2
                print(str(datetime.now()) + " " + "thr3_dollarconv got an update from ERA: " + disp_string_convCur_value)
                time.sleep(86400) 
        except KeyError:
            disp_string_convCur_value="JSON Key error on exchange rate response. Check log. Retrying in 5 min."
            print(str(datetime.now()) + " thr3_dollarconv got an API error. \nFCC:" + str(api_freeCurrConv_json) + "\nERA:" + str(api_ExchangeRateAPI_json))
            time.sleep(300)
        except ConnectionError:
            disp_string_convCur_value="Connection Error while getting the exchange rate. Will try again in 10 seconds."
            print(str(datetime.now()) + " thr3_dollarconv got a ConnectionError. will try again in 10 seconds.")
            time.sleep(10)
        except ValueError:
            disp_string_convCur_value="JSON Decode Error while getting the exchange rate. Will try again in 20 seconds."
            print(str(datetime.now()) + " thr3_dollarconv got a ValueError. will try again in 20 seconds.")
            time.sleep(20)

            # We have to find the possible errors that can happen.
            
def thread_get_weather_info(tokenOWM=api_OpenWeather_token, cityid=api_OpenWeather_yourCity):
    '''
    get the weather info for my city
    '''
    global disp_string_weatherInfo
    while True:
        try:
            base_url='https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}'
            api_OpenWeather_request=requests.get(base_url.format(cityid, tokenOWM))
            api_OpenWeather_json=api_OpenWeather_request.json()
            disp_string_weatherInfo=str(round(api_OpenWeather_json['main']['temp'])) + "￟C - " + api_OpenWeather_json['weather'][0]['description'] + " - " + api_OpenWeather_json['name']
            print(str(datetime.now()) + " " + "thr4_weatherinfo got an update: " + disp_string_weatherInfo)
            time.sleep(600)
        except KeyError:
            disp_string_weatherInfo="JSON Key error on weather info response. Check log. Retrying in 5 min."
            print(str(datetime.now()) + " thr4_weatherinfo got an API error. \n" + str(api_OpenWeather_json))
            time.sleep(360)
        except ConnectionError:
            disp_string_weatherInfo="Connection Error while getting the weather info. Will try again in 10 seconds."
            print(str(datetime.now()) + " thr4_weatherinfo got a ConnectionError. will try again in 10 seconds.")
            time.sleep(10)
        except ValueError:
            disp_string_weatherInfo="JSON Decode Error while getting the weather info. Will try again in 20 seconds."
            print(str(datetime.now()) + " thr4_weatherinfo got a ValueError. will try again in 20 seconds.")
            time.sleep(20)

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
            time.sleep(speed)
        time.sleep(1)
    else:
        display.lcd_display_string(text, num_line)

def get_ip():
    '''function to get the ip of this machine
       source: https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib#answer-28950776'''
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

def first_line():
    '''
    The instruction that displays the info in the first line.
    I put it in this function to avoid repeating it. 
    lcd_clear cleans the display so we need to repeat it.
    '''
    # the date
    mytime=time.localtime()
    
    # This shows the last 3 characters of our IP, the day and the month, and lastly the hour, a semicolon and the minutes.
    my_ip = get_ip()
    display.lcd_display_string("i:" + my_ip[-3:] + " " + str(mytime.tm_mday).zfill(2) + str(mytime.tm_mon).zfill(2) + " " + str(mytime.tm_hour) + ":" + str(mytime.tm_min).zfill(2), 1)



# print(dir(drivers))
# print(dir(drivers.Lcd))
print("\nRPi APIS INFO FOR 16X2 DISPLAY. Version a.00\n")

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

    while disp_string_convCur_value == "":
        # we wait for the conversion variable to get populated to start the next thread
        pass
    else:
        thr4_weatherinfo.start()

    # let's see what do we have
    while disp_string_weatherInfo == "":
        pass
    else:
        print("\nSENDING INITIAL INFO TO DISPLAY")

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
            long_string(display, disp_string_convCur_value, 2)
            time.sleep(4)
            display.lcd_clear()

    except KeyboardInterrupt:
        print("\nCleaning the display!")
        display.lcd_clear()
