from .pro8000_gui import PRO8000_GUI
from .newport_2835_C import NEWPORT_2835_GUI

INSTRUMENT_GUI_CLASSES = {
    "PRO8000": PRO8000_GUI,
    "2835-C" : NEWPORT_2835_GUI,
}

def get_instrument_gui_class(model_name):

    return INSTRUMENT_GUI_CLASSES.get(model_name.upper())