# Kō microseasons are a traditional Japanese way of dividing the year into 72 microseasons, each lasting about five days.
# by Rob Faludi 2025

import time
import re
import json
import secrets  # separate file that contains your WiFi credentials
import network
from machine import Pin, reset, RTC
import ntptime
import gy_ep204x

version = "1.0.15"
print("Ko Microseason Calendar - Version:", version)

# Wi-Fi credentials
ssid = secrets.WIFI_SSID  # your SSID name
password = secrets.WIFI_PASSWORD  # your WiFi password

UTC_OFFSET = -5  # Adjust as needed for your timezone
USE_DST = True  # Set to True if your timezone observes Daylight Saving Time

show_macro_season = True  # Set to True to print macro seasons
show_mini_season = True  # Set to True to print mini seasons

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
    printer = gy_ep204x.GY_EP204X(baudrate=115200, tx_pin=4, rx_pin=5)
    printer.reset()
    printer.set_japanese_charset()  # Set to Japanese character set
    return printer

def load_microseasons():
    try:
        with open('microseasons_ko.json', 'r') as f:
            microseasons_str = f.read()
            microseasons = json.loads(microseasons_str)
            # print(microseasons)
    except OSError:
        print("Failed to open json file.")
        microseasons = []
    return microseasons

def load_mini_seasons():
    try:
        with open('mini_seasons_sekki.json', 'r') as f:
            mini_seasons_str = f.read()
            mini_seasons = json.loads(mini_seasons_str)
            # print(mini_seasons)
    except OSError:
        print("Failed to open json file.")
        mini_seasons = []
    return mini_seasons

def load_seasons():
    try:
        with open('seasons_shiki.json', 'r') as f:
            seasons_str = f.read()
            seasons = json.loads(seasons_str)
            # print(seasons)
    except OSError:
        print("Failed to open json file.")
        seasons = []
    return seasons

def print_macro_season(printer):
    macro_seasons = load_seasons()
    for macro in macro_seasons:
        try:
            sm, sd = map(int, macro['start'].split('-'))
            em, ed = map(int, macro['end'].split('-'))
        except Exception:
            continue
        if sm == local_time(UTC_OFFSET)[1] and sd == local_time(UTC_OFFSET)[2]:
            print(f"Printing season: {macro['en']}")
            printer.center_justify()
            printer.print('===============[]=============\n')
            printer.double_height_width()
            printer.bold(True)
            printer.print_with_breaks(f"{macro['en']}", line_length=16)
            printer.bold(False)
            printer.feed(1)
            printer.set_japanese_charset() # Set to Japanese character set
            printer.triple_height_width()
            printer.print(macro['kanji'] + '\n')
            printer.normal_size()
            printer.feed_rows(6)
            printer.print_with_breaks(f"{macro['romaji']}", line_length=32)
            printer.normal_size()
            printer.feed(1)
            printer.bold(True)
            printer.print(f"{month_names[sm-1]} {sd} - {month_names[em-1]} {ed}\n")
            printer.bold(False)
            printer.feed(1)

def print_mini_season(printer):
    mini_seasons = load_mini_seasons()
    for mini in mini_seasons:
        try:
            sm, sd = map(int, mini['start'].split('-'))
            em, ed = map(int, mini['end'].split('-'))
        except Exception:
            continue
        if sm == local_time(UTC_OFFSET)[1] and sd == local_time(UTC_OFFSET)[2]:
            print(f"Printing mini season: {mini['en']}")
            printer.center_justify()
            printer.print('===============[ ]=============\n')
            printer.double_height_width()
            printer.bold(True)
            printer.print_with_breaks(f"{mini['en']}", line_length=16)
            printer.bold(False)
            printer.feed(1)
            printer.set_japanese_charset()  # Set to Japanese character set
            printer.triple_height_width()
            printer.print(mini['kanji'] + '\n')
            printer.normal_size()
            printer.feed_rows(6)
            printer.print_with_breaks(f"{mini['romaji']}", line_length=32)
            printer.normal_size()
            printer.feed(1)
            printer.bold(True)
            printer.print(f"{month_names[sm-1]} {sd} - {month_names[em-1]} {ed}\n")
            printer.bold(False)
            printer.feed(1)

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
    except (OSError, ValueError):
        store_current_season({"number": 0}) # initialize file if not present
        print("Failed to read current season from file, initializing.")
        return 0
    
def de_accent(str):
    """Removes common accent characters using regex, converts to lowercase."""
    # new_string = old_string.lower()
    str = re.sub(r'[àáâãäå]', 'a', str)
    str = re.sub(r'[èéêë]', 'e', str)
    str = re.sub(r'[ìíîï]', 'i', str)
    str = re.sub(r'[òóôõöō]', 'o', str)
    str = re.sub(r'[ùúûü]', 'u', str)
    return str

def get_microseason_for_number(microseasons, number):
    for ms in microseasons.get('seasons', []):
        if ms['number'] == number:
            return ms
    return None

def get_microseason_for_date(microseasons, month, day):
    # Returns the microseason for a given month and day, handling year-end wraparound
    # ensure month/day are ints
    try:
        date = (int(month), int(day))
    except Exception:
        return None
    for ms in microseasons.get('seasons', []):
        try:
            sm, sd = map(int, ms['start'].split('-'))
            em, ed = map(int, ms['end'].split('-'))
        except Exception:
            continue
        start = (sm, sd)
        end = (em, ed)
        if start <= end:
            # normal range within the same year
            if start <= date <= end:
                return ms
        else:
            # wraparound range (e.g., starts in December, ends in January)
            if date >= start or date <= end:
                return ms
    return None 

def print_microseason(printer, microseason):
    print(f"Printing microseason {microseason['number']}: {microseason['en']}")
    printer.center_justify()
    printer.print('===============[●]=============\n')
    printer.double_height_width()
    printer.bold(True)
    printer.print_with_breaks(f"{microseason['en']}", line_length=16)
    printer.bold(False)
    printer.feed(1)
    printer.triple_height_width()
    printer.set_japanese_charset()  # Set to Japanese character set
    printer.print(microseason['kanji'] + '\n')
    printer.normal_size()
    printer.feed_rows(6)
    printer.print_with_breaks(f"{microseason['romaji']}", line_length=32)
    printer.normal_size()
    printer.feed(1)
    printer.bold(True)
    printer.print(f"{month_names[int(microseason['start'][:2])-1]} {int(microseason['start'][3:])} - {month_names[int(microseason['end'][:2])-1]} {int(microseason['end'][3:])}\n")
    printer.bold(False)
    printer.feed(1)
    printer.print('===============[●]=============\n')

# def print_multiple(printer, microseasons, numbers):
#     for num in numbers:
#         for ms in microseasons['seasons']:
#             if ms['number'] == num:
#                 print_microseason(printer, ms)

def local_time( UTC_offset= -4 ):
    """Returns local time tuple adjusted for given UTC offset in hours, with rough adjustment for DST."""
    t = time.time() + (UTC_offset * 3600)
    if USE_DST:
        # Simple DST adjustment: add 1 hour if in DST period (e.g., March to October)
        month = time.localtime(t)[1]
        if 3 <= month <= 10:
            t += 3600
    return time.localtime(t)

def show_time():
    lt = local_time(UTC_OFFSET)
    print(f"Local time: {lt[0]:04d}-{lt[1]:02d}-{lt[2]:02d} {lt[3]:02d}:{lt[4]:02d}:{lt[5]:02d}")

last_press_time = manual_season = 0
def button_pressed(pin):
    global microseasons, printer, last_press_time, manual_season
    current_time = time.ticks_ms()
    if current_time - last_press_time > 500:
        print("Button pressed")
        if current_time - last_press_time > 10000:
            manual_season = load_current_season()
        last_press_time = current_time
        if manual_season > 72:
                manual_season = 1
        microseason = get_microseason_for_number(microseasons, manual_season)
        print_microseason(printer, microseason)
        manual_season += 1

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
        # For testing, you can hard-code a date: (year, month, day, weekday, hour, minute, second, millisecond)
        # RTC().datetime((2026, 11, 7, 2, 20, 31, 0, 0))
        # print(f"System time updated to {time.time()} hard-coded.")
    except:
        print("Failed to update time via NTP.")
    while True:
            if not connection:
                break # exit if no connection
            microseasons = load_microseasons()
            # list_microseasons(microseasons)
            show_time()
            season_today = get_microseason_for_date(microseasons, local_time(UTC_OFFSET)[1], local_time(UTC_OFFSET)[2])
            # print(season_today)
            if season_today is not None and local_time(UTC_OFFSET)[3] >= 9:  # Print at 9 am or later
                load_current_season()
                if season_today['number'] != load_current_season():
                    store_current_season(season_today)
                    if show_macro_season: print_macro_season(printer)
                    if show_mini_season: print_mini_season(printer)
                    print_microseason(printer, season_today)
                else:
                    print(f"Microseason {season_today['number']} already printed for today's date.")
            else:
                print("No microseason found for today's date or too early to print.")

            # Check once every hour, about the top of the hour
            print(f"Sleeping {60-local_time(UTC_OFFSET)[4]} minutes until next check.")
            time.sleep((60 * (60-local_time(UTC_OFFSET)[4]))-local_time(UTC_OFFSET)[5])  # Sleep until the top of the next hour 

main()
            
