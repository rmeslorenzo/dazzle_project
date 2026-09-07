from pyvisa.errors import VisaIOError
from time import sleep
from enum import IntEnum, StrEnum

from dazzle_project.instruments.equipment import Equipment
from dazzle_project.instruments.pro8000 import PRO_8000



class NEWPORT_2835_R(Equipment):

    class MODE(StrEnum):
        DCSINGLE    = "DCSNGL"
        DCCONTINUE  = "DCCONT"
        INTEGRATION = "INTG"
        PPSINGLE    = "PPSNGL"
        PULSESINGLE = "SNGLPULSE"
        CONTPULSE   = "CONTPULSE"

    class Channel(IntEnum):
        """Enumerator for Channel Selection."""
        CHANNELA = 0
        CHANNELB = 1

    class Range(IntEnum):
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
    def get_detector(self):
        result = self.query("DETMODEL_n?")
        return result

    # ------------
    #   MEASURE
    # ------------
    def get_units(self):
        self.write("UNITS_n?")
        sleep(1)
        self.read()
    def set_wavelength(self, wavelength : int):
        self.write("LAMBDA_n {}".format(wavelength))
    def get_wavelength(self):
        self.query("LAMBDA_n?")
    def set_mode(self, mode : MODE):
        self.write("MODE_n {}".format(mode.value))
    def get_mode(self):
        result = self.query("MODE_n?")[:-1]
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

    def get_stat_mean(self):
        result = self.query("STMEAN_n?")
        return result

    def get_auto_range(self):
        result = self.query("AUTO_n?")
        return result

    def set_auto_range(self, range_val : Range):
        """Set automatic range."""
        self.write("AUTO_n")

    def start_channel_acquisition(self):
        self.write("RUN_n")

    def read_single_channel(self):
        self.write("R_n?")

    def stop(self):
        self.write("STOP")

    def read_power(self):
        """Returns the Actual Power Measurement in Watts."""
        self.set_size_stat(100)
        self.start_channel_acquisition()



if __name__ == "__main__" :
    import pyvisa

    rm = pyvisa.ResourceManager()
    print(rm.list_resources())

    pro8000 = PRO_8000("GPIB0::10::INSTR")
    powermeter = NEWPORT_2835_R("GPIB0::6::INSTR")


    print("test")