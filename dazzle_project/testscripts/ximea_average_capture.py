import os

import numpy as np
from pathlib import Path

from matplotlib.pyplot import step
from pyvisa import ResourceManager
from time import sleep

from ximea import xiapi

from dazzle_project.instruments.pro8000 import PRO_8000
from dazzle_project.instruments.led_controller import LedController
from dazzle_project.tools.ParameterSweep import ParameterSweep

# input arguments
exposure_time = 1300 # in micro seconds ( us )
avg_sampling = 25

# folder path
kwargs = {
    "collimator": "PAF2-A4A",
    "detector": "818-UV",
    "laser": "25118553-BNT100",
    "base_folder": r"C:\Users\lab_a3\dazzle_folder", #r"C:\Users\lab_a3\dazzle_folder\dazzling",
    "item_folder": "LIV",
    "ld_current": 0.585, # 0.45
    "n_average": 10,
    "exposure_time": [140],
    "filter": None,
}
base_folder = kwargs["base_folder"]
collimator  = kwargs["collimator"]
item_folder = kwargs["item_folder"]
folder_test = os.path.join(base_folder, item_folder, collimator)
folder_test_path = Path(folder_test)

if not folder_test_path.exists():
    folder_test_path.mkdir()

#create instance for first connected camera
camera = xiapi.Camera()

#instantiate instruments
pro8000 = PRO_8000("GPIB0::10::INSTR", visa_resource_manager=ResourceManager())
channel_ld_driver = pro8000.Slot.SLOT6
tec_channel = pro8000.Slot.SLOT1

# enable laser at expected current values

pro8000.select_slot(channel_ld_driver)
#
# Apply current
#
ld_current    = kwargs["ld_current"]
if kwargs["filter"] is not None:
    filter        = kwargs["filter"]
print(f"[pro8000]: apply current {kwargs["ld_current"]} A")
pro8000.set_diode_current(kwargs["ld_current"])
sleep(1)
if ld_current == "dark":
    pro8000.set_ld_off_ch6()
else :
    pro8000.set_ld_on_ch6()

#start communication
#to open specific device, use:
#cam.open_device_by_SN('41305651')
#(open by serial number)
print('Opening first camera...')
camera.open_device()

exposure_time = kwargs["exposure_time"]

# number of sampling for each measurement
WAIT_SETTLING = 60
WAIT_MEAS = 10
n_average = kwargs["n_average"]

current_folder = os.path.join(folder_test, f"{ld_current}_A")
if not Path(current_folder).exists():
    Path(current_folder).mkdir()

#start data acquisition
print('Starting data acquisition...')
camera.start_acquisition()

for exp_t in exposure_time:

    # settings
    camera.set_exposure(exp_t)  # exposure is in us
    print('Exposure was set to %i us' % camera.get_exposure())
    temperature = camera.get_temp()
    print(f"temperature : {temperature} degC")

    #create instance of Image to store image data and metadata
    img = xiapi.Image()

    frames = []
    for i in range(n_average):
        # get image with sensor under laser fire

        camera.get_image(img)
        np_data = img.get_image_data_numpy()
        frames.append(np_data)

    frames = np.stack(frames)
    avg_frame = np.mean(frames, axis=0)

    if kwargs["filter"] is not None:
        file_name = f"dazzling_{filter}_{exp_t}_us.npy"
    else :
        file_name = f"dazzling_{exp_t}_us.npy"

    np.save(os.path.join(current_folder, file_name), avg_frame)

    sleep(0.5)


pro8000.set_ld_off_ch6()
#stop data acquisition
print('Stop data acquisition...')
camera.stop_acquisition()

camera.close_device()


