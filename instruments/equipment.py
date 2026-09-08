from abc import ABC
import pyvisa

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

    def __init__(self, resource_name, serial_number=None , manufacturer="", visa_resource_manager=None):
        self.manufacturer = manufacturer
        self.serial_number = serial_number
        self.name = "equipment"
        self.timeout = 50000
        self.rm = visa_resource_manager or pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(resource_name, timeout=self.timeout)

        self.id = None
        self.model = None
        self.firmware = None

    def query_id(self):
        self.id = self.query("*IDN?").strip()

        fields = [x.strip() for x in self.id.split(",")]

        if len(fields) >= 1:
            self.manufacturer = fields[0]

        if len(fields) >= 2:
            self.name = fields[1]

        # if len(fields) >= 3:
        #     self.serial_number = fields[2]
        #
        # if len(fields) >= 4:
        #     self.firmware = fields[3]

        return self.id

    def write(self, command):
        return self.instrument.write(command)

    def read(self):
        return self.instrument.read()

    def query(self, command):
        return self.instrument.query(command)

    def close(self):
        self.instrument.close()
