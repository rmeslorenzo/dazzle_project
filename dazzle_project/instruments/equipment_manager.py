from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import pyvisa

from dazzle_project.instruments.equipment import Equipment
from dazzle_project.instruments import get_instrument_class
from dazzle_project.gui.instrument_gui import InstrumentWidget
from dazzle_project.gui import get_instrument_gui_class

@dataclass
class InstrumentInfo:
    resource_name: str
    connection_type : Optional[str] = None
    address : Optional[int] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    firmware: Optional[str] = None
    identification: Optional[str] = None
    instrument_type: Optional[str] = None
    instrument_class: Optional[Equipment|None] = None
    gui_class : Optional[InstrumentWidget|None] = None


class EquipmentManager:
    def __init__(self, visa_backend: str = ""):
        """
        visa_backend examples:
            ""              -> default backend
            "@py"           -> pyvisa-py backend
            "C:\\windows\\system32\\visa64.dll"
        """
        self.rm = pyvisa.ResourceManager(visa_backend)
        self.instruments: Dict[str, InstrumentInfo] = {}

    def scan(self) -> Dict[str, InstrumentInfo]:
        """Discover and identify all VISA instruments."""

        self.instruments.clear()

        resources = self.rm.list_resources()

        for resource_name in resources:
            try:
                info = self._identify_resource(resource_name)
                self.instruments[resource_name] = info

            except Exception as ex:
                self.instruments[resource_name] = InstrumentInfo(
                    resource_name=resource_name,
                    identification=f"Failed to identify: {ex}"
                )

        return self.instruments

    def _identify_resource(self, resource_name: str) -> InstrumentInfo:
        """Attempt to identify a VISA resource."""

        instrument = self.rm.open_resource(resource_name)


        try:
            instrument.timeout = 2000

            # Primary identification method for SCPI instruments
            try:
                idn = instrument.query("*IDN?").strip()

                parts = [x.strip() for x in idn.split(",")]

                info = InstrumentInfo(
                    resource_name=resource_name,
                    identification=idn
                )

                # Check the address and connection type
                resource_info =  [rm for rm in resource_name.split(":") if rm.strip()]
                if "GPIB" in resource_info[0]:
                    info.connection_type = "GPIB"
                info.address = int(resource_info[1])
                if len(parts) >= 4:
                    info.manufacturer = parts[0]
                    info.model = parts[1]
                    info.serial_number = parts[2]
                    info.firmware = parts[3]

                print(f"Equipment Manager : instrument {info.model} detected")
                info.instrument_type, info.instrument_class, info.gui_class = self._guess_type(
                    info.manufacturer,
                    info.model
                )

                return info

            except Exception:
                pass

            # Fallback to VISA attributes
            try:
                resource_info = self.rm.resource_info(resource_name)

                return InstrumentInfo(
                    resource_name=resource_name,
                    manufacturer=str(resource_info.interface_type),
                    model=str(resource_info.resource_class),
                    identification="VISA resource detected",
                )

            except Exception:
                pass

            return InstrumentInfo(
                resource_name=resource_name,
                identification="Unknown VISA device"
            )

        finally:
            try:
                instrument.close()
            except Exception:
                pass

    def _guess_type(
        self,
        manufacturer: Optional[str],
        model: Optional[str]
    ) -> tuple[str, Equipment|None]:

        text = f"{manufacturer or ''} {model or ''}".lower()

        keywords = {
            # "oscilloscope": {
            #     "dso", "mso", "scope", "oscilloscope"
            # },
            "laser driver" : [
                  "PRO8000"
            ],
            "powermeter"   : [
                "2835-C"
            ],
            # "multimeter": {
            #     "dmm", "344", "multimeter"
            # },
            # "power supply": {
            #     "e36", "n57", "supply", "psu"
            # },
            # "function generator": {
            #     "awg", "afg", "generator"
            # },
            # "spectrum analyzer": {
            #     "spectrum", "analyzer", "fsv", "n90"
            # },
            # "network analyzer": {
            #     "vna", "network analyzer", "e507", "znb"
            # }
        }

        for instrument_type, instrument_list in keywords.items():
            for inst in instrument_list:
                if inst in text.upper():
                    equipment_class = get_instrument_class(inst)
                    equipment_gui = get_instrument_gui_class(inst)
                    return instrument_type, equipment_class, equipment_gui
        return "unknown", None, None

    def list_instruments(self) -> List[InstrumentInfo]:
        return list(self.instruments.values())

    def get(self, resource_name: str) -> Optional[InstrumentInfo]:
        return self.instruments.get(resource_name)

    def open(self, resource_name: str):
        """Return an open VISA handle."""
        return self.rm.open_resource(resource_name)

    def close(self):
        self.rm.close()


if __name__ == "__main__":

    manager = EquipmentManager()

    try:
        manager.scan()

        print(f"Found {len(manager.instruments)} instrument(s)\n")

        for inst in manager.list_instruments():
            print("=" * 80)
            print(f"Resource      : {inst.resource_name}")
            print(f"connection    : {inst.connection_type}")
            print(f"address       : {inst.address}")
            print(f"Manufacturer  : {inst.manufacturer}")
            print(f"Model         : {inst.model}")
            print(f"Serial        : {inst.serial_number}")
            print(f"Firmware      : {inst.firmware}")
            print(f"Type          : {inst.instrument_type}")
            print(f"Class         : {inst.instrument_class}")
            print(f"GUI           : {inst.gui_class}")
            print(f"Identification: {inst.identification}")

    finally:
        manager.close()

    print("test")