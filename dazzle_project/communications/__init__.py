"""
Import Connections. This dictionary is a database for connections in use in the lab. It is used by the equipment manager
to automatically recognize the instruments from their names or serial numbers if it is recognized it will instantiate the
according equipment class the instrument belongs.
"""

from .connection import VisaConnection, SerialConnection

CONNECTION_CLASSES = {
    "VISA": VisaConnection,
    "SERIAL": SerialConnection,
}

def get_connection_type(connection_name):

    return CONNECTION_CLASSES.get(connection_name.upper())