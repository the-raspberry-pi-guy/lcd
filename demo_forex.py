#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import lcddriver
import time
import requests 
import datetime
import locale
import bs4

display = lcddriver.lcd()
sleepSecond = 1
minute = 60
iteration = minute/sleepSecond

selectedCurrencyList = ["USD/TRY","EUR/TRY","EUR/USD","GAU/TRY",u"BİST 100"]

fakeHeaders = {
    'User-Agent': 'Google Chrome'
}

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
    htmlResponse = requests.get(url = "https://tr.investing.com/", headers = fakeHeaders)
    html = htmlResponse.content
    parsedHtml = bs4.BeautifulSoup(html, features="html.parser")
    htmlCurrencyList = parsedHtml.findAll("tr", {"class": "LeftLiContainer"})
    currencyTextList = list()
    for htmlCurrency in htmlCurrencyList:
        currencyName = htmlCurrency.find("td", {"class": "left bold first noWrap"}).find("a").text
        currencyValue = htmlCurrency.find("td", {"class": "lastNum"}).text
        if currencyName in selectedCurrencyList:
            currencyTextList.append(currencyName + " " + currencyValue)
            
    return currencyTextList

while True:
    try:
        currencyList = GetCurrencyList()
        for i in range(iteration/len(currencyList)):
            for item in currencyList:
                PrintScreen(item)
                time.sleep(sleepSecond)
    except:
        display.lcd_clear()
        PrintTime()
        time.sleep(sleepSecond)
