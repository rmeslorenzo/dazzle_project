from ximea import xiapi
from abc import ABC, abstractmethod

class Camera():
    """Abstract class for camera class."""
    @abstractmethod
    def connect(self):
        pass
    @abstractmethod
    def disconnect(self):
        pass
    @abstractmethod
    def start_acquisition(self):
        pass
    @abstractmethod
    def stop_acquisition(self):
        pass
    @abstractmethod
    def set_exposure_time(self, exposure_time):
        pass
    @abstractmethod
    def get_temperature(self):
        pass
    @abstractmethod
    def get_image_numpy(self):
        pass
