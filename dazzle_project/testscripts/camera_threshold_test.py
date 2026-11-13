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

# instruments
ld_ctrl = LedController(port='COM3')
ld_ctrl.output_off()

# input arguments
exposure_time = 1300 # in micro seconds ( us )
avg_sampling = 25


laser_illumination_time = [10] # in seconds
laser_current = 0.585

start_current = laser_current
stop_current = laser_current
npoints = 1

# folder path
LIDT_folder = r"C:\Users\lab_a3\dazzle_folder\LIDT\LIDT_POF"
collimator  = "PAF2-A4A"
ROI_folder  = "ROI2"
folder_test = os.path.join(LIDT_folder, collimator, ROI_folder)

current_sweep = ParameterSweep({
    "current": (start_current, stop_current, npoints),
})

kwargs = {
    "input_trigger"    : "XI_GPI_OFF",
    "trigger_source"   : "XI_TRG_OFF", #"XI_TRG_EDGE_RISING"
    # "trigger_selector" : "XI_GPO_FRAME_ACTIVE", #"XI_TRG_SEL_FRAME_START", "XI_TRG_SEL_EXPOSURE_ACTIVE"
    "output_trigger"   : "XI_GPO_OFF", # "XI_GPO_FRAME_ACTIVE"
}

#create instance for first connected camera
camera = xiapi.Camera()

#instantiate instruments
pro8000 = PRO_8000("GPIB0::10::INSTR", visa_resource_manager=ResourceManager())
channel_ld_driver = pro8000.Slot.SLOT6
tec_channel = pro8000.Slot.SLOT1



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

# enabled laser
for ld_illum in laser_illumination_time:

    illum_folder = os.path.join(folder_test, fr"{ld_illum}_s")
    print(f"==========\nlaser exposure : {ld_illum} s\n==========")
    # if folder not exists create it
    illum_folder_path = Path(illum_folder)
    if not illum_folder_path.exists():
        illum_folder_path.mkdir()

    for sw in current_sweep:
        # disable led light before laser exposure
        sleep(0.5)
        ld_ctrl.output_off()
        print(f"[pro8000] : setting to current {sw["current"]} mA...")
        pro8000.select_slot(channel_ld_driver)
        sleep(0.5)
        pro8000.set_diode_current(sw["current"])
        sleep(0.5)
        pro8000.set_ld_on_ch6()
        # keep for the assignated laser exposure time ld_illum
        sleep(ld_illum)
        # get image with sensor under laser fire
        camera.get_image(img)
        np_data = img.get_image_data_numpy()
        np.save(os.path.join(illum_folder, f"illuminate_under_laser_{sw["current"]}_A.npy"), np_data)

        # turn off laser
        pro8000.set_ld_off_ch6()

        # measure temperature from tec
        pro8000.select_slot(tec_channel)
        laser_temp = pro8000.read_temperature(tec_channel)
        print(f"[Camera] : temperature is : {laser_temp} degC\n")

        # LED Light enable
        print("[Camera] : capturing bright frame...")
        ld_ctrl.enable_white()

        sleep(0.5)

        # YOU NEED TO STOP HERE TO REMOVE THE LENS AND TAKE UNIFORM LIGHT ON THE SENSOR
        # get data and pass them from camera to img
        frames = []
        for i in range(avg_sampling):
            camera.get_image(img)
            np_data = img.get_image_data_numpy()
            frames.append(np_data)

        frames = np.stack(frames)
        avg_frame = np.mean(frames, axis=0)

        np.save(os.path.join(illum_folder, f"illuminate_after_laser_exposure_{sw["current"]}_A.npy"), avg_frame)

        # get dark image after laser
        print("[Camera] : capturing Dark frame...")
        ld_ctrl.output_off()

        sleep(0.5)

        # get data and pass them from camera to img
        frames = []
        for i in range(avg_sampling):
            camera.get_image(img)
            np_data = img.get_image_data_numpy()
            frames.append(np_data)

        frames = np.stack(frames)
        avg_frame = np.mean(frames, axis=0)

        np.save(os.path.join(illum_folder, f"dark_after_laser_exposure_{sw["current"]}_A.npy"), np_data)

#stop data acquisition
print('Stop data acquisition...')
camera.stop_acquisition()

camera.close_device()