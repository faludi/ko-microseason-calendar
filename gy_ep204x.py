import time
from machine import Pin, UART

version = "1.0.3"
class GY_EP204X:
    def __init__(self, baudrate=115200, tx_pin=4, rx_pin=5):
        self.uart = UART(1, baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin))
        self.uart.init(bits=8, parity=None, stop=1)

    def send_command(self, command: str):
        # Send a command string to the printer.
        self.uart.write(bytes(command, "ascii"))

    def print(self, text):
        # Code to send text to the printer
        self.uart.write(text.encode('utf-8'))

    def print_with_breaks(self, text, line_length=32):
        # Print text broken at spaces to fit within line_length
        words = text.split(' ')
        current_line = ''
        for word in words:
            if len(current_line) + len(word) + 1 <= line_length:
                if current_line:
                    current_line += ' '
                current_line += word
            else:
                self.print(current_line + '\n')
                current_line = word
        if current_line:
            self.print(current_line + '\n')

    def _set_timeout(self, period_s: float) -> None:
        # Set a timeout before future commands can be sent.
        self._resume = time.ticks_ms() + period_s * 1000

    def feed(self, lines: int):
        """Advance paper by specified number of blank lines."""
        assert 0 <= lines <= 255
        self.send_command(f"\x1Bd{chr(lines)}")
        time.sleep(lines * 0.05)

    def feed_rows(self, rows: int):
        """Advance paper by specified number of pixel rows."""
        assert 0 <= rows <= 255
        self.send_command(f"\x1BJ{chr(rows)}")
        time.sleep(rows * 0.05)

    def center_justify(self):
        self.send_command("\x1Ba\x01")

    def double_height(self):
        self.send_command("\x1D!\x01")

    def double_width(self):
        self.send_command("\x1D!\x10")

    def double_height_width(self):
        self.send_command("\x1D!\x11")
    
    def triple_height_width(self):
        self.send_command("\x1D!\x22")

    def bold(self, enable=True):
        if enable:
            self.send_command("\x1BG\x01")
        else:
            self.send_command("\x1BG\x00")

    def underline(self, enable=True):
        if enable:
            self.send_command("\x1B-\x01")
        else:
            self.send_command("\x1B-\x00")

    def left_justify(self):
        self.send_command("\x1Ba\x00")

    def right_justify(self):
        self.send_command("\x1Ba\x02")

    def highlight(self, enable=True):
        if enable:
            self.send_command("\x1DB\x01")
        else:
            self.send_command("\x1DB\x00")

    def normal_size(self):
        self.send_command("\x1D!\x00")

    def set_japanese_charset(self):
        self.send_command("\x1B9\x01")

    def reset(self):
        self.send_command("\x1B@")