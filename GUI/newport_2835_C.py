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
from PyQt6 import QtCore

import sys

from dazzle_project.instruments.equipment import DummyEquipment
from dazzle_project.gui.powermeter_gui import POWERMETER_GUI

mode_list = [
    "DCSNGL",
    "DCCONT",
    "INTG",
    "PPSNGL",
    "SNGLPULSE",
    "CONTPULSE",
]
range_list  = [
    "Auto"
]

class PowerMeterWorker(QtCore.QObject):
    pass


class NEWPORT_2835_GUI(POWERMETER_GUI):
    def __init__(self, instrument, parent=None):
        super().__init__(instrument, parent,range_list=range_list, mode_list=mode_list)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    equipment = DummyEquipment()
    window = NEWPORT_2835_GUI(equipment)
    window.show()
    sys.exit(app.exec())