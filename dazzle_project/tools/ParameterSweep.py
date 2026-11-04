from itertools import product
import numpy as np


class ParameterSweep:
    def __init__(self, parameters):
        """
        parameters can contain either:
          - an explicit list of values
          - a tuple: (start, stop, num_points)

        Example:
            {
                "learning_rate": (0.001, 0.01, 5),
                "batch_size": [16, 32, 64],
                "dropout": (0.0, 0.5, 6),
            }
        """
        self.parameters = {
            name: self._make_values(values)
            for name, values in parameters.items()
        }

    @staticmethod
    def _make_values(values):
        # Explicit values
        if isinstance(values, list):
            return values

        # (start, stop, num_points)
        if isinstance(values, tuple) and len(values) == 3:
            start, stop, num_points = values

            if num_points < 1:
                raise ValueError("num_points must be >= 1")

            if start > stop:
                raise ValueError("stop value must superior than start")

            return np.linspace(start, stop, num_points).tolist()

        raise ValueError(
            "Parameter must be a list or a (start, stop, num_points) tuple"
        )

    def __iter__(self):
        names = list(self.parameters.keys())
        values = list(self.parameters.values())

        for testcase_number, combination in enumerate(product(*values), start=1):
            params = dict(zip(names, combination))
            params["testcase"] = testcase_number
            yield params

    def __len__(self):
        result = 1
        for values in self.parameters.values():
            result *= len(values)
        return result

if __name__ == "__main__":
    # Example
    sweep = ParameterSweep({
        "current": (0.001, 0.01, 5),
        "temperature_meas": [16, 32],
        "power_meas": (0.0, 0.5, 3),
    })

    for params in sweep:
        print(params)