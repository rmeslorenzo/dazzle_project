test_list = [
                "Model",
                "laser",
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
            ]

measurement_info = {
            "collimator" : "PAF2A-11C",
            "pinhole"    : "P200HK_100um",
            "detector"   : "818-UV"
        }

test_results = test_list + list(measurement_info.keys())

print("test")