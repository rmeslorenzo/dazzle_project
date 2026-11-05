import pyvisa
import serial

from abc import ABC, abstractmethod


class Connection(ABC):

    @abstractmethod
    def write(self, cmd):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def query(self, cmd):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def clear(self):
        pass

class VisaConnection(Connection):

    def __init__(
        self,
        resource_name,
        visa_resource_manager=None,
        address=None,
    ):

        self.resource_name = resource_name
        self.rm = visa_resource_manager or pyvisa.ResourceManager()
        self.address = address

        self.instrument = self.rm.open_resource(
            resource_name
        )

    def write(self, command):
        return self.instrument.write(command)

    def read(self):
        return self.instrument.read()

    def query(self, command):
        return self.instrument.query(command)

    def close(self):
        self.instrument.close()

    def clear(self):
        self.instrument.clear()

class SerialConnection(Connection):

    def __init__(
        self,
        port,
        baudrate=9600,
        timeout=1
    ):

        self.instrument = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout
        )

        # if the port is open we close and reopen again
        if self.instrument.is_open:
            self.clear()

    def write(self, command, encoding="ascii"):

        if isinstance(command, str):
            command = command.encode(encoding)

        self.instrument.write(command)

    def read(self, encoding="ascii"):

        return self.instrument.readline() \
            .decode(encoding) \
            .strip()

    def query(self, command,encoding="ascii"):

        self.write(command, encoding)

        return self.read()


    def close(self):

        self.instrument.close()

    def clear(self):
        self.instrument.reset_input_buffer()
        self.instrument.reset_output_buffer()