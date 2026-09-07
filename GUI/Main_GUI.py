from PyQt6 import QtWidgets
import pyvisa

from dazzle_project.instruments.pro8000 import PRO_8000, DummyPro8000
from dazzle_project.GUI.pro8000_GUI import PRO8000_GUI


class MainGUI(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dazzle Instrument Control")
        self.resize(1200, 800)

        # Keep track of connected instruments
        self.instruments = []

        # =================================================
        # Main tab widget
        # =================================================

        self.tabs = QtWidgets.QTabWidget()

        self.setCentralWidget(self.tabs)

        # =================================================
        # Connection tab
        # =================================================

        self.connection_widget = QtWidgets.QWidget()
        self.create_connection_widget()

        self.tabs.addTab(
            self.connection_widget,
            "Connection"
        )

    def create_connection_widget(self):
        layout = QtWidgets.QVBoxLayout(
            self.connection_widget
        )

        # =================================================
        # Connected instruments
        # =================================================

        connected_label = QtWidgets.QLabel(
            "Connected instruments"
        )
        connected_label.setStyleSheet(
            "font-weight: bold; font-size: 14px;"
        )

        layout.addWidget(connected_label)

        self.instrument_table = QtWidgets.QTableWidget()

        self.instrument_table.setColumnCount(4)
        self.instrument_table.setHorizontalHeaderLabels([
            "Instrument",
            "Connection",
            "Address",
            "Status",
        ])

        self.instrument_table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.instrument_table.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
        )

        self.instrument_table.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.instrument_table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.instrument_table)

        # -------------------------------------------------
        # Disconnect
        # -------------------------------------------------
        self.disconnect_button = QtWidgets.QPushButton(
            "Disconnect selected"
        )

        self.disconnect_button.clicked.connect(
            self.disconnect_selected_instrument
        )

        layout.addWidget(self.disconnect_button)

        # =================================================
        # Connection controls
        # =================================================

        connection_label = QtWidgets.QLabel(
            "Add instrument"
        )

        connection_label.setStyleSheet(
            "font-weight: bold; font-size: 14px;"
        )

        layout.addWidget(connection_label)
        connection_layout = QtWidgets.QHBoxLayout()

        # Connection type
        connection_layout.addWidget(
            QtWidgets.QLabel("Connection:")
        )

        self.connection_type = QtWidgets.QComboBox()

        self.connection_type.addItems([
            "GPIB",
            "USB",
        ])

        connection_layout.addWidget(
            self.connection_type
        )

        # Address
        connection_layout.addWidget(
            QtWidgets.QLabel("Address:")
        )

        self.address = QtWidgets.QSpinBox()

        self.address.setMinimum(0)
        self.address.setMaximum(30)
        self.address.setValue(10)

        connection_layout.addWidget(
            self.address
        )

        # Instrument
        connection_layout.addWidget(
            QtWidgets.QLabel("Instrument:")
        )

        self.instrument_type = QtWidgets.QComboBox()

        self.instrument_type.addItems([
            "PRO8000",
            "PowerMeter",
        ])

        connection_layout.addWidget(
            self.instrument_type
        )

        # Connect
        self.connect_button = QtWidgets.QPushButton(
            "Connect"
        )

        self.connect_button.clicked.connect(
            self.connect_instrument
        )

        connection_layout.addWidget(
            self.connect_button
        )

        layout.addLayout(connection_layout)

        # Give the table the available vertical space
        layout.addStretch()

    # =====================================================
    # Connect instrument
    # =====================================================

    def connect_instrument(self):

        connection_type = self.connection_type.currentText()
        address = self.address.value()
        instrument_type = self.instrument_type.currentText()

        try:

            # ---------------------------------------------
            # Create instrument
            # ---------------------------------------------

            instrument = self.create_instrument(
                connection_type,
                address,
                instrument_type
            )

            # ---------------------------------------------
            # Create instrument GUI
            # ---------------------------------------------

            instrument_gui = self.create_instrument_gui(
                instrument_type,
                instrument
            )

        except Exception as e:

            QtWidgets.QMessageBox.critical(
                self,
                "Connection error",
                f"Could not connect to instrument:\n\n{e}"
            )

            return

        # ---------------------------------------------
        # Store information
        # ---------------------------------------------

        instrument_info = {
            "instrument": instrument,
            "gui": instrument_gui,
            "type": instrument_type,
            "connection": connection_type,
            "address": address,
        }

        self.instruments.append(instrument_info)

        # ---------------------------------------------
        # Add to table
        # ---------------------------------------------

        self.add_instrument_to_table(
            instrument_info
        )

        # ---------------------------------------------
        # Create tab
        # ---------------------------------------------

        tab_name = (
            f"{instrument_type} "
            f"({connection_type} {address})"
        )

        self.tabs.addTab(
            instrument_gui,
            tab_name
        )

        # Immediately show the new instrument
        self.tabs.setCurrentWidget(
            instrument_gui
        )

    # =====================================================
    # Create instrument
    # =====================================================

    def create_instrument_gui(
            self,
            instrument_type,
            instrument
    ):

        if instrument_type == "PRO8000":

            return PRO8000_GUI(instrument)

        elif instrument_type == "PowerMeter":

            raise NotImplementedError(
                "PowerMeter GUI not implemented yet."
            )

        raise ValueError(
            f"No GUI available for {instrument_type}"
        )

        # =====================================================
        # Create instrument
        # =====================================================

    def create_instrument(
            self,
            connection_type,
            address,
            instrument_type
    ):

        if instrument_type == "PRO8000":

            # Temporary during development
            return DummyPro8000()

            # Real implementation later:
            #
            # if connection_type == "GPIB":
            #     resource = f"GPIB0::{address}::INSTR"
            #     return PRO_8000(resource)

        elif instrument_type == "PowerMeter":

            raise NotImplementedError(
                "PowerMeter not implemented yet."
            )

        raise ValueError(
            f"Unknown instrument: {instrument_type}"
        )

        # =====================================================
        # Create GUI
        # =====================================================

    def create_instrument_gui(
            self,
            instrument_type,
            instrument
    ):

        if instrument_type == "PRO8000":

            return PRO8000_GUI(instrument)

        elif instrument_type == "PowerMeter":

            raise NotImplementedError(
                "PowerMeter GUI not implemented yet."
            )

        raise ValueError(
            f"No GUI available for {instrument_type}"
        )

    # =====================================================
    # Add instrument to table
    # =====================================================

    def add_instrument_to_table(self, instrument_info):

        row = self.instrument_table.rowCount()

        self.instrument_table.insertRow(row)

        values = [
            instrument_info["type"],
            instrument_info["connection"],
            str(instrument_info["address"]),
            "Connected",
        ]

        for column, value in enumerate(values):
            self.instrument_table.setItem(
                row,
                column,
                QtWidgets.QTableWidgetItem(value)
            )

    # =====================================================
    # Disconnect
    # =====================================================

    def disconnect_selected_instrument(self):

        row = self.instrument_table.currentRow()

        if row < 0:
            return

        instrument_info = self.instruments[row]

        # -------------------------------------------------
        # Stop / close GUI
        # -------------------------------------------------

        gui = instrument_info["gui"]

        if hasattr(gui, "close"):
            gui.close()

        # Remove tab
        tab_index = self.tabs.indexOf(gui)

        if tab_index >= 0:
            self.tabs.removeTab(tab_index)

        # -------------------------------------------------
        # Disconnect instrument
        # -------------------------------------------------

        instrument = instrument_info["instrument"]

        if hasattr(instrument, "disconnect"):
            instrument.disconnect()

        elif hasattr(instrument, "close"):
            instrument.close()

        # -------------------------------------------------
        # Remove from internal list
        # -------------------------------------------------

        self.instruments.pop(row)

        # -------------------------------------------------
        # Remove table row
        # -------------------------------------------------

        self.instrument_table.removeRow(row)
        # Show connection tab again
        self.tabs.setCurrentWidget(
            self.connection_widget
        )


# =========================================================
# Application
# =========================================================

if __name__ == "__main__":

    import sys

    app = QtWidgets.QApplication(sys.argv)

    window = MainGUI()
    window.show()

    sys.exit(app.exec())
