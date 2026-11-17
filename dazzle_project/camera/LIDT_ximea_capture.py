from ximea import xiapi
import numpy as np
import matplotlib.pyplot as plt

# args
kwargs = dict()
exposure_time = 100

def capture_image_after_laser_exposure():

    #create instance for first connected camera
    camera = xiapi.Camera()

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

    #trigger config
    if "input_trigger" in kwargs:
        camera.set_param("gpi_mode", "XI_GPI_OFF")
        camera.set_param("trigger_source", "XI_TRG_EDGE_RISING")
    elif "output_trigger" in kwargs:
        camera.set_param("gpo_mode", "XI_GPO_FRAME_ACTIVE")


    print('Exposure was set to %i us' %camera.get_exposure())
    temperature = camera.get_temp()

    #create instance of Image to store image data and metadata
    img = xiapi.Image()

    #start data acquisition
    print('Starting data acquisition...')
    camera.start_acquisition()

    for i in range(1):
        #get data and pass them from camera to img
        camera.get_image(img)

        #get raw data from camera
        #for Python2.x function returns string
        #for Python3.x function returns bytes
        np_data = img.get_image_data_numpy()

    #stop data acquisition
    print('Stopping acquisition...')
    camera.stop_acquisition()

    name_file = "laser_beam_no_pinhole_just_focus_580mA.npy"

    np.save(r"C:\Users\lab_a3\dazzle_folder\LIDT\LIDT_POF" + "\\"+ name_file, np_data)
    # np_data.astype(np.uint16).tofile("bakcground_ximea.bin")

    print("test")

    #stop communication
    camera.close_device()

if __name__ == '__main__':

    capture_image_after_laser_exposure()

    print("test")
