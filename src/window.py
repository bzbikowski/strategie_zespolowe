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
        modemenu = setmenu.addMenu("Choose mode")
        modemenu.addAction("Find minimum", lambda: self.gui.change_problem(0))
        modemenu.addAction("Traveling salesman problem", lambda: self.gui.change_problem(1))
        setmenu.addAction("Exit", self.close)
