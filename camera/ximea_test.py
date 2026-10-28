from ximea import xiapi
import numpy as np
import matplotlib.pyplot as plt

from time import sleep

#create instance for first connected camera
cam = xiapi.Camera()


#start communication
#to open specific device, use:
#cam.open_device_by_SN('41305651')
#(open by serial number)
print('Opening first camera...')
cam.open_device()

#settings
cam.set_exposure(1000) # exposure is in us
print('Exposure was set to %i us' %cam.get_exposure())
temperature = cam.get_temp()

#create instance of Image to store image data and metadata
img = xiapi.Image()

#GPIO test
#selector
gpi_selector = cam.get_gpi_selector()
gpi_selector_min = cam.get_gpi_selector_minimum()
gpi_selector_max = cam.get_gpi_selector_maximum()
gpi_selector_inc = cam.get_gpi_selector_increment()
# cam.set_gpi_selector(gpi_selector)
cam.get_param("gpi_selector")
#mode
gpi_mode = cam.get_gpi_mode()
gpi_mode_min = cam.get_gpi_mode_minimum()
gpi_mode_max = cam.get_gpi_mode_maximum()
gpi_mode_inc = cam.get_gpi_mode_increment()
# cam.set_gpi_mode(gpi_mode_max)
cam.set_param("gpi_mode", "XI_GPI_OFF")
sleep(0.5)
cam.get_param("gpi_mode")
# cam.set_param("gpi_mode", "XI_GPI_TRIGGER")

#source
gpi_source = cam.get_trigger_source()
gpi_source_min = cam.get_trigger_source_minimum()
gpi_source_max = cam.get_trigger_source_maximum()
gpi_source_inc = cam.get_trigger_source_increment()
# cam.set_trigger_source(gpi_source)
cam.get_param("trigger_selector")
# cam.set_param("trigger_source", "XI_TRG_EDGE_RISING")

#trigger overlap
# trigger_overlap = cam.get_trigger_overlap()
# trigger_overlap_min = cam.get_trigger_overlap_minimum()
# trigger_overlap_max = cam.get_trigger_overlap_maximum()
# trigger_overlap_inc = cam.get_trigger_overlap_increment()

# cam.set_trigger_overlap("trigger_overlap")

#level
gpi_level = cam.get_gpi_level()
gpi_level_min = cam.get_gpi_level_minimum()
gpi_level_max = cam.get_gpi_level_maximum()
gpi_level_inc = cam.get_gpi_level_increment()

cam.get_param("gpi_level")
# cam.get_param("gpi_level_at_image_exp_start")
#gpo selector
gpo_selector = cam.get_gpo_selector()
gpo_selector_min = cam.get_gpo_selector_minimum()
gpo_selector_max = cam.get_gpo_selector_maximum()
gpo_selector_inc = cam.get_gpo_selector_increment()
# cam.set_gpo_selector(gpo_selector)
cam.get_param("gpo_mode")
# cam.set_param("gpo_mode", "XI_GPO_HIGH_IMPEDANCE")

#start data acquisition
print('Starting data acquisition...')
cam.start_acquisition()

for i in range(10):
    #get data and pass them from camera to img
    cam.get_image(img)

    #get raw data from camera
    #for Python2.x function returns string
    #for Python3.x function returns bytes
    np_data = img.get_image_data_numpy()

    if i == 5:
        plt.imshow(np_data)
        plt.show()

    temperature = cam.get_temp()

    #print image data and metadata
    print("temperature is", temperature)
    print('Image number: ' + str(i))
    print('Image width (pixels):  ' + str(img.width))
    print('Image height (pixels): ' + str(img.height))
    # print('First 10 pixels: ' + str(data[:10]))
    print('\n')


#stop data acquisition
print('Stopping acquisition...')
cam.stop_acquisition()

name_file = "background_pixel_destruction_after_setup_pinhole_at_camera.npy"

np.save(r"C:\Users\rmmestre\dazzle_project\ximea_capture" + "\\"+ name_file, np_data)
# np_data.astype(np.uint16).tofile("bakcground_ximea.bin")

print("test")

#stop communication
cam.close_device()

