from .pro8000_gui import PRO8000_GUI, PRO_8000
from .newport_2835_C import NEWPORT_2835_GUI

INSTRUMENT_GUI_CLASSES = {
    "PRO8000": PRO8000_GUI,
    "2835-C" : NEWPORT_2835_GUI,
}

PRO8000_DEFAULT_VALUES = {
    "set_temperature" : 25,
    "tec_current_limit" : 0.9,
    "pid"   : [1.5, 0.1, 1.1],
    "slot6_enable" : False,
    "polarity_ch6" : [PRO_8000.Polarity.Anode.value, PRO_8000.Polarity.Anode.value] # [0] : pd polarity, [1] : ld polarity
}


def get_instrument_gui_class(model_name):

    return INSTRUMENT_GUI_CLASSES.get(model_name.upper())