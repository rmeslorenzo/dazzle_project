from enum import Enum
import serial
import time


class Led(Enum):
    GREEN = "g"
    BLUE = "b"
    RED = "r"
    WHITE = "w"


class LED_CONTROLLER:
    """Controls the LED lamp through a serial connection."""
    def __init__(self, port="COM3", baudrate=9600, timeout=1):
        """
               Open the serial connection to the LED controller.

               Args:
                   port: Serial port (e.g. 'COM3' on Windows,
                         '/dev/ttyUSB0' on Linux).
                   baudrate: Serial communication speed.
                   timeout: Read timeout in seconds.
               """
        self._ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout
        )

        # Arduino may reset when the serial port is opened
        time.sleep(2)

        self._current_led = None

    def _send(self, command: str):
        self._ser.write(command.encode("ascii"))

    def enable(self, led: Led):
        """
        Enable exactly one LED.
        If another LED is active, turn it off first.
        """
        if self._current_led == led:
            return

        self.output_off()
        self._send(led.value)
        self._current_led = led

    def enable_green(self):
        """
        Enable the green LED.

        Any previously enabled LED will be turned off.
        """
        self.enable(Led.GREEN)

    def enable_blue(self):
        """
        Enable the blue LED.

        Any previously enabled LED will be turned off.
        """
        self.enable(Led.BLUE)

    def enable_red(self):
        """
        Enable the red LED.

        Any previously enabled LED will be turned off.
        """
        self.enable(Led.RED)

    def enable_white(self):
        """
        Enable the white LED.

        Any previously enabled LED will be turned off.
        """
        self.enable(Led.WHITE)

    def output_off(self):
        """
        Disable all LEDs.
        """
        self._send("o")
        self._current_led = None

    def close(self):
        self.output_off()
        self._ser.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()