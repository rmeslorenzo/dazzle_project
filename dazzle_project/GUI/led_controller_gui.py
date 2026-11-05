"""
====================================================================
LED Controller GUI
====================================================================

Graphical user interface for the LED controller instrument.

This widget provides manual control of the red, green, blue, and
white LED channels through a simple button-based interface.

Company : ALTER
Author  : Ricardo Mestre
Date    : 2026-11-05

====================================================================
"""
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QGroupBox,
    QGridLayout,
    QApplication
)

from dazzle_project.instruments.led_controller import LedController
from dazzle_project.gui.instrument_gui import InstrumentWidget


class LedControllerGUI(InstrumentWidget):
    """
    GUI for the LED controller.

    Provides controls for enabling and disabling
    individual LED channels.
    """

    def __init__(self, instrument, parent=None):
        """
        Construct the LED controller GUI.

        Parameters
        ----------
        instrument : LedController
            Connected LED controller instance.
        parent : QWidget | None
            Parent widget.
        """
        super().__init__(instrument, parent)

        self.create_gui()
        self.set_default()

    # =====================================================
    # GUI Construction
    # =====================================================

    def create_gui(self):
        """
        Create the graphical user interface widgets.
        """

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        title = QLabel("LED Controller")
        title.setStyleSheet(
            "font-size: 16px;"
            "font-weight: bold;"
        )

        self.main_layout.addWidget(title)

        # -------------------------------------------------
        # LED Controls
        # -------------------------------------------------

        led_group = QGroupBox("LED Controls")

        led_layout = QGridLayout()

        # Red LED controls
        self.red_on_button = QPushButton("Red ON")
        # self.red_off_button = QPushButton("Red OFF")

        # Green LED controls
        self.green_on_button = QPushButton("Green ON")
        # self.green_off_button = QPushButton("Green OFF")

        # Blue LED controls
        self.blue_on_button = QPushButton("Blue ON")
        # self.blue_off_button = QPushButton("Blue OFF")

        # White LED controls
        self.white_on_button = QPushButton("White ON")
        # self.white_off_button = QPushButton("White OFF")

        led_layout.addWidget(self.red_on_button, 0, 0)
        # led_layout.addWidget(self.red_off_button, 0, 1)

        led_layout.addWidget(self.green_on_button, 1, 0)
        # led_layout.addWidget(self.green_off_button, 1, 1)

        led_layout.addWidget(self.blue_on_button, 2, 0)
        # led_layout.addWidget(self.blue_off_button, 2, 1)

        led_layout.addWidget(self.white_on_button, 3, 0)
        # led_layout.addWidget(self.white_off_button, 3, 1)

        led_group.setLayout(led_layout)

        self.main_layout.addWidget(led_group)

        # -------------------------------------------------
        # Global Controls
        # -------------------------------------------------

        self.all_off_button = QPushButton("All OFF")

        self.main_layout.addWidget(
            self.all_off_button
        )

        self.main_layout.addStretch()

        # -------------------------------------------------
        # Signal Connections
        # -------------------------------------------------

        self.red_on_button.clicked.connect(
            self.instrument.enable_red
        )

        self.green_on_button.clicked.connect(
            self.instrument.enable_green
        )

        self.blue_on_button.clicked.connect(
            self.instrument.enable_blue
        )

        self.white_on_button.clicked.connect(
            self.instrument.enable_white
        )

        self.all_off_button.clicked.connect(
            self.instrument.output_off
        )

    # =====================================================
    # Default Configuration
    # =====================================================

    def set_default(self):
        """
        Initialize the GUI to its default state.
        """
        pass

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ld_ctrl = LedController(port='COM3')
    ld_ctrl_gui = LedControllerGUI(ld_ctrl)
    ld_ctrl_gui.show()

    sys.exit(app.exec())