from pyvisa.errors import VisaIOError

from enum import Enum, StrEnum

from dazzle_project.instruments.equipment import Equipment



class NEWPORT_2936_R(Equipment):

    class MODE(Enum):
        DCCONTINUE    = 0
        DCSINGLE      = 1
        INTEGRATION   = 2
        PPCONTINUE    = 3
        PPSINGLE      = 4
        PULSECONTINUE = 5
        PULSESINGLE   = 6
        RMS           = 7

    class UNITS(Enum):
        AMPS       = 0
        VOLTS      = 1
        WATTS      = 2
        WATTS_CM2  = 3
        JOULES     = 4
        JOULES_CM2 = 5
        dBm        = 6

    class Channel(Enum):
        """Enumerator for Channel Selection."""
        ChannelA = 0
        ChannelB = 1

    class Range(Enum):
        """Enumerator for Range Mode."""
        Manual = 0
        Auto = 1

    def __init__(self, resource_name, serial_number=None):
        super().__init__(resource_name, serial_number)
        self.current_channel=None

    def select_channel(self, channel : Channel):
        print("selecting channel", )
        self.write("PM:CHAN {}".format(channel.value))
        self.current_channel = self.Channel(channel)

    def get_channel(self):
        result = self.query("PM:CHAN?")
        return result

    # ------------
    #   DETECTOR
    # ------------
    def get_detector(self):
        result = self.query("PM:DETMODEL?")
        return result

    # ------------
    #   MEASURE
    # ------------
    def get_units(self):
        out = self.query("PM:UNITS?")
        return self.UNITS(out)

    def set_units(self, unit_val : UNITS):
        self.write(f"PM:UNITS {unit_val.value}")
        print("Units set to ", str(unit_val.name))

    def set_mode(self, mode : MODE):
        self.write(f"PM:MODE {mode.value}")
        print("Mode set to ", str(mode.name))

    def get_mode(self):
        out = self.query("PM:MODE?")
        return self.MODE(out)

    def get_wavelength(self):
        wavelength = self.query("PM:Lambda?")
        return wavelength

    def set_wavelength(self, value : int):
        self.write("PM:Lambda {}".format(value))

    def get_auto_range(self):
        result = self.query("PM:AUTO?")
        return result

    def set_auto_range(self, range_val : Range):
        """Set automatic range."""
        self.write("PM:AUTO {}".format(range_val.value))

    def read_dectector_power(self):
        """Returns the Actual Power Measurement in Watts."""
        return float(self.query("PM:DPower?"))

    def read_power(self):
        return float(self.query("PM:P?"))

if __name__ == "__main__" :
    from ctypes import cdll

    # library_name = ""
    try :
        pm = cdll.LoadLibrary(r"C:\Program Files\Newport\Newport Power Meter Application\Samples\PowerMeterLib.dll")
        print("Loaded OK")
    except Exception as e:
        print(e)

    # powermeter = NEWPORT_2936_R("GPIB0::6::INSTR")


    print("test")