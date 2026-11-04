from typing import Callable, Any
from datetime import datetime

class DataAcquisition:
    def __init__(self, measurement: Callable[[], Any]):
        self.measurement = measurement
        self.last_value = None
        self.last_timestamp = None

    def acquire(self):
        value = self.measurement()
        self.last_value = value
        self.last_timestamp = datetime.now()
        # for name, item in self.config.items():
        #     function = item["function"]
        #     params = item.get("params", {})
        #
        #     results[name] = function(**params)

        return value