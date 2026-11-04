from dazzle_project.instruments.led_controller import LED_CONTROLLER


ld_ctrl = LED_CONTROLLER(port='COM3')

ld_ctrl.enable_red()

ld_ctrl.close()

print("test")




