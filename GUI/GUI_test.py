from PyQt6.QtWidgets import QComboBox, QDoubleSpinBox, QCheckBox, QLabel, QLCDNumber

import sys

from PyQt6.QtWidgets import QApplication, QWidget

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("PRO-8000")
window.resize(800, 600)

window.show()

sys.exit(app.exec())