from pyqtgraph.Qt.QtCore import Slot
from win32net import NetGetAnyDCName

from dazzle_project.instruments.equipment import Equipment
from pyvisa.errors import VisaIOError
import threading
from enum import IntEnum, StrEnum
import random
from time import sleep

class DummyPro8000:

    name = "dummy"
    instrument = "Dummy:00:Instrument"

    class Sensor(StrEnum):
        """Enumerator for temperature sensors for PRO8000."""
        AD = "AD"
        TH = "TH"

    class Polarity(StrEnum):
        """Enumerator for polarity diodes for PRO8000."""
        Cathode = "CG"
        Anode = "AG"

    class Calibration(StrEnum):
        """Enumerator for the temperature sensor calibration for PRO8000."""
        EXP = "EXP"
        SH = "SH"

    class Slot(IntEnum):
        """Enumerator for PRO8000 Slots."""
        SLOT0 = 0
        SLOT1 = 1
        SLOT2 = 2
        SLOT3 = 3
        SLOT4 = 4
        SLOT5 = 5
        SLOT6 = 6
        SLOT7 = 7
        SLOT8 = 8

    current_slot = Slot.SLOT1

    def select_slot(self, slot : Slot):
        print("{} selected".format(slot))
        self.current_slot = slot

    def set_voltage(self, voltage):
        print(f"Setting voltage to {voltage} V")

    def set_current(self, current):
        print(f"Setting current to {current} A")

    def read_temperature_slot1(self):
        return random.uniform(20,30)

    def set_temperature(self, temp):
        print("{} degC".format(temp))

    def tec_on(self):
        print("TEC On")

    def tec_off(self):
        print("TEC Off")

    def read_tec_current_slot1(self):

        return random.uniform(0.2, 0.1)

    def read_tec_voltage_slot1(self):

        return random.uniform(1.2, 1.5)

    def set_tec_software_limit(self, current):
        print("current is {} A".format(current))

    def set_sensor(self, sensor : Sensor):
        print("Sensor is ", sensor)

    def read_laser_diode_voltage_slot6(self):
        return random.uniform(1.6, 1.8)

    def read_hardware_current_limit(self):
        return 4.15

    def read_diode_current_slot6(self):
        val = random.uniform(0.4, 0.49)
        print(f"LD Current{val}")
        return val

    def set_i_share_on(self):
        print("share i on")

    def set_i_share_off(self):
        print("share i off")

    def set_p_share(self, value):

        print("{} %".format(value))

    def set_d_share(self, value):
        print("{} %".format(value))

    def set_i_share(self, value):
        print("{} %".format(value))

    def read_p_share(self):
        return 1.1

    def read_d_share(self):
        return 0.1

    def read_i_share(self):
        return 0.8

    def read_laser_polarity(self):
        return "AG"
    def read_pd_polarity(self):
        return "AG"


    # def set_mode(self, mode):
    #     print(f"Setting mode to {mode}")
    #
    # def measure_voltage(self):
    #     return 4.998
    #
    # def measure_current(self):
    #     return 0.997


class PRO_8000(Equipment):
    """Thorlabs PRO8000-4 laboratory instrument."""

    class Slot(IntEnum):
        """Enumerator for PRO8000 Slots."""
        SLOT0 = 0
        SLOT1 = 1
        SLOT2 = 2
        SLOT3 = 3
        SLOT4 = 4
        SLOT5 = 5
        SLOT6 = 6
        SLOT7 = 7
        SLOT8 = 8

    def __init__(self, resource_name, serial_number = None, current_slot = Slot.SLOT0, current_sensor : Sensor = None):
        super().__init__(resource_name, serial_number)

        self.select_slot(self.Slot.SLOT1)
        self.current_slot = current_slot
        self.current_calibration = None
        self.current_sensor = current_sensor
        self._lock = threading.Lock()
        self.name = "PRO8000"

    class Sensor(StrEnum):
        """Enumerator for temperature sensors for PRO8000."""
        AD = "AD"
        TH = "TH"

    class Polarity(StrEnum):
        """Enumerator for polarity diodes for PRO8000."""
        Cathode = "CG"
        Anode = "AG"

    class Calibration(StrEnum):
        """Enumerator for the temperature sensor calibration for PRO8000."""
        Beta = "BETA"
        SH = "SH"

    def select_slot(self, slot : Slot):
        """Select a PRO8000 slot."""
        if not 1 <= slot <= 8:
            raise ValueError("Slot must be between 1 and 8.")

        self.write(f":SLOT {slot}")
        sleep(0.2)
        self.current_slot = slot


    def get_slot(self):
        """Return the currently selected slot."""
        slot = int(self.query(":SLOT?").strip(":SLOT "))
        self.current_slot = slot
        return slot

    def get_errors(self):
        """Return the current PRO8000 system error."""
        return self.query(":SYST:ERR?").strip()

    # TEC
    def tec_on(self):
        """TEC ON."""
        self.write(":TEC ON")
    def tec_off(self):
        """TEC OFF."""
        self.write(":TEC OFF")

    def set_tec_software_limit(self, limt):
        """Set the current software limit."""
        self.write(":LIMT:SET {}".format(limt))

    def read_tec_software_limit(self):
        """Read the current software limit."""
        result = self.query(":LIMT:SET?" )
        return float(result.strip(":LIMT:SET ")[:-1])

    def read_tec_current(self, slot : Slot):
        """Read the TEC current temperature."""
        with self._lock:
            self.write(":ITE:MEAS {}".format(slot.value))
            TEC_current = self.query(":ITE:ACT?")
            return float(TEC_current.strip(":ITE:ACT "))

    def read_tec_current_slot1(self):

        if self.current_slot == self.Slot.SLOT1:
            return self.read_tec_current(self.Slot.SLOT1)
        else :
            return -1

    def read_tec_current_slot6(self):

        return self.read_tec_current(self.Slot.SLOT6)

    def read_tec_voltage(self, slot : Slot):
        """Read the TEC voltage."""
        try :
            self.write(":VTE:MEAS {}".format(slot.value))
            VTE = self.query(":VTE:ACT?" )
            return float(VTE.strip(":VTE:ACT "))
        except VisaIOError as e :
            print("VTE read failed, slot active {} ", self.current_slot)

    def read_tec_voltage_slot1(self):
        if self.current_slot == self.Slot.SLOT1:
            return self.read_tec_voltage(self.Slot.SLOT1)
        else :
            return -1

    # Temperature
    def set_temperature(self, temp : int):
        """Set the current temperature."""
        self.write(":TEMP:SET {}".format(temp))

    def read_set_temperature(self):
        """Read the set temperature."""
        result = self.query(":TEMP:SET?")
        return float(result.strip(":TEMP:SET "))

    def read_temperature(self, slot):
        """Read the temperature."""
        self.write(":TEMP:MEAS {}".format(slot.value))
        self.write(":TEMP:ACT?")
        result = self.read()
        return float(result.strip(":TEMP:ACT ")[:-1])

    def read_temperature_slot1(self):
        """Read the temperature slot 1 (TEC)."""
        if self.current_slot == self.Slot.SLOT1:
            result = self.read_temperature(self.Slot.SLOT1)
            return result
        else :
            return -1

    def read_temperature_slot6(self):
        """Read the temperature slot 1 (TEC)."""
        result = self.read_temperature(self.Slot.SLOT6)
        return result


    # Laser diode
    def set_ld_on(self):
        if self.current_slot == self.Slot.SLOT6:
            self.write(":LASER ON")

    def set_ld_off(self):
        if self.current_slot == self.Slot.SLOT6:
            self.write(":LASER OFF")

    def set_diode_current(self, ild : float):
        """Set the current diode current."""
        if self.current_slot == self.Slot.SLOT6:
            self.write(":ILD:SET {}".format(ild))

    def read_diode_current(self, slot : Slot):
        """Read the current diode current."""
        try :
            self.write(":ILD:MEAS {}".format(slot.value))
            result = float(self.query(":ILD:ACT?").strip(":ILD:ACT"))
            return result
        except VisaIOError as e :
            print("diode current read command failed", e)

    def read_diode_current_slot6(self):
        result = -1
        if self.current_slot == self.Slot.SLOT6:
            result = self.read_diode_current(self.Slot.SLOT6)
        return result

    def read_hardware_current_limit(self):
        """Read the current hardware current limit."""
        limcp = -1
        if self.current_slot == self.Slot.SLOT6:
            limcp = float(self.query(":LIMCP:ACT?").strip(":LIMCP:ACT "))
        return limcp

    def set_laser_diode_software_current_limit(self, LIMC : float):
        """Set the diode software current limit."""
        if self.current_slot == self.Slot.SLOT6:
            self.write(":LIMC:SET {}".format(LIMC))

    def read_laser_diode_software_current_limit(self):
        """Set the diode software current limit."""
        result = -1
        if self.current_slot == self.Slot.SLOT6:
            self.write(":LIMC:SET?")
            result = self.read()
        return result

    def read_laser_diode_voltage(self, slot):
        """Read the current laser diode voltage."""
        try :
            self.write(":VLD:MEAS {}".format(slot.value))
            vld = self.query(":VLD:ACT?" ).strip(":VLD:ACT ")
            return vld
        except VisaIOError as e:
            print("read Vld failed", e)

    def read_laser_diode_voltage_slot6(self):
        """Read the current laser diode voltage."""
        vld = -1
        if self.current_slot == self.Slot.SLOT6:
            self.write(":VLD:MEAS {}".format(self.Slot.SLOT6))
            vld = float(self.query(":VLD:ACT?").strip(":VLD:ACT "))
        return vld

    def set_ld_polarity(self, polarity: Polarity):
        """Set the laser polarity."""
        if self.current_slot == self.Slot.SLOT6:
            self.write(":LDPOL {}".format(polarity.value))

    def set_pd_polarity(self, polarity: Polarity):
        """Set the laser polarity."""
        if self.current_slot == self.Slot.SLOT6:
            self.write(":PDPOL {}".format(polarity.value))

    def read_laser_polarity(self):
        """Set the laser polarity."""
        try :
            if self.current_slot == self.Slot.SLOT6:
                result = self.query(":LDPOL?")
                return result.strip(":LDPOL ")[:2]
            else :
                print("Polarity read failed, channel 6 is unactive")
                return "slot6 unactive"
        except VisaIOError as e:
            print(f"Polarity read failed: {e}")

    def read_pd_polarity(self):
        """Set the laser polarity."""
        try :
            if self.current_slot == self.Slot.SLOT6:
                result = self.query(":PDPOL?")
                # print("instrument : " + result.strip(":PDPOL ")[:2])
                return result.strip(":PDPOL ")[:2]
            else :
                return "slot6 unactive"
        except VisaIOError as e:
            print(f"Polarity read failed: {e}")


    # Selecting the sensor
    def set_sensor(self, sensor : Sensor):
        """Select the temperature sensor."""
        self.write(":SENS {}".format(sensor.value))
        self.current_sensor = sensor

    def get_sensor(self):
        """Get the temperature sensor in use."""
        result = self.query(":SENS?")
        return self.Sensor(str(result.strip(":SENS ")))

    def set_resistance_sensor(self, value):
        """Set the resistance sensor."""
        self.write(":RESI:SET {}".format(value))

    def read_resistance_sensor(self, slot:Slot):
        """Measure the resistance sensor."""
        self.write(":RESI:MEAS {}".format(slot.value))
        result = self.query(":RESI:ACT?")
        return float(result.strip(":RESI:ACT "))

    def read_resistance_sensor_slot1(self):

        return self.read_resistance_sensor(self.Slot.SLOT1)

    def set_bval(self, value):
        """Set the Energy Constant Bval."""
        self.write(":CALTB:SET {}".format(value))
        self.current_calibration = self.Calibration(value)

    def set_R0(self, value):
        """Set the Nominal resistance R0."""
        self.write(":CALTR:SET {}".format(value))
        self.current_calibration = self.Calibration(value)

    def set_T0(self, value):
        """Set the Nominal resistance T0."""
        self.write(":CALTT:SET {}".format(value))
        self.current_calibration = self.Calibration(value)

    # PID

    def set_p_share(self, value: float):
        """Set the P parameter in the PID [in %]"""
        if not value < 100:
            raise ValueError("Slot must lower than 100.")
        self.write(":SHAREP:SET {}".format(value))

    def set_i_share(self, value: float):
        """Set the P parameter in the PID [in %]"""
        if not value < 100:
            raise ValueError("Slot must lower than 100.")
        # self.set_i_share_off()
        self.write(":SHAREI:SET {}".format(value))
        # self.set_i_share_on()


    def set_d_share(self, value: float):
        """Set the P parameter in the PID [in %]"""
        if not value < 100:
            raise ValueError("Slot must lower than 100.")
        self.write(":SHARED:SET {}".format(value))

    def read_p_share(self):
        try :
            with self._lock:
                print("query for pshare ", self.query(":SHAREP:SET?"))
                out = self.query(":SHAREP:SET?")
                if ":SHAREP:SET " in out:
                    result = float(out.strip(":SHAREP:SET ")[:-1])
                else :
                    result = -1
                return result
        except Exception as e:
            print(f"Read P-Share read failed: {e}")

    def read_d_share(self):
        try :
            with self._lock:
                print("query for dshare ", self.query(":SHARED:SET?"))
                sleep(0.1)
                out = self.query(":SHARED:SET?")
                if ":SHARED:SET " in out:
                    result = float(out.strip(":SHARED:SET ")[:-1])
                else:
                    result = -1
                return result
        except Exception as e:
            print(f"Read Dshare read failed: {e}")

    def read_i_share(self):
        try :
            with self._lock:
                out = self.query(":SHAREI:SET?")
                result = float(out.strip(":SHAREI:SET ")[:-1])
                return result
        except Exception as e:
            print(f"Read IShare read failed: {e}")

    def set_i_share_on(self):
        self.write(":INTEG ON")

    def set_i_share_off(self):
        self.write(":INTEG OFF")



if __name__ == "__main__" :
    import pyvisa

    rm = pyvisa.ResourceManager()
    print(rm.list_resources())

    pro8000 = PRO_8000("GPIB0::10::INSTR")

    pro8000.query_id()

    pro8000.query(":CALTR:SET?")
    pro8000.read_tec_voltage_slot1()

    print("test")
