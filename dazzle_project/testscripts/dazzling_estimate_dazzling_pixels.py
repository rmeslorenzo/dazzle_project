import os

import numpy as np
from pathlib import Path

from matplotlib.pyplot import step
from pyvisa import ResourceManager
from time import sleep

from ximea import xiapi

from dazzle_project.instruments.pro8000 import PRO_8000

kwargs = {
    "powermeter"    : "NEWPORT_2835_C",
    "collimator"    : "PAF2-A4A",
    "detector"      : "818-UV",
    "laser"         : "25118553-BNT100",
    "base_folder"   : r"C:\Users\lab_a3\dazzle_folder\LIV",
    "ld_current"    : 0.45,
    "n_average"     : 10,
    "exposure_time" : 100
}

# ======== instantiate instruments ========

#create instance for first connected camera
camera = xiapi.Camera()

#start communication
#to open specific device, use:
#cam.open_device_by_SN('41305651')
#(open by serial number)
print('Opening first camera...')
camera.open_device()

# settings
exposure_time = kwargs["exposure_time"]
camera.set_exposure(exposure_time)  # exposure is in us
print('Exposure was set to %i us' % camera.get_exposure())
temperature = camera.get_temp()
print(f"temperature : {temperature} degC")


# laser driver pro8000
pro8000 = PRO_8000("GPIB0::10::INSTR", visa_resource_manager=ResourceManager())
channel_ld_driver = pro8000.Slot.SLOT6
tec_channel = pro8000.Slot.SLOT1

# enable laser
ld_current = kwargs["ld_current"]
pro8000.select_slot(channel_ld_driver)
pro8000.set_diode_current(ld_current)
sleep(1)
pro8000.set_ld_on_ch6()

# number of sampling for each measurement
WAIT_SETTLING = 60
WAIT_MEAS = 10
N_MEASUREMENTS = kwargs["n_average"]

for i in range(N_MEASUREMENTS):
    pass
