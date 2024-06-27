#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import drivers
import time
import requests 
import datetime
from bs4 import BeautifulSoup

display = drivers.Lcd()
sleepSecond = 1
minute = 60
iteration = minute/sleepSecond

def GetTime():
    currentTime = datetime.datetime.now()
    return currentTime.strftime("%d.%m %a %H:%M")

def PrintTime():
    display.lcd_display_string(GetTime(), 1)

def PrintCurrency(currency):
    display.lcd_display_string(currency, 2)

def PrintScreen(currency):
    display.lcd_clear()
    PrintTime()
    PrintCurrency(currency)

def GetCurrencyList():
    try:
        request = requests.get("https://www.investing.com/currencies/")
        html_content = request.content
        # parse content
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table', id='cr1')
        rows = table.find('tbody').find_all('tr')
        currencies_list = {}
        for row in rows:
            cells = row.find_all('td')
            pair = cells[1].find('a').text.strip()
            value = cells[2].text.strip()
            currencies_list[pair] = value
        return currencies_list
    except Exception as e:
        print(f"Failed to get currency list\n Error: {e}")
        return False

# main logic
try:
    while True:
        currencyList = GetCurrencyList()
        if currencyList:
            for i in range(int(iteration/len(currencyList))):
                for item in currencyList:
                    PrintScreen(f"{item} {currencyList.get(item)}")
                    time.sleep(sleepSecond)
        else:
            display.lcd_clear()
            PrintTime()
            time.sleep(sleepSecond)

except KeyboardInterrupt:
    print("Cleaning up!")
    display.lcd_clear()