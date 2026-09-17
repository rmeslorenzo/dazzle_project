from .pro8000_gui import PRO8000_GUI

INSTRUMENT_GUI_CLASSES = {
    "PRO8000": PRO8000_GUI,
}

def get_instrument_gui_class(model_name):

    return INSTRUMENT_GUI_CLASSES.get(model_name.upper())