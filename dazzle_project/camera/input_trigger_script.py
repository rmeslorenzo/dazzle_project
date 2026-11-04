from ximea import xiapi
import numpy as np
import matplotlib.pyplot as plt

#create instance for first connected camera
cam = xiapi.Camera()

#start communication
print('Opening first camera...')
cam.open_device()

#create instance of Image to store image data and metadata
img = xiapi.Image()

# Set input to input
cam.set_param("gpi_mode", "XI_GPI_TRIGGER")

# Select trigger to frame start
cam.set_param("trigger_selector", "XI_TRG_SEL_FRAME_START")

# trigger source to rising edgeS
cam.set_param("trigger_source", "XI_TRG_EDGE_RISING")

#start data acquisition
print('Starting data acquisition...')
cam.start_acquisition()

for i in range(10):

    # file name
    name_file = f"input_trigger_test{i}.npy"

    #get data and pass them from camera to img
    cam.get_image(img)

    #get raw data from camera and save in file
    np_data = img.get_image_data_numpy()
    np.save(r"C:\Users\rmmestre\dazzle_project\ximea_capture" + "\\" + name_file, np_data)


#stop data acquisition
print('Stopping acquisition...')
cam.stop_acquisition()






