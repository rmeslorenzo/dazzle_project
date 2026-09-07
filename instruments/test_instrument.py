import pyvisa
import time

from dazzle_project.instruments.equipment import Equipment

serial_number = 10
rm = pyvisa.ResourceManager()
print(rm.list_resources())

# instrument = rm.open_resource("GPIB0::10::INSTR")
equipment = None
Instrument = None
# check IDN
for resource in rm.list_resources():
    try:
        name_list = resource.split("::")
        if name_list[1] == str(serial_number):
            instrument = rm.open_resource(resource)

    except pyvisa.VisaIOError:
        # Resource isn't accessible or doesn't support the query
        continue

# select slot in the mainframe
instrument.write(":SLOT 1") # OR SLOT6 for LD
# TEC Current Software Limit
instrument.write(":LIMT:SET 0.150")
# Set polarities
instrument.write("")
#switches on the TEC
instrument.write(":TEC ON")
time.sleep(0.5)
instrument.query(":TEC?")
# set temperature
instrument.write(":TEMP:SET 25")
# read temperature
instrument.write(":TEMP:MEAS 3")
# set laser diode software limit
instrument.write(":LIMC:SET 0.150")
# set laser diode current
instrument.write(":ILD:SET 0.1")
# Read TEC Voltage
instrument.write(":VTE:MEAS 2")

