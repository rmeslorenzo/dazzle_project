import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QDoubleSpinBox, QComboBox, QGridLayout, QLabel, QWidget, \
    QPushButton


class DummyEquipment:

    def set_voltage(self, voltage):
        print(f"Setting voltage to {voltage} V")

    def set_current(self, current):
        print(f"Setting current to {current} A")

    def set_mode(self, mode):
        print(f"Setting mode to {mode}")

    def measure_voltage(self):
        return 4.998

    def measure_current(self):
        return 0.997


class MainWindow(QMainWindow):

    def __init__(self, instrument):
        super().__init__()

        self.instrument = instrument

        self.setWindowTitle("PRO-8000")
        self.resize(1000, 700)

        self.voltage_input = QDoubleSpinBox()
        self.current_input = QDoubleSpinBox()

        self.voltage_measurement = QLabel("---- V")
        self.current_measurement = QLabel("---- A")

        self.mode_combo = QComboBox()

        self.mode_combo.addItems([
            "Constant Voltage",
            "Constant Current",
            "Remote Sense",
        ])

        self.apply_button = QPushButton("Apply")
        self.measure_button = QPushButton("Measure")

        # ----------------------
        # Create layout
        # ----------------------

        # Parameters
        central_widget = QWidget()
        layout = QGridLayout()

        layout.addWidget(QLabel("Voltage:"), 0, 0)
        layout.addWidget(self.voltage_input, 0, 1)

        layout.addWidget(QLabel("Current:"), 1, 0)
        layout.addWidget(self.current_input, 1, 1)

        layout.addWidget(QLabel("Mode:"), 2, 0)
        layout.addWidget(self.mode_combo, 2, 1)

        layout.addWidget(self.apply_button, 3, 1)

        # Measurements
        layout.addWidget(QLabel("Measured voltage:"), 5, 0)
        layout.addWidget(self.voltage_measurement, 5, 1)

        layout.addWidget(QLabel("Measured current:"), 6, 0)
        layout.addWidget(self.current_measurement, 6, 1)

        layout.addWidget(self.measure_button, 7, 1)

        self.voltage_input.setRange(0, 100)
        self.voltage_input.setDecimals(3)
        self.voltage_input.setValue(5.0)

        self.current_input.setRange(0.0, 10.0)
        self.current_input.setDecimals(3)
        self.current_input.setValue(1.0)

        # Put layout into central widget
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        # -------------------------
        # Connect button
        # -------------------------

        self.apply_button.clicked.connect(self.apply_parameters)

        self.measure_button.clicked.connect(self.read_measurements)

    # ==================================================
    # Functions called by the GUI
    # ==================================================

    def apply_parameters(self):
        voltage = self.voltage_input.value()
        current = self.current_input.value()

        self.instrument.set_voltage(voltage)
        self.instrument.set_current(current)

    def read_measurements(self):

        voltage = self.instrument.measure_voltage()
        current = self.instrument.measure_current()

        self.voltage_measurement.setText(f"{voltage:.3f} V")
        self.current_measurement.setText(f"{current:.3f} A")



if __name__ == "__main__":
    app = QApplication(sys.argv)

    instrument = DummyEquipment()

    window = MainWindow(instrument)
    window.show()

    sys.exit(app.exec())