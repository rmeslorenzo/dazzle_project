from abc import ABC, abstractmethod
import pyvisa, serial
from threading import Lock
from time import sleep

class DummyEquipment():

    manufacturer = "Dummy manufacturer"
    serial_number = "101"
    name = "equipment"
    instrument = "Dummy::10::Instrument"

    id = 0
    model = "dummy model"

    def query_id(self):
        return "Query ID : Dummy"

        # if len(fields) >= 3:
        #     self.serial_number = fields[2]
        #
        # if len(fields) >= 4:
        #     self.firmware = fields[3]

        return self.id

    def write(self, command: str):
        return f"command : {command} written"

    def read(self):
        return "read command : 1546546"

    def query(self, command):
        return f"query command : {command} "

    def close(self):
        return "Instrument closed"


class Equipment(ABC):

    def __init__(
        self,
        name="Equipment",
        connection=None,
        serial_number=None,
        manufacturer=""
    ):

        self.name = name
        self.connection = connection

        self.serial_number = serial_number
        self.manufacturer = manufacturer

        self.connected = True

        self.id = None
        self.model = None
        self.firmware = None

    def write(self, command):
        return self.connection.write(command)

    def read(self):
        return self.connection.read()

    def query(self, command):
        return self.connection.query(command)

    def close(self):

        self.connection.close()
        self.connected = False

    def clear(self):

        self.connection.clear()
        sleep(0.1)

    def query_id(self):

        self.id = self.query("*IDN?").strip()

        fields = [x.strip() for x in self.id.split(",")]

        if len(fields) > 0:
            self.manufacturer = fields[0]

        if len(fields) > 1:
            self.model = fields[1]

        return self.id

class SerialEquipment(Equipment):

    def __init__(
        self,
        port,
        baudrate=9600,
        timeout=1
    ):

        super().__init__()

        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

    def connect(self):

        try:

            self.instrument = serial.Serial(
                self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )

            self.connected = True

        except serial.SerialException as ex:

            print(
                f"Could not open {self.port}: {ex}"
            )