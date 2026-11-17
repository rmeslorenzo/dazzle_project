import os
from math import sqrt, pi

import numpy as np
from pathlib import Path

from matplotlib.pyplot import step
from pyvisa import ResourceManager
from time import sleep

from ximea import xiapi

from dazzle_project.instruments.pro8000 import PRO_8000

def count_saturated_pixels(image: np.ndarray, saturation_value=None):
    """
    Count saturated pixels in a 2D image.

    Parameters
    ----------
    image : np.ndarray
        2D numpy array representing the image.
    saturation_value : int or float, optional
        Pixel value considered saturated.
        If None, the maximum value present in the image is used.

    Returns
    -------
    int
        Number of saturated pixels.
    float
        Percentage of saturated pixels.
    """
    if saturation_value is None:
        saturation_value = image.max()

    saturated_count = np.count_nonzero(image >= saturation_value)
    saturated_percentage = 100 * saturated_count / image.size

    return saturated_count, saturated_percentage


if __name__ == "__main__":

    kwargs = {
        "folder"        : r"C:\Users\lab_a3\dazzle_folder\dazzling\PAF2-A4A",
        "current"       : [0.2, 0.35, 0.45, 0.51],
        "exposure_time" : [15, 100, 1000, 3000],
    }

    folder = kwargs["folder"]

    for crt in kwargs["current"]:

        print(f"=========\n Current {crt} A \n=========")

        for exp_t in kwargs["exposure_time"]:
            print(f"exposure time: {exp_t} [us]")

            file_name = f"dazzling_{exp_t}_us.npy"
            file_path = os.path.join(folder, str(crt)+ "_A", file_name)



            image_array = np.load(file_path)

            count, percentage = count_saturated_pixels(image_array, saturation_value=255)

            d_daz = sqrt(count/pi)

            print(f"Saturated pixels: {count}")
            print(f"dazzling diamter: {d_daz} [pixels]")
            print(f"Percentage: {percentage:.3f}%\n")



