from PyQt6.QtWidgets import (
QApplication,
QWidget,
QGridLayout,
QLabel,
QComboBox,
QDoubleSpinBox,
QPushButton,
QGroupBox,
QVBoxLayout,
)

import sys

from dazzle_project.instruments.equipment import DummyEquipment
from dazzle_project.GUI.instrument_gui import InstrumentWidget

class POWERMETER_GUI(InstrumentWidget):
    """Abstract class for the power meter GUI."""
    def __init__(self, instrument, mode_list : list|None = None, range_list : list|None = None):
        super().__init__(instrument)

        self.setWindowTitle("Power Meter")

        settings_group = QGroupBox("Power Meter Settings")
        settings_layout = QGridLayout()
        # Channel
        settings_layout.addWidget(QLabel("Channel"), 0, 0)
        self.channel_combo = QComboBox()
        self.channel_combo.addItems(["A", "B"])
        settings_layout.addWidget(self.channel_combo, 0, 1)

        # Measurement Mode
        settings_layout.addWidget(QLabel("Mode"), 1, 0)
        self.mode_combo = QComboBox()
        if mode_list is None :
            self.mode_combo.addItems([
                "Continuous",
                "Power",
                "Energy"
            ])
        else :
            self.mode_combo.addItems(mode_list)

        settings_layout.addWidget(self.mode_combo, 1, 1)

        # Wavelength
        settings_layout.addWidget(QLabel("Wavelength (nm)"), 2, 0)

        self.wavelength_spin = QDoubleSpinBox()
        self.wavelength_spin.setRange(200.0, 2000.0)
        self.wavelength_spin.setDecimals(1)
        self.wavelength_spin.setValue(1550.0)
        self.wavelength_spin.setSuffix(" nm")
        settings_layout.addWidget(self.wavelength_spin, 2, 1)

        # Range
        self.range_combo = QComboBox()
        if range_list is None :
            self.range_combo.addItems([
                "Auto",
                "Low",
                "Medium",
                "High"
            ])
        else :
            self.range_combo.addItems(range_list)

        settings_layout.addWidget(self.range_combo, 3, 1)

        # Units
        settings_layout.addWidget(QLabel("Units"), 4, 0)

        self.unit_combo = QComboBox()
        self.unit_combo.addItems([
            "W",
            "dBm",
            "dB",
            "J"
        ])
        settings_layout.addWidget(self.unit_combo, 4, 1)

        settings_group.setLayout(settings_layout)
        self.main_layout.addWidget(settings_group)

        # Apply button
        self.apply_button = QPushButton("Apply Settings")
        self.main_layout.addWidget(self.apply_button)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    equipment = DummyEquipment()
    window = POWERMETER_GUI(equipment)
    window.show()
    sys.exit(app.exec())