from dataclasses import dataclass
from typing import Dict, List, Optional
import pyvisa


@dataclass
class InstrumentInfo:
    resource_name: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    firmware: Optional[str] = None
    identification: Optional[str] = None
    instrument_type: Optional[str] = None


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

                if len(parts) >= 4:
                    info.manufacturer = parts[0]
                    info.model = parts[1]
                    info.serial_number = parts[2]
                    info.firmware = parts[3]

                info.instrument_type = self._guess_type(
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
    ) -> str:

        text = f"{manufacturer or ''} {model or ''}".lower()

        keywords = {
            "oscilloscope": [
                "dso", "mso", "scope", "oscilloscope"
            ],
            "multimeter": [
                "dmm", "344", "multimeter"
            ],
            "power supply": [
                "e36", "n57", "supply", "psu"
            ],
            "function generator": [
                "awg", "afg", "generator"
            ],
            "spectrum analyzer": [
                "spectrum", "analyzer", "fsv", "n90"
            ],
            "network analyzer": [
                "vna", "network analyzer", "e507", "znb"
            ]
        }

        for instrument_type, words in keywords.items():
            if any(word in text for word in words):
                return instrument_type

        return "unknown"

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
            print(f"Manufacturer  : {inst.manufacturer}")
            print(f"Model         : {inst.model}")
            print(f"Serial        : {inst.serial_number}")
            print(f"Firmware      : {inst.firmware}")
            print(f"Type          : {inst.instrument_type}")
            print(f"Identification: {inst.identification}")

    finally:
        manager.close()