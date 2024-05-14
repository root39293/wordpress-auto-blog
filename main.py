from PyQt5 import QtWidgets
from main_window import MainWindow

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    mainWindow = MainWindow()

    app.exec_()
