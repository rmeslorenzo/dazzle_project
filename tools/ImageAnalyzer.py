import numpy as np
from PIL import Image

from PyQt6 import QtWidgets
import pyqtgraph as pg


pg.setConfigOptions(imageAxisOrder="row-major")


class ImageAnalysisWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.image = None

        # =====================================================
        # Controls
        # =====================================================

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
        # Main Layout
        # =====================================================

        layout = QtWidgets.QVBoxLayout(self)

        layout.addWidget(self.graphics)
        layout.addLayout(stats_layout)
        layout.addWidget(self.load_button)

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
            "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )

        if not filename:
            return

        img = Image.open(filename)

        if img.mode != "L":
            img = img.convert("L")

        image = np.array(img)

        self.set_image(image)

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

        self.v_line.setPos(x)
        self.h_line.setPos(y)

    # =========================================================
    # Public Method
    # =========================================================

    def set_image(self, image: np.ndarray):

        self.image = image.astype(np.float64)

        self.update_display()

    # =========================================================
    # Display Update
    # =========================================================

    def update_display(self):

        if self.image is None:
            return

        rows, cols = self.image.shape

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