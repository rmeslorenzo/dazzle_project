# Date : 13/10/2026
# Project : TENSIS ( Technology for EuropeaN independance in Space Image Sensors )
# Author : Ricardo Mestre
# ---------------------Description ------------------------------
# Image Analyzer software to process the image acquired by our camera during LIDT (Laser Induced Damage Threshold)
# experiment.
# ImageAnalyzer will measure the laser beam diameter (1/e2) of a gaussian beam and measured the number of pixels
# that are damaged (10% deviation from normal image) or dazzled (saturated).
# The diameter will be given in mumber of pixels or um2 if the pixel sized is inputed.
# -----------------------------------------------------------------------


import cv2
import numpy as np

from PIL import Image

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen

import pyqtgraph as pg

from pathlib import Path


pg.setConfigOptions(imageAxisOrder="row-major")


class ImageAnalysisWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # ====================
        #  Profile parameter
        # ====================
        self.xc                   = None
        self.yc                   = None
        self.beam_center_marker   = None
        self.beam_contour         = None
        self.beam_radius_pixels   = None
        self.beam_diameter_pixels = None

        self.image = None

        # =====================================================
        # Controls
        # =====================================================
        self.fit_button = QtWidgets.QPushButton("Fit Image")
        self.fit_button.clicked.connect(self.fit_image)

        self.load_button = QtWidgets.QPushButton("Load Image")
        self.load_button.clicked.connect(self.load_image)

        self.measure_beam_button = QtWidgets.QPushButton("Measure Beam")
        self.measure_beam_button.clicked.connect(self.measure_beam)

        self.use_roi_checkbox = QtWidgets.QCheckBox("Use ROI")
        self.use_roi_checkbox.setChecked(False)
        self.use_roi_checkbox.toggled.connect(self.toggle_roi)

        # ==========================
        # PROFILE TYPE SELECTION
        # =========================
        self.profile_mode = QtWidgets.QComboBox()
        self.profile_mode.addItems([
            "Average",
            "Standard Deviation",
            "Minimum",
            "Maximum"
        ])
        self.profile_mode.currentIndexChanged.connect(
            self.update_display
        )

        # =====================================================
        # Statistics
        # =====================================================

        self.size_label = QtWidgets.QLabel("Size: -")
        self.avg_label = QtWidgets.QLabel("Avg: -")
        self.std_label = QtWidgets.QLabel("Std: -")
        self.min_label = QtWidgets.QLabel("Min: -")
        self.max_label = QtWidgets.QLabel("Max: -")
        self.cursor_label = QtWidgets.QLabel("X: -, Y: -, Pixel: -")

        # Profile
        self.xc_label = QtWidgets.QLabel("Xc: -")
        self.yc_label = QtWidgets.QLabel("Yc: -")
        self.radius_label = QtWidgets.QLabel("Radius: -")
        self.diameter_label = QtWidgets.QLabel("Diameter: -")


        stats_layout = QtWidgets.QHBoxLayout()
        stats_layout.addWidget(self.size_label)
        stats_layout.addWidget(self.avg_label)
        stats_layout.addWidget(self.std_label)
        stats_layout.addWidget(self.min_label)
        stats_layout.addWidget(self.max_label)
        stats_layout.addWidget(self.cursor_label)
        stats_layout.addWidget(QtWidgets.QLabel("Profile:"))
        stats_layout.addWidget(self.profile_mode)
        # Profile
        stats_layout.addWidget(self.xc_label)
        stats_layout.addWidget(self.yc_label)
        stats_layout.addWidget(self.radius_label)
        stats_layout.addWidget(self.diameter_label)

        stats_layout.addStretch()

        # =====================================================
        # Graphics Layout
        # =====================================================

        self.graphics = pg.GraphicsLayoutWidget()

        # histogram levels
        self.histogram = pg.HistogramLUTWidget()

        #
        # IMAGE
        #
        self.image_plot = self.graphics.addPlot(row=0, col=0)
        self.image_plot.setTitle("Image")
        self.image_plot.setAspectLocked(True)

        self.image_item = pg.ImageItem()
        # associate histogram with image
        self.histogram.setImageItem(self.image_item)
        self.image_plot.addItem(self.image_item)

        self.image_border = None
        #
        # ROW PROFILE (RIGHT)
        #
        self.row_plot = self.graphics.addPlot(row=0, col=1)
        self.row_plot.setTitle("Average Row")

        self.row_curve = self.row_plot.plot(
            pen=pg.mkPen('r', width=2)
        )

        #
        # COLUMN PROFILE (BOTTOM)
        #
        self.column_plot = self.graphics.addPlot(row=1, col=0)
        self.column_plot.setTitle("Average Column")

        self.column_curve = self.column_plot.plot(
            pen=pg.mkPen('b', width=2)
        )

        # Link axes

        self.row_plot.setYLink(self.image_plot)
        self.column_plot.setXLink(self.image_plot)

        # Optional grid

        self.row_plot.showGrid(x=True, y=True)
        self.column_plot.showGrid(x=True, y=True)

        # Make right plot narrower

        self.graphics.ci.layout.setColumnStretchFactor(0, 4)
        self.graphics.ci.layout.setColumnStretchFactor(1, 1)

        # =====================================================
        #                  IMAGE OPTIONS
        # =====================================================
        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(self.load_button)
        image_layout.addWidget(self.fit_button)
        image_layout.addWidget(self.measure_beam_button)
        image_layout.addWidget(self.use_roi_checkbox)

        # ----------------------------------------------
        #   Image load option for *.bin and *.npy files
        # ----------------------------------------------
        self.width_spin = QtWidgets.QSpinBox()
        self.width_spin.setRange(1, 100000)
        self.width_spin.setValue(640)

        self.height_spin = QtWidgets.QSpinBox()
        self.height_spin.setRange(1, 100000)
        self.height_spin.setValue(512)

        self.dtype_combo = QtWidgets.QComboBox()
        self.dtype_combo.addItems([
            "uint8",
            "uint16",
            "float32"
        ])

        params_layout = QtWidgets.QHBoxLayout()

        params_layout.addWidget(QtWidgets.QLabel("Width"))
        params_layout.addWidget(self.width_spin)

        params_layout.addWidget(QtWidgets.QLabel("Height"))
        params_layout.addWidget(self.height_spin)

        params_layout.addWidget(QtWidgets.QLabel("Datatype"))
        params_layout.addWidget(self.dtype_combo)

        params_layout.addStretch()

        # =====================================================
        # Main Layout
        # =====================================================

        plot_layout = QtWidgets.QHBoxLayout()
        plot_layout.addWidget(self.graphics)
        plot_layout.addWidget(self.histogram)

        layout = QtWidgets.QVBoxLayout(self)

        layout.addLayout(plot_layout)
        layout.addLayout(stats_layout)
        layout.addLayout(params_layout)
        layout.addLayout(image_layout)

        # ==================================
        #  READ PIXEL WHEN MOUSE IS POINTING
        # ==================================
        self.mouse_proxy = pg.SignalProxy(
            self.image_plot.scene().sigMouseMoved,
            rateLimit=60,
            slot=self.mouse_moved
        )

        self.v_line = pg.InfiniteLine(
            angle=90,
            movable=False,
            pen='y'
        )

        self.h_line = pg.InfiniteLine(
            angle=0,
            movable=False,
            pen='y'
        )

        self.beam_roi = pg.RectROI(
            [200, 200],
            [300, 300],
            pen=pg.mkPen('y', width=2)
        )

        self.image_plot.addItem(self.v_line)
        self.image_plot.addItem(self.h_line)
        self.image_plot.addItem(self.beam_roi)

        # Hidden by default
        self.beam_roi.hide()

    # =========================================================
    # Image Loading
    # =========================================================

    def load_image(self):

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.npy *.bin)"
        )

        if not filename:
            return

        try :

            suffix = Path(filename).suffix.lower()

            if suffix in [".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"]:

                img = Image.open(filename)

                if img.mode != "L":
                    img = img.convert("L")

                image = np.array(img)


            elif suffix == ".npy":

                image = np.load(filename)

                # When loading a .npy, you can automatically update the gui:
                rows, cols = image.shape

                self.width_spin.setValue(cols)
                self.height_spin.setValue(rows)

                dtype_name = str(image.dtype)

                index = self.dtype_combo.findText(dtype_name)

                if index >= 0:
                    self.dtype_combo.setCurrentIndex(index)

            elif suffix == ".bin":

                image = self.load_bin_file(filename)

            else :
                return

        except Exception as e:

            self.show_error(
                f"Could not load image:\n\n{str(e)}"
            )

        self.set_image(image)

        self.image_item.setImage(self.image,autoLevels=True)

        self.fit_image()

    # ================
    #  MOUSE MOVED
    #================

    def mouse_moved(self, event):

        if self.image is None:
            return

        pos = event[0]

        if not self.image_plot.sceneBoundingRect().contains(pos):
            return

        mouse_point = self.image_plot.vb.mapSceneToView(pos)

        x = int(mouse_point.x())
        y = int(mouse_point.y())

        rows, cols = self.image.shape

        if (
                0 <= x < cols and
                0 <= y < rows
        ):
            pixel_value = self.image[y, x]

            self.cursor_label.setText(
                f"X: {x}   Y: {y}   Pixel: {pixel_value:.2f}"
            )

        else : # cursor outside image

            self.cursor_label.setText(
                "Outside image"
            )

            return

        self.v_line.setPos(x)
        self.h_line.setPos(y)

    # =========================================================
    # Public Method
    # =========================================================

    def toggle_roi(self, checked):

        if checked:
            self.beam_roi.show()
        else:
            self.beam_roi.hide()

    def set_image(self, image: np.ndarray):

        self.image = image.astype(np.float64)

        self.update_display()

    def fit_image(self):
        if self.image is None:
            return

        rows, cols = self.image.shape

        self.image_plot.setRange(
            xRange=(0, cols),
            yRange=(0, rows),
            padding=0
        )

    def load_bin_file(self, filename):

        width = self.width_spin.value()
        height = self.height_spin.value()

        dtype_name = self.dtype_combo.currentText()

        dtype_map = {
            "uint8": np.uint8,
            "uint16": np.uint16,
            "float32": np.float32,
        }

        dtype = dtype_map[dtype_name]

        data = np.fromfile(
            filename,
            dtype=dtype
        )

        # print("dtype =", dtype)
        # print("file elements =", data.size)
        # print("expected =", width * height)

        expected_size = width * height
        ratio = data.size / expected_size

        if data.size != expected_size:
            raise ValueError(
                f"Expected {expected_size} pixels "
                f"but found {data.size} "
                f"(ratio = {ratio:.2f})\n\n"
                "Check width, height or datatype."
            )

        return data.reshape(height, width)

    def show_error(self, text):

        QtWidgets.QMessageBox.critical(
            self,
            "Image Loading Error",
            text
        )

    # =========================================================
    # Display Update
    # =========================================================

    def update_display(self):

        if self.image is None:
            return

        rows, cols = self.image.shape

        # disabling zoomin out outside camera size
        viewbox = self.image_plot.getViewBox()
        #
        # viewbox.setLimits(
        #     xMin=0,
        #     yMin=0,
        # )
        # hide the axis beyond image size
        self.image_plot.hideAxis('left')
        self.image_plot.hideAxis('bottom')

        viewbox.autoRange()

        #
        # create image border
        #
        if self.image_border is not None:
            self.image_plot.removeItem(self.image_border)

        self.image_border = QtWidgets.QGraphicsRectItem(
            0, 0,
            cols, rows
        )

        self.image_border.setPen(
            QPen(Qt.GlobalColor.green, 2)
        )

        self.image_plot.addItem(self.image_border)

        #
        # update profiles
        #
        mode = self.profile_mode.currentText()

        self.row_plot.setTitle(
            f"{mode} Row Profile"
        )

        self.column_plot.setTitle(
            f"{mode} Column Profile"
        )

        #
        # Statistics
        #

        avg = np.mean(self.image)
        std = np.std(self.image)
        minimum = np.min(self.image)
        maximum = np.max(self.image)

        self.size_label.setText(
            f"Size: {cols} x {rows}"
        )

        self.avg_label.setText(
            f"Avg: {avg:.2f}"
        )

        self.std_label.setText(
            f"Std: {std:.2f}"
        )

        self.min_label.setText(
            f"Min: {minimum:.2f}"
        )

        self.max_label.setText(
            f"Max: {maximum:.2f}"
        )

        #
        # Image
        #

        self.image_item.setImage(
            self.image,
            autoLevels=True
        )

        # ==========
        # Profiles
        # ==========
        row_profile, column_profile = self.calculate_profiles()

        #
        # Right plot
        # ROW profile
        #

        self.row_curve.setData(
            row_profile,
            np.arange(rows)
        )

        #
        # Bottom plot
        # COLUMN profile
        #

        self.column_curve.setData(
            np.arange(cols),
            column_profile
        )

    # ==================
    #  MANAGE PROFILES
    # ==================

    def calculate_profiles(self):

        mode = self.profile_mode.currentText()

        if mode == "Average":

            row_profile = np.mean(self.image, axis=1)
            column_profile = np.mean(self.image, axis=0)

        elif mode == "Standard Deviation":

            row_profile = np.std(self.image, axis=1)
            column_profile = np.std(self.image, axis=0)

        elif mode == "Minimum":

            row_profile = np.min(self.image, axis=1)
            column_profile = np.min(self.image, axis=0)

        elif mode == "Maximum":

            row_profile = np.max(self.image, axis=1)
            column_profile = np.max(self.image, axis=0)

        return row_profile, column_profile

    def beam_centroid(self, image):

        image = image.astype(float)

        y, x = np.indices(image.shape)

        total = image.sum()

        if total <= 0:
            return None, None

        xc = (x * image).sum() / total
        yc = (y * image).sum() / total

        print("shape =", image.shape)

        y_peak, x_peak = np.unravel_index(
            np.argmax(image),
            image.shape
        )

        print("peak =", x_peak, y_peak)
        print("centroid =", xc, yc)

        return xc, yc

    def define_profile(self, image):

        # ====================================
        #  Step 1: Initiate and reset values
        # ====================================
        if self.beam_contour is not None:
            self.image_plot.removeItem(self.beam_contour)
            self.beam_contour = None

        if self.beam_center_marker is not None:
            self.image_plot.removeItem(
                self.beam_center_marker
            )

        # ==================================
        #  Determine 1/e² threshold
        # ==================================

        # Remove background and calculate centroid
        background = np.median(image)

        image_bs = image - background
        image_bs[image_bs < 0] = 0

        print(
            image.min(),
            image.max(),
            image.sum()
        )

        print(
            image_bs.min(),
            image_bs.max(),
            image_bs.sum()
        )

        peak = image_bs.max()

        #threshold = peak * np.exp(-2)
        threshold = 0.1353 * peak

        # =============================
        #  Step 3: Create Binary Mask
        # =============================

        beam_mask = image_bs >= threshold

        masked_beam = image_bs * beam_mask

        self.xc, self.yc = self.beam_centroid(masked_beam)

        self.beam_center_marker = pg.ScatterPlotItem(
            pos=np.array([[self.xc, self.yc]]),
            symbol='+',
            size=20,
            pen=pg.mkPen('g', width=3)
        )

        self.image_plot.addItem(
            self.beam_center_marker
        )

        # ===========================================
        #  Step 4: Calculate equivalent beam radius
        # ===========================================

        beam_area_pixels = np.sum(beam_mask)

        self.beam_radius_pixels = np.sqrt(
            beam_area_pixels / np.pi
        )

        self.beam_diameter_pixels = 2 * self.beam_radius_pixels

        # print(f"xc={self.xc}, yc={self.yc}")

        contours, _ = cv2.findContours(
            beam_mask.astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Handles missing countour safely
        if len(contours) == 0:
            return False

        if peak == 0:
            return False

        contour = max(
            contours,
            key=cv2.contourArea
        )

        pts = contour.squeeze()

        x = pts[:, 0]
        y = pts[:, 1]

        if self.use_roi_checkbox.isChecked():
            roi_pos = self.beam_roi.pos()

            x = x + roi_pos.x()
            y = y + roi_pos.y()

        x = np.append(x, x[0])
        y = np.append(y, y[0])

        self.beam_contour = pg.PlotDataItem(
            x,
            y,
            pen=pg.mkPen('r', width=2)
        )

        self.image_plot.addItem(
            self.beam_contour
        )

        return True


    # Calculates beam on the image using define_profile function
    def measure_beam(self):

        if self.image is None:
            return


        if self.use_roi_checkbox.isChecked():

            # selected ROI
            roi_data = self.beam_roi.getArrayRegion(
                self.image,
                self.image_item
            )

            if roi_data is None:
                print("Invalid ROI")
                return

            print(type(roi_data))
            print(roi_data.shape if roi_data is not None else None)

            success = self.define_profile(roi_data)

            if not success:
                return

            # Correction The ROI coordinates relative to the global center
            roi_pos = self.beam_roi.pos()

            self.xc += roi_pos.x()
            self.yc += roi_pos.y()

        else:

            self.define_profile(self.image)

        self.xc_label.setText(
            f"Xc: {self.xc:.1f}"
        )

        self.yc_label.setText(
            f"Yc: {self.yc:.1f}"
        )

        self.radius_label.setText(
            f"Radius: {self.beam_radius_pixels:.1f} px"
        )

        self.diameter_label.setText(
            f"Diameter: {self.beam_diameter_pixels:.1f} px"
        )


if __name__ == "__main__":

    app = QtWidgets.QApplication([])

    widget = ImageAnalysisWidget()

    widget.resize(1200, 900)
    widget.show()

    app.exec()