from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel
)
from docutils.nodes import address

from dazzle_project.instruments.equipment import DummyEquipment

class InstrumentWidget(QWidget):
    def __init__(self, instrument):
        super().__init__()
        self.instrument = instrument

        self.mainLayout = QVBoxLayout(self)



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    equipment = DummyEquipment()
    widget = InstrumentWidget(equipment)
    widget.show()

    sys.exit(app.exec())