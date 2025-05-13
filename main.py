import sys
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import gui

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setApplicationName('iNatDex')
    widget = gui.startupWidget()
    widget.show()
    sys.exit(app.exec())