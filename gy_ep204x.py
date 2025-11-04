import time
from machine import Pin, UART

class GY_EP204X:
    def __init__(self):
        self.uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
        self.uart.init(bits=8, parity=None, stop=1)

    def send_command(self, command: str):
        # Send a command string to the printer.
        self.uart.write(bytes(command, "ascii"))

    def print(self, text):
        # Code to send text to the printer
        self.uart.write(text.encode('utf-8'))

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

    def normal_size(self):
        self.send_command("\x1D!\x00")

    def set_japanese_charset(self):
        self.send_command("\x1B9{chr(1)}")

    def reset(self):
        self.send_command("\x1B@")