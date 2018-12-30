import sys

from PySide2.QtWidgets import QApplication

from src.window import Window

if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    app = Window()
    app.resize(1024, 768)
    app.show()
    sys.exit(qApp.exec_())
