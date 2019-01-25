from PySide2.QtWidgets import QMainWindow

from src.ui import Ui


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Swarm algorithms - project")
        self.gui = Ui(self)
        self.create_menu()
        self.setCentralWidget(self.gui)

    def create_menu(self):
        menu = self.menuBar()
        setmenu = menu.addMenu("Settings")
        setmenu.addAction("New run", self.gui.new_run)
        setmenu.addAction("Exit", self.close)
