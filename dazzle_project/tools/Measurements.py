from dataclasses import dataclass
from typing import Callable


@dataclass
class MeasurementDefinition:
    key: str
    function: Callable
    unit: str = ""
    

class MeasurementRegistry:

    def __init__(self):
        self._measurements = {}

    def register(self, key, function, unit=""):

        self._measurements[key] = MeasurementDefinition(
            key=key,
            function=function,
            unit=unit
        )

    def get(self, key):
        return self._measurements[key]

    def available(self):
        return list(self._measurements.keys())