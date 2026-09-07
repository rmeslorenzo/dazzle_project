from pyvisa.errors import VisaIOError

from enum import IntEnum, StrEnum

from dazzle_project.instruments.equipment import Equipment



class NEWPORT_2936_R(Equipment):

    class Channel(IntEnum):
        """Enumerator for Channel Selection."""
        ChannelA = 0
        ChannelB = 1

    class Range(IntEnum):
        """Enumerator for Range Mode."""
        Manual = 0
        Auto = 1

    def __init__(self, resource_name, serial_number=None):
        super().__init__(resource_name, serial_number)
        self.current_channel=None

    def select_channel(self, channel : int):
        print("selecting channel", )
        self.write("PM:CHAN {}".format(channel))
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
        pass
    def set_wavelength(self):
        pass
    def set_mode(self):
        pass

    def get_auto_range(self):
        result = self.query("PM:AUTO?")
        return result

    def set_auto_range(self, range_val : Range):
        """Set automatic range."""
        self.write("PM:AUTO {}".format(range_val.value))

    def read_power(self):
        """Returns the Actual Power Measurement in Watts."""
        return float(self.query("PM:DPower?"))

if __name__ == "__main__" :
    import pyvisa

    rm = pyvisa.ResourceManager()
    print(rm.list_resources())

    powermeter = NEWPORT_2936_R("GPIB0::6::INSTR")


    print("test")