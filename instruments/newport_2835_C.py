from pyvisa.errors import VisaIOError
from time import sleep
from enum import Enum, StrEnum

from dazzle_project.instruments.equipment import Equipment
from dazzle_project.instruments.pro8000 import PRO_8000
import ThorlabsPM100



class NEWPORT_2835_C(Equipment):

    class MODE(StrEnum):
        DCSINGLE    = "DCSNGL"
        DCCONTINUE  = "DCCONT"
        INTEGRATION = "INTG"
        PPSINGLE    = "PPSNGL"
        PULSESINGLE = "SNGLPULSE"
        CONTPULSE   = "CONTPULSE"

    class Channel(StrEnum):
        """Enumerator for Channel Selection."""
        CHANNELA = "A"
        CHANNELB = "B"

    class Range(Enum):
        """Enumerator for Range Mode."""
        MANUAL = 0
        AUTO = 1

    def __init__(self, resource_name, serial_number=None):
        super().__init__(resource_name, serial_number)
        self.current_channel=None
        self.name = "NEWPORT_2835_R"

    # ------------
    #   DETECTOR
    # ------------
    def get_detector(self, channel : Channel):
        result = self.query(f"DETMODEL_{channel.value}?")
        return result

    # ------------
    #   MEASURE
    # ------------
    def get_units(self, channel : Channel):
        self.write(f"UNITS_{channel.value}?")
        sleep(1)
        self.read()
    def set_wavelength(self, channel: Channel, wavelength : int):
        self.write("LAMBDA_{} {}".format(channel.value, wavelength))
    def get_wavelength(self, channel : Channel):
        self.query(f"LAMBDA_{channel.value}?")
    def set_mode(self, channel : Channel, mode : MODE):
        self.write("MODE_{} {}".format(channel.value, mode.value))
    def get_mode(self, channel : Channel):
        result = self.query(f"MODE_{channel.value}?")[:-1]
        return self.MODE(result)

    # ------
    # STATS
    # ------
    def set_size_stat(self, value : int):
        if not isinstance(value, int):
            raise TypeError("value must be an integer")
        if not 1 <= value <= 100:
            raise ValueError("value must be between 1 and 100")
        self.write("STSIZE_n {}".format(value))

    def get_stat_mean(self, channel : Channel):
        result = self.query(f"STMEAN_{channel.value}?")
        return result

    def get_auto_range(self, channel : Channel):
        result = self.query(f"AUTO_{channel.value}?")
        return result

    def set_auto_range(self, channel : Channel):
        """Set automatic range."""
        self.write(f"AUTO_{channel.value}")

    def start_channel_acquisition(self, channel : Channel):
        self.write(f"RUN_{channel.value}")

    def read_single_channel(self, channel : Channel):
        return float(self.query(f"R_{channel.value}?"))

    def stop(self):
        self.write("STOP")

    def read_power(self):
        """Returns the Actual Power Measurement in Watts."""
        self.set_size_stat(100)
        self.start_channel_acquisition()



if __name__ == "__main__" :
    import pyvisa
    from ThorlabsPM100 import ThorlabsPM100
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())

    print("test")
    powermeter = NEWPORT_2835_C("GPIB0::6::INSTR")
    # pm = ThorlabsPM100(inst=powermeter)
    print("test2")