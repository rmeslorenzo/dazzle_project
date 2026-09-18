from ximea import xiapi

from dazzle_project.camera.camera import Camera


class XimeaCamera(Camera):

    def __init__(self, serial_number):
        self.serial_number = serial_number
        self.cam = xiapi.Camera()

        # open device
        self.cam.open_device_by_SN(serial_number)
        print(f"ximea camera {serial_number} is connected")

    def start_acquisition(self):
        self.cam.start_acquisition()

    def stop_acquisition(self):
        self.cam.stop_acquisition()

    def get_temperature(self):
        return self.cam.get_temp()

    def set_exposure_time(self, exposure_time):
        """ Set exposure time in microseconds """
        print(f"set exposure time to {exposure_time} us")
        self.cam.set_exposure(exposure_time)

    def get_image_numpy(self):
        # create instance of Image to store image data and metadata
        img = xiapi.Image()

        self.start_acquisition()
        self.cam.get_image(img)

        np_data = img.get_image_data_numpy()

        self.stop_acquisition()

        return np_data
