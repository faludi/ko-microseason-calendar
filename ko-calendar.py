# Kō microseasons are a traditional Japanese way of dividing the year into 72 microseasons, each lasting about five days.
# by Rob Faludi 2025

import time
import re
import json
import secrets  # separate file that contains your WiFi credentials
import network
from machine import Pin, reset
import ntptime
import gy_ep204x

version = "1.0.4"
print("Ko Microseason Calendar - Version:", version)

# Wi-Fi credentials
ssid = secrets.WIFI_SSID  # your SSID name
password = secrets.WIFI_PASSWORD  # your WiFi password



month_names = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # Connect to network
    wlan.connect(ssid, password)
    connection_timeout = 10
    while connection_timeout > 0:
        if wlan.status() >= 3:
            break
        connection_timeout -= 1
        print('Waiting for Wi-Fi connection...')
        time.sleep(1)
    # Check if connection is successful
    if wlan.status() != 3:
        print('Failed to establish a network connection')
        return False
    else:
        print('Connection successful!')
        network_info = wlan.ifconfig()
        print('IP address:', network_info[0])
        return True
    
def setup_printer():
    printer = gy_ep204x.GY_EP204X()
    printer.reset()
    printer.send_command(f"\x1B9{chr(1)}")  # Set to Japanese character set
    return printer

def load_microseasons():
    try:
        with open('microseasons.json', 'r') as f:
            microseasons_str = f.read()
            microseasons = json.loads(microseasons_str)
            # print(microseasons)
    except OSError:
        print("Failed to open json file.")
        microseasons = []
    return microseasons

def list_microseasons(microseasons):
    for ms in microseasons['seasons']:
        print(f"{ms['number']:02d}: {ms['en']} ({de_accent(ms['romaji'])}) -> {ms['start']} to {ms['end']}")  

def store_current_season(microseason):
    try:
        with open('current_season.txt', 'w') as f:
            f.write(str(microseason['number']))
    except OSError:
        print("Failed to write current season to file.")

def load_current_season():
    try:
        with open('current_season.txt', 'r') as f:
            season_number = int(f.read())
            return season_number
    except OSError:
        print("Failed to read current season from file.")
        return None
    
def de_accent(str):
    """Removes common accent characters using regex, converts to lowercase."""
    # new_string = old_string.lower()
    str = re.sub(r'[àáâãäå]', 'a', str)
    str = re.sub(r'[èéêë]', 'e', str)
    str = re.sub(r'[ìíîï]', 'i', str)
    str = re.sub(r'[òóôõöō]', 'o', str)
    str = re.sub(r'[ùúûü]', 'u', str)
    return str

def get_microseason_for_date(microseasons, month, day):
    """Returns the microseason for a given month and day."""
    date_str = f"{month:02d}-{day:02d}"
    for ms in microseasons['seasons']:
        if ms['start'] <= date_str <= ms['end']:
            return ms
    return None
    

def print_microseason(printer, microseason):
    printer.center_justify()
    printer.print('================================\n')
    printer.double_height_width()
    printer.bold(True)
    printer.print_with_breaks(f"{microseason['en']}", line_length=16)
    printer.bold(False)
    printer.feed(1)
    printer.triple_height_width()
    printer.print(microseason['kanji'] + '\n')
    printer.normal_size()
    printer.feed(1)
    printer.print_with_breaks(f"{microseason['romaji']}", line_length=32)
    printer.normal_size()
    printer.feed_rows(6)
    printer.print(f"{month_names[int(microseason['start'][:2])]} {int(microseason['start'][3:])} - {month_names[int(microseason['end'][:2])]} {int(microseason['end'][3:])}\n")
    printer.print('================================\n')
    printer.print('\n')

def print_multiple(printer, microseasons, numbers):
    for num in numbers:
        for ms in microseasons['seasons']:
            if ms['number'] == num:
                print_microseason(printer, ms)

last_press_time = 0
def button_pressed(pin):
    global microseasons,printer, last_press_time
    current_time = time.ticks_ms()
    if current_time - last_press_time > 1000:
        print("Button pressed")
        last_press_time = current_time
        microseason = get_microseason_for_date(microseasons, time.localtime()[1], time.localtime()[2])
        print_microseason(printer, microseason)

button = Pin(6, Pin.IN, Pin.PULL_DOWN)
button.irq(trigger=Pin.IRQ_RISING, handler=button_pressed)


def main():
    global microseasons,printer
    connection = False
    connection_timeout = 10
    printer = setup_printer()
    while not connection:
            connection = connect_to_wifi()
            connection_timeout -= 1
            if connection_timeout == 0:
                print('Could not connect to Wi-Fi, exiting')
                reset()
    try:
        ntptime.settime()
        print(f"System time updated to {time.time()} via NTP.")
    except:
        print("Failed to update time via NTP.")
    while True:
            if not connection:
                break # exit if no connection
            microseasons = load_microseasons()
            # list_microseasons(microseasons)
            print(f"Month: {time.localtime()[1]}, Day: {time.localtime()[2]}, Year: {time.localtime()[0]}, Weekday: {time.localtime()[6]}, Yearday: {time.localtime()[7]}")
            # print_multiple(printer, microseasons, [60,61,62,63])  # Example: print microseasons 29 to 32
            season_today = get_microseason_for_date(microseasons, time.localtime()[1], time.localtime()[2])
            if season_today is not None and time.localtime()[3] >= 9:  # Print at 9 am or later
                load_current_season()
                if season_today['number'] != load_current_season():
                    store_current_season(season_today)
                    print_microseason(printer, season_today)
                else:
                    print(f"Microseason {season_today['number']} already printed for today's date.")
            else:
                print("No microseason found for today's date.")

            # Check once every hour, about the top of the hour
            print(f"Sleeping {60-time.localtime()[4]} minutes until next check.")
            time.sleep((60 * (60-time.localtime()[4]))-time.localtime()[5])  # Sleep until the top of the next hour 

main()
            
