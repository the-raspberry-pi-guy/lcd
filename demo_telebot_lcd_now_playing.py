#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import json
import os
import subprocess
from datetime import datetime
from time import sleep
from time import strftime

import spotipy
import telepot
from gpiozero import CPUTemperature
from gpiozero import OutputDevice
from spotipy.oauth2 import SpotifyOAuth
from telepot.loop import MessageLoop

# Import necessary libraries for communication and display use
import drivers


# House temperature
def ds18b20(temp_file):
    temp_file = open(temp_file)
    temp = temp_file.read()
    temp_file.close()
    temp_value = temp.split("\n")[1]
    temp_output = temp_value.split(" ")[9]
    return float(temp_output[2:]) / 1000


# Session state backlight
def backlight(value):
    session_state_backlight['backlight'] = {'is_backlight': value}


# Commands from Telegram Bot
def handle(msg):
    chat_id_input = msg['chat']['id']
    command = msg['text']

    if chat_id_input == chat_id_owner:

        # Command to ON/OFF LCD
        if command == '/lcd_off':
            backlight(0)
            bot.sendMessage(chat_id_owner, "LCD OFF")
        elif command == '/lcd_on':
            backlight(1)
            bot.sendMessage(chat_id_owner, "LCD ON")

        # Get temperature of CPU and DS18B20
        elif command == '/temp':
            bot.sendMessage(chat_id_owner, f'CPU: {cpu[0:4]}°C\nHouse: {house_temp[0:4]}°C ')

        # Update Raspberry
        elif command == '/quick_update':
            weekly_update.on()
            bot.sendMessage(chat_id_owner, 'Starting update...')
            os.system('sudo apt-get update -y')
            bot.sendMessage(chat_id_owner, 'Update done.\nStarting upgrade...')
            os.system('sudo apt-get upgrade -y')
            bot.sendMessage(chat_id_owner, 'Upgrade done')
        elif command == '/update':
            weekly_update.on()
            bot.sendMessage(chat_id_owner, 'Starting update...')
            os.system('sudo apt-get update -y')
            bot.sendMessage(chat_id_owner, 'Update done.\nStarting upgrade...')
            os.system('sudo apt-get upgrade -y')
            bot.sendMessage(chat_id_owner, 'Upgrade done.\nStarting autoremove...')
            os.system('sudo apt-get autoremove -y')
            bot.sendMessage(chat_id_owner, 'Autoremove done.\nStarting reboot...\nSee U soon')
            # os.system('sudo reboot now')

        # Control Raspberry
        elif command == '/reboot':
            bot.sendMessage(chat_id_owner, 'See U soon')
            os.system('sudo reboot now')
        elif command == '/shutdown':
            bot.sendMessage(chat_id_owner, 'Seen U soon')
            os.system('sudo shutdown now')

        # Commands for testing bot and components + help
        elif command == '/test':
            bot.sendMessage(chat_id_owner, 'test')
        elif command == '/fan_on':
            fan.on()
        elif command == '/fan_off':
            fan.off()
        elif command == '/update_on':
            weekly_update.on()
        elif command == '/update_off':
            weekly_update.off()
        elif command == '/help_test':
            bot.sendMessage(chat_id_owner,
                            "/fan_on - /fan_off - Test the fan\n"
                            "/update_on - /update_off - Test LED update\n"
                            "/test - Is bot actived ?")
        elif command == '/help':
            bot.sendMessage(chat_id_owner,
                            "/temp - Get temperature\n"
                            "/quick_update - To update and upgrade without autoremove and reboot\n"
                            "/update - To update, upgrade and autoremove AND REBOOT\n"
                            "/shutdown - As excepted\n"
                            '/lcd_on - As excepted\n'
                            '/lcd_off - As excepted\n'
                            "/help - A little reminder")
        else:
            bot.sendMessage(chat_id_owner, "I don't understand... Try /help or /help_test")

    # Avoid an intrusion
    else:
        bot.sendMessage(chat_id_input, f"You are not allowed, your ID is {str(chat_id_input)}.")
        bot.sendMessage(chat_id_owner, f"Someone trying to do something strange...\nID: {str(chat_id_input)}\n"
                                       f"Message: {str(command)}")


# Retrieve information of connection to Telegram Bot, Spotify API, GPIO etc...
os.chdir("/home/pi/lcd/")  # To find .cache

script_directory = os.path.dirname(os.path.abspath(__file__))
secrets_path = os.path.join(script_directory, 'SECRETS.json')
with open(secrets_path, 'r') as secrets_file:
    secrets = json.load(secrets_file)
chat_id_owner = secrets['id_owner']
token = secrets['token']

CLIENT_ID = secrets['CLIENT_ID']
CLIENT_SECRET = secrets['CLIENT_SECRET']
REDIRECT_URI = secrets['REDIRECT_URI']
while True:
    try:
        cache_access = subprocess.check_output("ls -l .cache", shell=True, text=True)

        if not "rwsrwsrwt" in cache_access:
            print(cache_access)
            print('Error: Bad permissions for .cache')
            print('Execution: All permissions for .cache')
            os.system('sudo chmod 7777 .cache')
        else:
            print('Success: .cache has required permissions')
            break
    except subprocess.CalledProcessError as e:
        print(f'Error during execution: {e}')

ON_THRESHOLD = secrets["ON_THRESHOLD"]
OFF_THRESHOLD = secrets['OFF_THRESHOLD']
SHUTDOWN_THRESHOLD = secrets['SHUTDOWN_THRESHOLD']

temp_file = glob.glob("/sys/bus/w1/devices/28*/w1_slave")  # File location for ambient temp from D18B20
GPIO_PIN_FAN = 17  # Fan control
GPIO_PIN_UPDATE = 27  # LED update control

fan = OutputDevice(GPIO_PIN_FAN)
weekly_update = OutputDevice(GPIO_PIN_UPDATE)
update_list = ['02:00', '02:30']
session_state_backlight = {}  # On/off LCD backlight

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = drivers.Lcd()

# Custom character for LCD
cc = drivers.CustomCharacters(display)

cc.char_1_data = ["01010",  # CPU 0x00
                  "11111",
                  "10001",
                  "10101",
                  "10001",
                  "11111",
                  "01010",
                  "00000"]

cc.char_2_data = ["00100",  # House 0x01
                  "01110",
                  "11011",
                  "10001",
                  "10101",
                  "10101",
                  "11111",
                  "00000"]

cc.char_3_data = ["00011",  # Music 0x02
                  "00111",
                  "01101",
                  "01001",
                  "01001",
                  "01011",
                  "11011",
                  "11000"]

cc.load_custom_characters_data()  # Load custom characters for LCD

# Connection to Spotify API
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI,
                              scope='user-read-playback-state'))

# Start LCD
session_state_backlight['backlight'] = {'is_backlight': 1}
display.lcd_clear()
print('Success: LCD ON')
display.lcd_display_string("  Hello  World  ", 1)

# Start Telegram Bot
bot = telepot.Bot(token)
MessageLoop(bot, {'chat': handle}).run_as_thread()  # For receive command from Telegram Bot
print('Success: Telebot ON')
bot.sendMessage(chat_id_owner, 'Hello World 😊')

# Loop for LCD
while True:
    # Retrieve ambient and CPU temperatures and gestion
    cpu = CPUTemperature()
    temp = cpu.temperature
    cpu = str(temp)
    if len(temp_file) > 0:
        temperature = ds18b20(temp_file[0])
        house_temp = str(temperature)
    else:
        print("DS18B20 not detected")

    if temp > ON_THRESHOLD and not fan.value:  # Warning hot temperature
        fan.on()
        bot.sendMessage(chat_id_owner, f"WARNING! Temperature too HOT! {cpu[0:4]}°C")
    elif temp > SHUTDOWN_THRESHOLD:  # Alert too hot temperature  + shutdown
        fan.on()
        bot.sendMessage(chat_id_owner, f"ALERT! CRITICAL TEMPERATURE! {cpu[0:4]}°C ! SHUTDOWN !")
        os.system('sudo shutdown now')
    elif temp < OFF_THRESHOLD and fan.value:  # Temperature under control
        fan.off()
        bot.sendMessage(chat_id_owner, f"Temperature under control. {cpu[0:4]}°C. Good job !")

    # Retrieve date and time
    now = datetime.now()
    hour = now.strftime("%H:%M")
    date = now.strftime("%d")
    day = now.weekday()

    if day == 0 and hour == '02:30' and not weekly_update.value:  # Little update
        weekly_update.on()
        bot.sendMessage(chat_id_owner, 'Starting weekly update...')
        os.system('sudo apt-get update -y')
        bot.sendMessage(chat_id_owner, 'Weekly update done.\nStarting weekly upgrade...')
        os.system('sudo apt-get upgrade -y')
        bot.sendMessage(chat_id_owner, 'Weekly upgrade done')
    elif date == '1' and hour == '02:00' and not weekly_update.value:  # Major update
        weekly_update.on()
        bot.sendMessage(chat_id_owner, 'Starting monthly update...')
        os.system('sudo apt-get update -y')
        bot.sendMessage(chat_id_owner, 'Monthly update done.\nStarting monthly upgrade...')
        os.system('sudo apt-get upgrade -y')
        bot.sendMessage(chat_id_owner, 'Monthly upgrade done.\nStarting monthly autoremove...')
        os.system('sudo apt-get autoremove -y')
        bot.sendMessage(chat_id_owner, 'Monthly autoremove done.\nStarting reboot...\nSee U soon')
        # os.system('sudo reboot now')
    elif hour not in update_list and weekly_update.value:
        weekly_update.off()

    # Retrieve now playing on Spotify
    current_track = sp.current_playback()
    if current_track is not None and 'is_playing' in current_track and not current_track['is_playing']:
        pause = 1
    elif current_track is not None and 'item' in current_track:
        pause = 0
        track_name = current_track['item']['name']
        artists = ', '.join([artist['name'] for artist in current_track['item']['artists']])
        music = f"{track_name}-{artists}"
    else:
        pause = 1

    # Display on LCD
    if session_state_backlight['backlight']['is_backlight'] == 1:  # LCD backlight ON (default)
        display.lcd_backlight(1)

        display.lcd_clear()  # Avoid having residual characters
        display.lcd_display_string(str(strftime("%a %d.%m  %H:%M")), 1)  # Line 1

        if pause == 1:
            display.lcd_display_extended_string(' {0x00} ' + cpu[0:4] + '  {0x01} ' + house_temp[0:4], 2)  # Line 2
            sleep(5)
        else:
            display.lcd_display_extended_string('{0x02}{0x00} ' + cpu[0:4] + '  {0x01} ' + house_temp[0:4], 2)
            sleep(1)

            if len(music) > 16:  # If music are longer than lcd (16 blocs), scroll it !
                display.lcd_display_extended_string('{0x02}' + music[:16], 2)
                for i in range(len(music) - 15):
                    display.lcd_display_extended_string('{0x02}' + music[i:i + 16], 2)
                    sleep(0.5)
            else:
                display.lcd_display_extended_string('{0x02}' + '{:^16}'.format(music), 2)

            display.lcd_display_extended_string('{0x02}{0x00} ' + cpu[0:4] + '  {0x01} ' + house_temp[0:4], 2)
            sleep(1)

    elif session_state_backlight['backlight']['is_backlight'] == 0:  # LCD backlight OFF
        display.lcd_backlight(0)
        sleep(1)
