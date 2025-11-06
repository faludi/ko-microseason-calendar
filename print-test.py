import time
from machine import Pin, UART
import gy_ep204x

printer = gy_ep204x.GY_EP204X()
printer.reset()

printer.send_command(f"\x1B9{chr(1)}")  # Set to Japanese character set

printer.center_justify()
# printer.print('================================\n')
printer.print('/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\\n')
# printer.print('===============[●]=============\n')
printer.double_height_width()
printer.bold(True)
printer.print_with_breaks("Parsley flourishes", line_length=16)
printer.bold(False)
printer.feed(1)
printer.triple_height_width()
printer.print("芹乃栄\n")
printer.normal_size()
printer.feed(1)
printer.print_with_breaks("Seri sunawachi sakau", line_length=32)
printer.normal_size()
printer.feed_rows(6)
printer.bold(True)
printer.print(f"Jan 05 - Jan 10\n")
printer.bold(False)
printer.print('________________________________\n')
printer.print('Lesser cold  小寒  Shōkan\n')
printer.print("Winter  冬  Fuyu\n")
printer.print('================================\n')
# printer.print('\n')



# printer.send_command(f"\x1B7\x0B\x78")  # send heating information
# printer.print('Hello World!\n')


# printer.center_justify()
# printer.double_height_width()
# printer.bold(True)
# printer.print_with_breaks("Fish rise up and ice begins to melt\n",16)
# printer.print_with_breaks("Rotting grass turns into fireflies\n",16)
# printer.print_with_breaks("Heaven and earth grow solemn\n",16)
# printer.print_with_breaks("Everything closes up for winter\n",16)
# printer.print_with_breaks("Rainbows hide\n",32)



# uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
# uart.init(bits=8, parity=None, stop=1)




# uart.write(' __| |____________________| |__\n')
# uart.write('(__   ____________________   __)\n')
# uart.write('   | |                    | |\n')
# uart.write('   | |                    | |\n')
# uart.write('   | |                    | |\n')
# uart.write('   | |                    | |\n')
# uart.write('   | |                    | |\n')
# uart.write('   | |                    | |\n')
# uart.write(' __| |____________________| |__\n')
# uart.write('(__   ____________________   __)\n')
# uart.write('   | |                    | |\n')

# ThermalPrinter = adafruit_thermal_printer.get_printer_class(2.69)

# printer = ThermalPrinter(uart, auto_warm_up=False)

# printer.reset()

# printer.send_command(f"\x1B9{chr(1)}")
# printer.print('こんにちは世界！')
# printer.print('Hello Kō')


# printer.send_command(f"\x1B9{chr(charset)}")
# printer.print('こんにちは世界！')
# printer.warm_up()

# printer.justify = adafruit_thermal_printer.JUSTIFY_CENTER
# printer.print('--------------------------------')
# printer.print("10-28 to 11-03")
# printer.print("\n10-28 to 11-03")
# printer.size = adafruit_thermal_printer.SIZE_LARGE
# printer.print('小雨時々降\n\n')
# printer.print('Light rains fall')
# printer.size = adafruit_thermal_printer.SIZE_SMALL
# printer.print('--------------------------------')

# uart.write(bytes(f"\x1B9{chr(1)}", "ascii")) # Set to Japanese character set
# uart.write(bytes("\x1Ba\x01", "ascii")) # Center justification
# uart.write('--------------------------------')
# uart.write(bytes("\x1D!\x11", "ascii")) # Double height and width
# uart.write('小雨時々降\n')
# uart.write(bytes("\x1D!\x00", "ascii")) # Back to normal size
# uart.write('Kosame tokidoki furu\nLight rains fall\n10-28 to 11-03\n')
# uart.write('--------------------------------')
# uart.write('\n')
# time.sleep(15)
# uart.write('--------------------------------')
# uart.write('楓蔦黄 \nMomiji tsuta kibamu\nMaple and ivy turn yellow\n11-04 to 11-10\n')
# uart.write('--------------------------------')
# uart.write('\n')
# time.sleep(15)
# uart.write('--------------------------------')
# uart.write('山茶始開 \nTsubaki hajimete hiraku\nCamellias begin to bloom\n11-11 to 11-17\n')
# uart.write('--------------------------------')
# uart.write('\n')
