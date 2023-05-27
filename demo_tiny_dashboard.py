#!/usr/bin/env python
import drivers
from datetime import date
from datetime import time
from datetime import datetime
import time
import threading
import requests
import socket

'''
This is a script that takes info from some apis and shows it in the 16*2 display.
It uses the following apis:

QUOTABLE.IO / https://github.com/lukePeavey/quotable
Quotable is a free, open source quotations API that provides famous quotes from well known people.

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

# minimum and maximum length of the quote obtained from quotable.io
quote_minLength=0
quote_maxLength=140

# api_OpenWeather_yourCity : Search for your city in openweathermap.org, then put the <city,country> code here with no space in between.
api_OpenWeather_yourCity="London,GB"

# Put the currency pair here to see the exchange rate. An amount of 1 curr1 will be converted to curr2
# refer to each api for the list of supported currencies
curr1="USD"
curr2="GBP"

#------------NOTHING ELSE NEEDS TO BE CHANGED BEYOND THIS POINT---------------------

# start the lcd driver
display = drivers.Lcd()

# Global variables go here. These store the info from the apis that we want to display. Do not put anything here.
disp_string_quote=""
disp_string_weatherInfo=""
disp_string_convCur_value=""

### HERE WE GET THE INFO WE NEED FROM EITHER THE SYSTEM OR THE APIS ###
def thread_get_quotable():
    ''' 
    This is a thread that gets a random quote from quotable.io every 10 minutes
    '''
    quotable_baseurl="https://api.quotable.io/quotes/random?minLength={}&maxLength={}"

    while True:
        global disp_string_quote
        try:
            api_quotable_req=requests.get(quotable_baseurl.format(quote_minLength, quote_maxLength))
            print("thread_get_quotable got response code: " + str(api_quotable_req.status_code)) # response
            api_quotable_json=api_quotable_req.json() # convert it to json
            disp_string_quote=api_quotable_json[0]['content'] + " - " + api_quotable_json[0]['author']
            print(str(datetime.now()) + " " + "thread_get_quotable got a quote to display:\n" + "\t\t" + disp_string_quote)
            time.sleep(600)
        except KeyError:
            disp_string_quote="There is an error, we need to review log and debug"
            print(str(datetime.now()) + " " + "thread_get_quotable got an API error:\n" + "\t\t" + disp_string_quote)
            time.sleep(300)
        except ConnectionError:
            disp_string_quote="Connection Error while getting the quote. Will try again in 10 seconds."
            print(str(datetime.now()) + " " + "thread_get_quotable got a ConnectionError. will try again in 10 seconds.")
            time.sleep(10)
        except ValueError:
            disp_string_quote="JSON Decode Error while getting the quote. Will try again in 20 seconds."
            print(str(datetime.now()) + " " + "thread_get_quotable got a ValueError. will try again in 20 seconds.")
            time.sleep(20)
        except:
            disp_string_quote="There is an unknown error, we need to review log and debug"

def thread_get_currency_conversion(tokenERA=api_ExchangeRateAPI_token, tokenFCC=api_freeCurrConv_token, c1=curr1, c2=curr2):
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
                base_url="https://v6.exchangerate-api.com/v6/{}/pair/{}/{}"
                api_ExchangeRateAPI_request=requests.get(base_url.format(tokenERA, c1, c2))
                api_ExchangeRateAPI_json=api_ExchangeRateAPI_request.json()
                disp_string_convCur_value="1"+ c1 + ":" + str(round(api_ExchangeRateAPI_json['conversion_rate'],2)) + c2
                print(str(datetime.now()) + " " + "thr3_dollarconv got an update from ERA: " + disp_string_convCur_value)
                time.sleep(86400) 
            except (ConnectionError, KeyError, ValueError) as e:
                base_url="https://free.currconv.com/api/v7/convert?q={}_{}&compact=ultra&apiKey={}"
                api_freeCurrConv_request=requests.get(base_url.format(c1, c2, tokenFCC))
                api_freeCurrConv_json=api_freeCurrConv_request.json()
                fcc_rate= c1 + "_" + c2
                disp_string_convCur_value="1" + c1 + ":" + str(round(api_freeCurrConv_json[fcc_rate],2)) + c2
                print(str(datetime.now()) + " " + "thr3_dollarconv got an update from FCC: " + disp_string_convCur_value)
                time.sleep(3600) 
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


print("\nRPi TINY DASHBOARD FOR 16X2 DISPLAY.\n")

# CREATING AND CALLING THREADS STARTS HERE
if __name__=="__main__":
    # Start by declaring all these threads
    thr1_get_quotable=threading.Thread(target=thread_get_quotable, daemon=True)
    thr2_currconv=threading.Thread(target=thread_get_currency_conversion, daemon=True)
    thr3_weatherinfo=threading.Thread(target=thread_get_weather_info, daemon=True)
    
    # Then we start the threads that populate the variables
    # We wait while the global variables get populated, then start the threads.

    thr1_get_quotable.start()

    while disp_string_quote == "":
        # we wait for the quotes string to start the next thread
        pass
    else:
        thr2_currconv.start()

    while disp_string_convCur_value == "":
        # we wait for the conversion variable to get populated to start the next thread
        pass
    else:
        thr3_weatherinfo.start()

    # let's see what do we have
    while disp_string_weatherInfo == "":
        pass
    else:
        print("\nSENDING INITIAL INFO TO DISPLAY")

    # THIS IS WHERE WE SEND THE INFO TO THE DISPLAY
    try:
        while True:
            ''' display first line and quote '''
            first_line() 
            long_string(display, disp_string_quote, 2)
            time.sleep(2)
            display.lcd_clear()
            
            ''' display first line and weather info '''
            first_line() 
            long_string(display, disp_string_weatherInfo, 2)
            time.sleep(2)
            display.lcd_clear()

            ''' display first line and currency conversion '''
            first_line() 
            long_string(display, disp_string_convCur_value, 2)
            time.sleep(4)
            display.lcd_clear()

    except KeyboardInterrupt:
        print("\nCleaning the display!")
        display.lcd_clear()
