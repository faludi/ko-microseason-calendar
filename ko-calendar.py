# Kō microseasons are a traditional Japanese way of dividing the year into 72 microseasons, each lasting about five days.
# https://www.nippon.com/en/features/h00124/
# by Rob Faludi 2025

import time
import re
import json
import secrets  # separate file that contains your WiFi credentials
import network
from machine import Pin, reset, RTC
import ntptime
import gy_ep204x

version = "1.1.0"
print("Ko Microseason Calendar - Version:", version)

# Wi-Fi credentials
ssid = secrets.WIFI_SSID  # your SSID name stored in secrets.py
password = secrets.WIFI_PASSWORD  # your WiFi password stored in secrets.py

UTC_OFFSET = -5  # Adjust as needed for your timezone
USE_DST = True  # Set to True if your timezone observes Daylight Saving Time

show_macro_season = True  # Set to True to print macro seasons
show_mini_season = True  # Set to True to print mini seasons

month_names = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

LED = Pin("LED", Pin.OUT)      # digital output for status LED

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
        blink_led(1, 0.1)
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
            printer.bold(True)
            printer.print(f"{macro['en']}  {macro['kanji']}   {macro['romaji']}\n")
            printer.bold(False)
            printer.print(f"{month_names[sm-1]} {sd} - {month_names[em-1]} {ed}\n")
            printer.print('-------------------------------\n')


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
            printer.bold(True)
            printer.print(f'{mini['en']} {mini['kanji']} {mini['romaji']}\n')
            printer.bold(False)
            printer.print(f"{month_names[sm-1]} {sd} - {month_names[em-1]} {ed}\n")
            printer.print('===============================\n')

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
    printer.double_height_width()
    printer.bold(True)
    printer.print_with_breaks(f"{microseason['en']}", line_length=16)
    printer.bold(False)
    # printer.feed(1)
    printer.feed_rows(8)
    printer.feed_rows(8)
    printer.triple_height_width()
    printer.print(f'{microseason['kanji']}\n')
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

def print_header(printer):
    printer.center_justify()
    printer.set_japanese_charset()  # Set to Japanese character set
    printer.print('===============[●]=============\n')

def blink_led(times, interval=0.2):
    for _ in range(times):
        LED.on()
        time.sleep(interval)
        LED.off()
        time.sleep(interval)

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

def formatted_time(lt):
    return(f"UTC: {lt[0]:04d}-{lt[1]:02d}-{lt[2]:02d} {lt[3]:02d}:{lt[4]:02d}:{lt[5]:02d}")

def get_ntp(retries=False):
    global next_ntp_sync
    ntp_set = False
    while not ntp_set:
        try:
            print('Syncing time via NTP...')
            ntptime.settime()
            print(f"System time updated to {formatted_time(time.localtime())} via NTP.")
            next_ntp_sync = time.time() + 43200 # update every 12 hours
            ntp_set = True
        except Exception as e:
            print("Failed to update time via NTP.", e)
            if retries:
                print('Retrying in 5 seconds...')
                time.sleep(5)
                ntp_set = False
            else:
                next_ntp_sync = time.time() + 600  # try again in 10 minutes
                print("Trying again in 10 minutes.")


def check_button():
    if button.value() == 0:
        # print current microseason
        print('Button pressed')
        blink_led(1, 0.1)
        manual_season = load_current_season()
        microseason = get_microseason_for_number(microseasons, manual_season)
        print_header(printer)
        print_microseason(printer, microseason)
        time.sleep(1.5)
        while button.value() == 0:
            # print additional microseasons while button held down
            manual_season += 1
            if manual_season > 72:
                    manual_season = 1
            microseason = get_microseason_for_number(microseasons, manual_season)
            print_header(printer)
            print_microseason(printer, microseason)
            time.sleep(1.5)
            

button = Pin(6, Pin.IN, Pin.PULL_UP)

next_ntp_sync = 0

def main():
    global microseasons, printer, next_ntp_sync
    connection = False
    connection_timeout = 10
    blink_led(3, 0.1)
    printer = setup_printer()
    while not connection:
            connection = connect_to_wifi()
            connection_timeout -= 1
            if connection_timeout == 0:
                print('Could not connect to Wi-Fi, exiting')
                reset()
    get_ntp(retries=True)
    while True:
            blink_led(2, 0.1)
            if not connection:
                break # exit if no connection
            microseasons = load_microseasons()
            # list_microseasons(microseasons)
            show_time()
            if time.time() >= next_ntp_sync:
                get_ntp(retries=False)
            # Set time manually to test microseason printing:
            # RTC().datetime((2025, 5, 5, 1, 13, 0, 0, 0))   # year, month, day, weekday, hour, minute, second, subseconds
            show_time()
            season_today = get_microseason_for_date(microseasons, local_time(UTC_OFFSET)[1], local_time(UTC_OFFSET)[2])
            # print(season_today)
            if season_today is not None and local_time(UTC_OFFSET)[3] >= 9:  # Print at 9 am or later
                load_current_season()
                if season_today['number'] != load_current_season():
                    store_current_season(season_today)
                    print_header(printer)
                    if show_macro_season: print_macro_season(printer)
                    if show_mini_season: print_mini_season(printer)
                    print_microseason(printer, season_today)
                else:
                    print(f"Microseason {season_today['number']} already printed for today's date.")
            else:
                print("No microseason found for today's date or too early to print.")
            # Check once every hour, about the top of the hour
            print(f"Sleeping {60-local_time(UTC_OFFSET)[4]} minutes until next check.")
            sleep_time = (60 * (60-local_time(UTC_OFFSET)[4]))-local_time(UTC_OFFSET)[5]  # Sleep until the top of the next hour 
            start_time = time.time()
            while (time.time() - start_time) < sleep_time:
                check_button()
                time.sleep(0.1)

main()
            
