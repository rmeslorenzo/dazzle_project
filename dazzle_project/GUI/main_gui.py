from PyQt6 import QtWidgets
import pyvisa

from dazzle_project.instruments import get_instrument_class, INSTRUMENT_CLASSES
from dazzle_project.gui import get_instrument_gui_class, INSTRUMENT_GUI_CLASSES
from dazzle_project.communications import get_connection_type, CONNECTION_CLASSES

from dazzle_project.instruments.equipment_manager import EquipmentManager
from dazzle_project.instruments.pro8000 import PRO_8000, DummyPro8000
from dazzle_project.instruments.newport_2835_C import NEWPORT_2835_C
from dazzle_project.gui.pro8000_gui import PRO8000_GUI


class MainGUI(QtWidgets.QMainWindow):

    def __init__(self, dummy_mode = False):
        super().__init__()

        self.dummy_mode = dummy_mode
        self.visa_resource_manager = None
        self.setWindowTitle("Dazzle Instrument Control")
        self.resize(1200, 800)

        # Keep track of connected instruments
        self.manager = EquipmentManager()
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

        # interface layout with all the option for the com interface
        interface_box = QtWidgets.QGroupBox("interface parameters")
        interface_layout = QtWidgets.QVBoxLayout()

        # Connection type
        row_layout = QtWidgets.QHBoxLayout()

        row_layout.addWidget(
            QtWidgets.QLabel("Connection:")
        )

        self.connection_type = QtWidgets.QComboBox()

        self.connection_type.addItems([
            "visa",
            "serial",
        ])

        row_layout.addWidget(
            self.connection_type
        )

        interface_layout.addLayout(row_layout)

        # GPIB ID if GPIB is used
        row_layout = QtWidgets.QHBoxLayout()
        row_layout.addWidget(
            QtWidgets.QLabel("Interface (visa only): ")
        )
        self.interface_type = QtWidgets.QComboBox()

        self.interface_type.addItems([
            "GPIB",
            "USB",
        ])

        row_layout.addWidget(
            self.interface_type
        )
        interface_layout.addLayout(row_layout)

        # Bus number in case there is a GPIB interface
        row_layout = QtWidgets.QHBoxLayout()

        row_layout.addWidget(
            QtWidgets.QLabel("Bus# (GPIB only): ")
        )

        self.bus_number = QtWidgets.QSpinBox()

        self.bus_number.setMinimum(0)
        self.bus_number.setMaximum(10)
        self.bus_number.setValue(0)

        row_layout.addWidget(
            self.bus_number
        )

        interface_layout.addLayout(row_layout)

        # Baudrate for serial communications
        row_layout = QtWidgets.QHBoxLayout()
        row_layout.addWidget(
            QtWidgets.QLabel("Baud rate (Serial only): ")
        )

        self.baudrate = QtWidgets.QSpinBox()

        self.baudrate.setMinimum(300)
        self.baudrate.setMaximum(256000)
        self.baudrate.setValue(9600)

        row_layout.addWidget(
            self.baudrate
        )

        interface_layout.addLayout(row_layout)
        interface_box.setLayout(interface_layout)

        connection_layout.addWidget(interface_box)

        # Address
        connection_layout.addWidget(
            QtWidgets.QLabel("Address/Port:")
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

        self.instrument_model = QtWidgets.QComboBox()

        self.instrument_model.addItems(INSTRUMENT_CLASSES.keys())

        connection_layout.addWidget(
            self.instrument_model
        )

        # Connect
        self.connect_button = QtWidgets.QPushButton(
            "Connect"
        )
        self.autoscan_button = QtWidgets.QPushButton(
            "Auto-Scan"
        )

        self.autoscan_button.clicked.connect(
            self.auto_scan
        )

        self.connect_button.clicked.connect(
            self.connect_instrument_button
        )

        connection_layout.addWidget(
            self.connect_button
        )
        connection_layout.addWidget(
            self.autoscan_button
        )

        layout.addLayout(connection_layout)

        # Give the table the available vertical space
        layout.addStretch()

    # =====================================================
    # Connect instrument
    # =====================================================
    def auto_scan(self):
        """Automatic recognition and connection of instruments.
        """
        self.manager.scan_visa()
        for inst_info in self.manager.list_instruments():
            if inst_info.instrument_type is not None:
                self.connect_instrument(
                    inst_info.connection_type,
                    inst_info.connection_kwargs,
                    inst_info.model,
                    inst_info.instrument_class,
                    inst_info.gui_class,
                )

    def connect_instrument_button(self):

        connection_type = self.connection_type.currentText()
        interface_type = self.interface_type.currentText()
        bus_number = self.bus_number.value()
        baudrate = self.baudrate.value()
        address = self.address.value()
        instrument_model = self.instrument_model.currentText()

        # create dict with parameters
        if connection_type == "serial":
            kwargs_dict = {"port"     : f"COM{address}",
                           "baudrate" : baudrate,
                           }
        elif connection_type == "visa":
            if self.visa_resource_manager is None:
                self.visa_resource_manager = pyvisa.ResourceManager()
            if interface_type != "GPIB":
                bus_number = ""
            resource_name =  f"{interface_type}{bus_number}::{address}::INSTR"
            kwargs_dict = {"resource_name" : resource_name,
                           "visa_resource_manager" : self.visa_resource_manager,
                           "address" : address,
                           }

        instrument_class     = get_instrument_class(instrument_model)
        instrument_gui_class = get_instrument_gui_class(instrument_model)

        self.connect_instrument(connection_type, kwargs_dict, instrument_model, instrument_class, instrument_gui_class)


    def connect_instrument(self, connection_type, connection_kwargs, instrument_model, instrument_class, instrument_gui_class):

        # Extract param from kwargs
        if connection_type == "visa":
            resource_name = connection_kwargs["resource_name"]
            address = connection_kwargs["address"]

        elif connection_type == "serial":
            resource_name = "who_cares_its_serial"
            address = connection_kwargs["port"]

        else :
            raise ValueError("Invalid connection type")

        try:

            # ---------------------------------------------
            # Create instrument
            # ---------------------------------------------
            print(f"connecting to instrument {instrument_model}")

            instrument = self.create_instrument(
                resource_name,
                connection_type,
                connection_kwargs,
                instrument_model,
                instrument_class
            )

            # ---------------------------------------------
            # Create instrument gui
            # ---------------------------------------------

            instrument_gui = self.create_instrument_gui(
                instrument,
                instrument_gui_class
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
            "model": instrument_model,
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
            f"{instrument_model} "
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

    def create_instrument_gui_old(
            self,
            instrument_type,
            instrument
    ):

        if instrument_type == "PRO8000":

            return PRO8000_GUI(instrument)

        elif instrument_type == "powermeter":

            raise NotImplementedError(
                "PowerMeter gui not implemented yet."
            )

        raise ValueError(
            f"No gui available for {instrument_type}"
        )

        # =====================================================
        # Create instrument
        # =====================================================

    def create_instrument(
            self,
            resource_name,
            connection_type,
            connection_kwargs,
            instrument_model,
            instrument_class,
    ):
        connection_class = get_connection_type(str(connection_type))

        print("connection_type :", connection_type)
        print("connection_class:", connection_class)

        if connection_type == "visa":
            return instrument_class(
                resource_name=connection_kwargs["resource_name"],
                visa_resource_manager=connection_kwargs["visa_resource_manager"],
            )
        elif connection_type == "serial":
            return instrument_class(
                port=connection_kwargs["port"],
                baudrate=connection_kwargs["baudrate"],
            )

        # =====================================================
        # Create gui
        # =====================================================

    def create_instrument_gui(
            self,
            instrument,
            instrument_gui_class
    ):
        try:
            if self.dummy_mode:
                return PRO8000_GUI(instrument)
            else :
                if instrument_gui_class is None :

                    QtWidgets.QMessageBox.critical(
                        self,
                        "gui Creation Error",
                        f"Could not create Gui from gui class"
                    )
                    return

                else :
                    return instrument_gui_class(instrument, parent=self)

        except Exception as e:
            print(f"Error : {e}")

        # if instrument_type == "PRO8000":
        #
        #     return PRO8000_GUI(instrument)
        #
        # elif instrument_type == "PowerMeter":
        #
        #     raise NotImplementedError(
        #         "PowerMeter gui not implemented yet."
        #     )
        #
        # raise ValueError(
        #     f"No gui available for {instrument_type}"

    # =====================================================
    # Add instrument to table
    # =====================================================

    def add_instrument_to_table(self, instrument_info):

        row = self.instrument_table.rowCount()

        self.instrument_table.insertRow(row)

        values = [
            instrument_info["model"],
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
        # Stop / close gui
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

    window = MainGUI(dummy_mode=False)
    window.show()

    sys.exit(app.exec())
