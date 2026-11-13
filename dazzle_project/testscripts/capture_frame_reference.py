import os
from pathlib import Path
from pyvisa import ResourceManager
from time import sleep

import numpy as np

from ximea import xiapi

from dazzle_project.instruments.pro8000 import PRO_8000
from dazzle_project.instruments.led_controller import LedController

# input arguments

exposure_time = 1300
avg_samping = 25

kwargs = {
    "input_trigger"    : "XI_GPI_OFF",
    "trigger_source"   : "XI_TRG_OFF", #"XI_TRG_EDGE_RISING"
    # "trigger_selector" : "XI_GPO_FRAME_ACTIVE", #"XI_TRG_SEL_FRAME_START", "XI_TRG_SEL_EXPOSURE_ACTIVE"
    "output_trigger"   : "XI_GPO_OFF", # "XI_GPO_FRAME_ACTIVE"
    "roi_x"            : 544,
    "roi_y"            : 360,
    "x_width"          : 280,
    "y_height"         : 160,
}

LIDT_folder = r"C:\Users\lab_a3\dazzle_folder\LIDT\LIDT_POF"
collimator  = "PAF2-A4A"
folder_test = os.path.join(LIDT_folder, collimator, "reference_ROI2")

# if folder not exists create it
folder_test_path = Path(folder_test)
if not folder_test_path.exists():
    folder_test_path.mkdir()

#create instance for first connected camera
camera = xiapi.Camera()

#instantiate instruments
# pro8000 = PRO_8000("GPIB0::10::INSTR", visa_resource_manager=ResourceManager())
ld_ctrl = LedController(port='COM3')

#start communication
#to open specific device, use:
#cam.open_device_by_SN('41305651')
#(open by serial number)
print('Opening first camera...')
camera.open_device()

# settings
camera.set_exposure(exposure_time)  # exposure is in us
print('Exposure was set to %i us' % camera.get_exposure())
temperature = camera.get_temp()
print(f"temperature : {temperature} degC")


# trigger config
if "input_trigger" in kwargs:
    camera.set_param("gpi_mode", kwargs["input_trigger"])
    camera.set_param("trigger_source", "XI_TRG_EDGE_RISING")
if "trigger_source" in kwargs:
    camera.set_param("trigger_source", kwargs["trigger_source"])
if "trigger_selector" in kwargs:
    camera.set_param("trigger_selector", kwargs["trigger_selector"])
if "output_trigger" in kwargs:
    camera.set_param("gpo_mode", kwargs["output_trigger"])


#create instance of Image to store image data and metadata
img = xiapi.Image()

#start data acquisition
print('Starting data acquisition...')
camera.start_acquisition()

# capture illuminated frame
sleep(0.1)
ld_ctrl.enable_white()
sleep(1)
#get data and pass them from camera to img
print("[Camera] : Capture bright reference frame")
frames = []
for i in range(avg_samping):
    camera.get_image(img)
    np_data = img.get_image_data_numpy()
    frames.append(np_data)

frames = np.stack(frames)
avg_frame = np.mean(frames, axis=0)

np.save(folder_test + "\\" +"illuminate_reference_image.npy", avg_frame)

# capture dark frame
sleep(0.1)
ld_ctrl.output_off()
sleep(1)
print("[Camera] : Capture dark reference frame")
frames = []
for i in range(avg_samping):
    camera.get_image(img)
    np_data = img.get_image_data_numpy()
    frames.append(np_data)

frames = np.stack(frames)
avg_frame = np.mean(frames, axis=0)

np.save(folder_test + "\\" + "dark_reference_image.npy", avg_frame)

camera.stop_acquisition()

camera.close_device()


