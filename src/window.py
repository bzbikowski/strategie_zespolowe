from PySide2.QtWidgets import QMainWindow

from src.ui import Ui


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Swarm algorithms - project")
        self.create_menu()
        self.gui = Ui(self)
        self.setCentralWidget(self.gui)

    def create_menu(self):
        # todo create more options
        menu = self.menuBar()
        setMenu = menu.addMenu("Settings")
        setMenu.addAction("Exit", self.close)
