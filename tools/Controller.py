from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class ControlDefinition:
    key: str
    function: Callable[[Any], None]

class ParameterController:

    def __init__(self):
        self._controls = {}

    def register(self, key: str, function: Callable):
        self._controls[key] = ControlDefinition(
            key=key,
            function=function
        )

    def apply(self, key: str, value):

        control = self._controls[key]

        control.function(value)

        return {
            "key": key,
            "value": value,
            "success": True
        }