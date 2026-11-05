from dazzle_project.instruments.led_controller import LedController


ld_ctrl = LedController(port='COM3')

ld_ctrl.enable_green()

ld_ctrl.write("*IDN?")

ld_ctrl.close()

print("test")
