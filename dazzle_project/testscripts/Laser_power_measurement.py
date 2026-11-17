import datetime, os, csv, statistics

from pyvisa import ResourceManager
from time import sleep
from pathlib import Path

from dazzle_project.instruments.pro8000 import PRO_8000
from dazzle_project.instruments.newport_2835_C import NEWPORT_2835_C
from dazzle_project.tools.ParameterSweep import ParameterSweep

kwargs = {
    "powermeter"    : "NEWPORT_2835_C",
    "collimator"    : "PAF2-A4A",
    "detector"      : "818-UV",
    "laser"         : "25118553-BNT100",
    "base_folder"   : r"C:\Users\lab_a3\dazzle_folder\LIV",
    "start_current" : 0.1,
    "stop_current"  : 0.585,
    "npoints"       : 15,
}

# ======== instantiate instruments ========
# laser driver pro8000
pro8000 = PRO_8000("GPIB0::10::INSTR", visa_resource_manager=ResourceManager())
channel_ld_driver = pro8000.Slot.SLOT6
tec_channel = pro8000.Slot.SLOT1
# powermeter
powermeter = NEWPORT_2835_C("GPIB0::6::INSTR")

# set powermeter
powermeter.set_wavelength(powermeter.Channel.CHANNELB, 532)
# current sweep
sweep = ParameterSweep({
            "current": (kwargs["start_current"], kwargs["stop_current"], kwargs["npoints"]),
        })
# folder to store the data
folder_name = os.path.join(kwargs["base_folder"], kwargs["collimator"])
# if folder not exists create it
folder_test_path = Path(folder_name)
if not folder_test_path.exists():
    folder_test_path.mkdir()
# csv file to save the measurement data
filename = os.path.join(folder_name,
            f"{kwargs["laser"]}_ld_sweep_"
            f"{datetime.datetime.now():%Y%m%d_%H%M%S}.csv"
            )

# ======== create file and start measuring ========
with open(filename, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
                        "set_ld_current_A",
                        "read_current_A",
                        "temperature_avg_degC",
                        "temperature_std_degC",
                        "tec_current_avg_A",
                        "tec_current_std_A",
                        "tec_voltage_avg_A",
                        "tec_voltage_std_A",
                        "power_avg_W",
                        "power_std_W"
                    ] + list(kwargs.keys()))

    #
    # Go to LD channel
    #
    pro8000.select_slot(channel_ld_driver)
    pro8000.set_diode_current(kwargs["start_current"])
    pro8000.set_ld_on_ch6()

    # number of sampling for each measurement
    WAIT_SETTLING = 60
    WAIT_MEAS = 10
    N_MEASUREMENTS = 10

    print(f"waiting {WAIT_SETTLING} s for settling")
    sleep(WAIT_SETTLING)
    
    for sw in sweep:

        #
        # Apply current
        #
        print(f"[pro8000]: apply current {sw["current"]} A")
        pro8000.set_diode_current(sw["current"])
        read_ld_current = pro8000.read_diode_current_slot6()

        #
        # Wait for settling
        #
        sleep(WAIT_MEAS)
        model = ""
        temperatures = []
        powers = []
        tec_currents = []
        tec_voltages = []

        for i in range(N_MEASUREMENTS):
            # wait
            #
            # Read temperature
            #
            pro8000.select_slot(
                pro8000.Slot.SLOT1
            )

            temperature = (
                pro8000.read_temperature_slot1()
            )

            tec_current = (pro8000.read_tec_current_slot1())
            tec_voltage = (pro8000.read_tec_voltage_slot1())

            print(f"temperature is : {temperature}")

            temperatures.append(temperature)
            tec_currents.append(tec_current)
            tec_voltages.append(tec_voltage)
            #
            #  power reading
            #
            power = powermeter.read_single_power()
            powers.append(power)

            temp_avg = statistics.mean(temperatures)
            temp_std = statistics.stdev(temperatures) \
                if len(temperatures) > 1 else 0.0
            tec_current_avg = statistics.mean(tec_currents)
            tec_current_std = statistics.stdev(tec_currents) \
                if len(temperatures) > 1 else 0.0
            tec_voltage_avg = statistics.mean(tec_voltages)
            tec_voltage_std = statistics.stdev(tec_voltages) \
                if len(temperatures) > 1 else 0.0
            power_avg = statistics.mean(powers)
            power_std = statistics.stdev(powers) \
                if len(powers) > 1 else 0.0

            print(f"power is {power:.4f} W")

        #
        # Save
        #
        writer.writerow([
                            sw["current"],
                            read_ld_current,
                            temp_avg,
                            temp_std,
                            tec_current_avg,
                            tec_current_std,
                            tec_voltage_avg,
                            tec_voltage_std,
                            power_avg,
                            power_std
                        ] + list(kwargs.values()))
        print(f"Sweep saved to {filename}")

        print(
            f"I={sw["current"]:.4f}A "
            f"T={temp_avg:.3f}+-{temp_std:.3f} °C "
            f"P={power_avg:.3f}+-{power_std:.3f} W"
        )

        #
        # Return to LD channel
        #
        pro8000.select_slot(
            pro8000.Slot.SLOT6
        )

    pro8000.set_ld_off_ch6()
    pro8000.select_slot(tec_channel)

    print("measurement end")

