import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

# def capture_average_frame(camera, avg_sampling : int):
#     # get data and pass them from camera to img
#     frames = []
#     for i in range(avg_samping):
#         camera.get_image(img)
#         np_data = img.get_image_data_numpy()
#         frames.append(np_data)


def compare_arrays(array1, array2=None, array3=None, array4=None,
                   title1="Array 1",
                   title2="Array 2",
                   title3="Array 3",
                   title4="Array 4",
                   cmap="gray"):
    """
    Display three 2D arrays side by side.
    """

    fig, axes = plt.subplots(1, 4, figsize=(18, 5))

    im1 = axes[0].imshow(array1, cmap=cmap)
    axes[0].set_title(title1)
    axes[0].axis("off")
    plt.colorbar(im1, ax=axes[0])

    if array2 is not None:
        im2 = axes[1].imshow(array2, cmap=cmap)
        axes[1].set_title(title2)
        axes[1].axis("off")
        plt.colorbar(im2, ax=axes[1])

    if array3 is not None:
        im3 = axes[2].imshow(array3, cmap=cmap)
        axes[2].set_title(title3)
        axes[2].axis("off")
        plt.colorbar(im3, ax=axes[2])

    if array4 is not None:
        im4 = axes[3].imshow(array4, cmap=cmap)
        axes[3].set_title(title4)
        axes[3].axis("off")
        plt.colorbar(im4, ax=axes[3])

    plt.show()


def create_flat_correction_image(bright_frame_path, dark_frame_path, roi=None):

    bright_frame_array = np.load(bright_frame_path)
    dark_frame_array = np.load(dark_frame_path)

    corrected_frame = np.zeros_like(bright_frame_array)
    corrected_frame = bright_frame_array - dark_frame_array

    return corrected_frame

def correct_frames(root_folder):
    """
    Find all bright/dark frame pairs and save corrected frames.

    Expected filenames:
        illuminate_after_laser_0.25s.npy
        dark_after_laser_0.25s.npy

    Output:
        corrected_after_laser_0.25s.npy
    """

    root_folder = Path(root_folder)

    for bright_file in root_folder.rglob("illuminate_after_laser_*.npy"):

        # Extract exposure part (e.g. "0.25s")
        exposure = bright_file.stem.replace("illuminate_after_laser_", "")

        dark_file = bright_file.with_name(
            f"dark_after_laser_{exposure}.npy"
        )

        if not dark_file.exists():
            print(f"Missing dark frame: {dark_file}")
            continue

        try:
            bright = np.load(bright_file)
            dark = np.load(dark_file)

            corrected = bright - dark

            output_file = bright_file.with_name(
                f"corrected_after_laser_{exposure}.npy"
            )

            np.save(output_file, corrected)

            print(f"Saved: {output_file}")

        except Exception as e:
            print(f"Error processing {bright_file}: {e}")

import numpy as np


def compute_damage_mask(after_laser_corrected,
                        reference_corrected,
                        threshold=0.1):
    """
    Compute damaged pixels from flat-field correction.

    Parameters
    ----------
    after_laser_corrected : np.ndarray
        Dark-corrected frame after laser exposure.

    reference_corrected : np.ndarray
        Dark-corrected reference frame.

    threshold : float
        Relative responsivity change threshold.
        Default = 0.1 (10%).

    Returns
    -------
    np.ndarray
        Boolean array. True indicates a damaged pixel.
    """

    # Avoid division by zero
    valid_pixels = reference_corrected > 0

    ratio = np.ones_like(reference_corrected, dtype=float)

    ratio[valid_pixels] = (
        after_laser_corrected[valid_pixels]
        / reference_corrected[valid_pixels]
    )
    # ratio = after_laser_corrected - reference_corrected

    print(f"average normal : {np.mean( np.abs(ratio - 1.0))}")
    print(f"min normal : {np.min(np.abs(ratio - 1.0))}")
    print(f"max normal : {np.max(np.abs(ratio - 1.0))}")

    damage_mask = np.abs(ratio - 1.0)  > threshold

    return damage_mask, ratio #ratio



if __name__ == "__main__":

    correct_frames_to_do = False
    damage_mask_to_do = True

    lidt_path = r"C:\Users\lab_a3\dazzle_folder\LIDT\LIDT_POF"
    collimator = "PAF2-A4A"
    ROI_folder = "ROI2"
    laser_exposure_folder = "300_s"
    reference_path = os.path.join(lidt_path, collimator, f"reference_{ROI_folder}")
    illum_path     = os.path.join(lidt_path, collimator, ROI_folder, laser_exposure_folder)

    # current driven to the laser
    laser_current = "0.585"

    file_name = fr"corrected_after_laser_exposure_{laser_current}_A.npy"

    bright_frame_path = os.path.join(reference_path, r"illuminate_reference_image.npy")
    dark_frame_path   = os.path.join(reference_path, r"dark_reference_image.npy")

    if correct_frames_to_do:
        correct_frames(reference_path)

        corrected_frame = create_flat_correction_image(bright_frame_path, dark_frame_path)

        np.save(os.path.join(os.path.dirname(bright_frame_path), "reference_corrected_image.npy"), corrected_frame)


        compare_arrays( corrected_frame, np.load(bright_frame_path), np.load(dark_frame_path), title1="corrected_frame", title2="illumination_reference",
                       title3="dark_reference", title4=None)

        # np.save(os.path.join(os.path.dirname(bright_frame_path_test), "damage_mask.npy"), damage_mask)

    # damage mask

    if damage_mask_to_do :
        after_laser_corrected = os.path.join(illum_path, file_name)

        correct_frames(illum_path)
        reference_corrected = os.path.join(reference_path, "reference_corrected_image.npy")

        after_laser_array = np.load(after_laser_corrected)
        reference_array = np.load(reference_corrected)

        damage_mask, ratio = compute_damage_mask(after_laser_corrected=after_laser_array, reference_corrected=reference_array, threshold=0.02)

        compare_arrays(after_laser_array, reference_array, ratio, damage_mask, title1="after_laser", title2="reference", title3="ratio", title4="damage_mask")

        np.save(os.path.join(illum_path, "ratio_mask_image.npy"), ratio)
        np.save(os.path.join(illum_path, "damage_mask.npy"), damage_mask)

