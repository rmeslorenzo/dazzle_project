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

        self.image = None

        # =====================================================
        # Controls
        # =====================================================
        self.fit_button = QtWidgets.QPushButton("Fit Image")
        self.fit_button.clicked.connect(self.fit_image)

        self.load_button = QtWidgets.QPushButton("Load Image")
        self.load_button.clicked.connect(self.load_image)

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


        stats_layout = QtWidgets.QHBoxLayout()
        stats_layout.addWidget(self.size_label)
        stats_layout.addWidget(self.avg_label)
        stats_layout.addWidget(self.std_label)
        stats_layout.addWidget(self.min_label)
        stats_layout.addWidget(self.max_label)
        stats_layout.addWidget(self.cursor_label)
        stats_layout.addWidget(QtWidgets.QLabel("Profile:"))
        stats_layout.addWidget(self.profile_mode)

        stats_layout.addStretch()

        # =====================================================
        # Graphics Layout
        # =====================================================

        self.graphics = pg.GraphicsLayoutWidget()

        #
        # IMAGE
        #
        self.image_plot = self.graphics.addPlot(row=0, col=0)
        self.image_plot.setTitle("Image")
        self.image_plot.setAspectLocked(True)

        self.image_item = pg.ImageItem()
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


        layout = QtWidgets.QVBoxLayout(self)

        layout.addWidget(self.graphics)
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

        self.image_plot.addItem(self.v_line)
        self.image_plot.addItem(self.h_line)

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

                # When loading a .npy, you can automatically update the GUI:
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

        print("dtype =", dtype)
        print("file elements =", data.size)
        print("expected =", width * height)

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


if __name__ == "__main__":

    app = QtWidgets.QApplication([])

    widget = ImageAnalysisWidget()

    widget.resize(1200, 900)
    widget.show()

    app.exec()