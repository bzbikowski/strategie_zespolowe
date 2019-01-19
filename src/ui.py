import json
import os

from PySide2.QtCore import QUrl, QLocale, Qt
from PySide2.QtGui import QIntValidator, QDoubleValidator
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QLineEdit, QTextEdit, \
    QMessageBox
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import lib.algorithms as alg
from src.frame import PlotWidget
from src.popup import ProblemDialog
from src.problem import Problem


class Ui(QWidget):
    # todo make GUI more user friendly
    def __init__(self, parent):
        super(Ui, self).__init__()
        self.setParent(parent)
        self.mainLayout = None
        self.algorithmLayout = None
        self.webPageView = None
        self.algorithmTitle = None
        self.algorithmList = None
        self.chosenAlgorithm = None
        self.algorithmSplitLayout = None
        self.algorithmNext = None
        self.problemLayout = None
        self.parametersLayout = None
        self.mainHelpLayout = None
        self.parametersFullLayout = None
        self.finalButton = None
        self.problems = None
        self.problem = None
        self.algorithm = None
        self.popup = None

        self.setupUI()

    def setupUI(self):
        """Create first layout for algorithm list and html view"""
        self.mainLayout = QHBoxLayout(self)
        self.algorithmLayout = QVBoxLayout()

        self.algorithmTitle = QLabel("Choose an algorithm")
        self.algorithmLayout.addWidget(self.algorithmTitle)

        self.algorithmSplitLayout = QHBoxLayout()
        self.algorithmLayout.addLayout(self.algorithmSplitLayout)

        self.algorithmList = QListWidget()
        self.algorithmList.clicked.connect(self.chooseAlgorithm)
        self.algorithmSplitLayout.addWidget(self.algorithmList)
        self.makeAlgorithmList()

        self.algorithmNext = QPushButton("Next", self)
        self.algorithmNext.released.connect(self.goToNextLayout)
        self.algorithmSplitLayout.addWidget(self.algorithmNext)

        self.webPageView = QWebEngineView()
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "help/default.html"))
        local_url = QUrl.fromLocalFile(file_path)
        self.webPageView.load(local_url)

        self.mainLayout.addLayout(self.algorithmLayout)
        self.mainLayout.addWidget(self.webPageView)

    def makeAlgorithmList(self):
        for file in os.listdir("./src/schema"):
            error = False
            with open(f"./src/schema/{file}") as f:
                data = json.load(f)
                for elem in data["elements"]:
                    if "name" not in elem or "type" not in elem or "default" not in elem:
                        error = True
                        break
                    if elem["type"] not in ["int", "float"]:
                        error = True
                        break
                    if elem["type"] == "int":
                        try:
                            int(elem["default"])
                        except ValueError as e:
                            error = True
                            break
                    elif elem["type"] == "float":
                        try:
                            float(elem["default"])
                        except ValueError as e:
                            error = True
                            break
            if error:
                continue
            self.algorithmList.addItem(file[:-5])

    def chooseAlgorithm(self, index):
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"help/{index.data()}.html"))
        if os.path.exists(file_path):
            local_url = QUrl.fromLocalFile(file_path)
            self.webPageView.load(local_url)
        else:
            file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"help/none.html"))
            local_url = QUrl.fromLocalFile(file_path)
            self.webPageView.load(local_url)

    def goToNextLayout(self):
        """Clear elements from first layout and make second layout for choosing parameters and problem"""
        try:
            self.chosenAlgorithm = self.algorithmList.currentItem().data(0)
        except AttributeError as e:
            # algorithm is not selected
            QMessageBox.warning(self, "Algorithm not chosen", "Please, choose an algorithm before going further.")
            return

        self.clearLayout(self.algorithmSplitLayout)
        self.algorithmSplitLayout.layout().deleteLater()
        self.clearLayout(self.algorithmLayout)
        self.algorithmLayout.layout().deleteLater()
        self.clearLayout(self.mainLayout)

        self.mainHelpLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.mainHelpLayout)

        self.parametersFullLayout = QHBoxLayout()
        self.mainHelpLayout.addLayout(self.parametersFullLayout)

        self.problemLayout = QVBoxLayout()
        self.parametersFullLayout.addLayout(self.problemLayout)

        self.problemList = QListWidget()
        self.problemLayout.addWidget(self.problemList)
        self.makeProblemsList()

        self.problemOptionLayout = QHBoxLayout()
        self.problemLayout.addLayout(self.problemOptionLayout)

        self.addProblemButton = QPushButton("Add")
        self.addProblemButton.released.connect(self.openAddMenu)
        self.problemOptionLayout.addWidget(self.addProblemButton)

        self.editProblemButton = QPushButton("Edit")
        self.editProblemButton.released.connect(self.openEditMenu)
        self.problemOptionLayout.addWidget(self.editProblemButton)

        self.delProblemButton = QPushButton("Delete")
        self.delProblemButton.released.connect(self.openDelMenu)
        self.problemOptionLayout.addWidget(self.delProblemButton)

        self.parametersLayout = QVBoxLayout()
        self.parametersFullLayout.addLayout(self.parametersLayout)

        self.makeParametersLayout()

        self.finalButton = QPushButton("Next")
        self.finalButton.released.connect(self.startAlgorithm)
        self.mainHelpLayout.addWidget(self.finalButton)

    def clearLayout(self, layout):
        """Clear all widgets from given layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def makeParametersLayout(self):
        """Create layout for algorithm's parameters"""
        data = None
        with open(f"src/schema/{self.chosenAlgorithm}.json", "r") as f:
            data = json.load(f)
        for element in data['elements']:
            layout = QHBoxLayout()
            label = QLabel(element['name'])
            text = None
            if element['type'] == 'int':
                text = QLineEdit(element['default'])
                text.setValidator(QIntValidator())
            elif element['type'] == 'float':
                text = QLineEdit(element['default'])
                lo = QLocale(QLocale.c())
                lo.setNumberOptions(QLocale.RejectGroupSeparator)
                val = QDoubleValidator()
                val.setLocale(lo)
                text.setValidator(val)
            else:
                pass
            layout.addWidget(label)
            layout.addWidget(text)
            self.parametersLayout.addLayout(layout)

    def startAlgorithm(self):
        """Check if inputed data is correct, gather all data and setup layout"""
        # take all parameters and problem params
        params = []
        for index in range(self.parametersLayout.count()):
            child = self.parametersLayout.itemAt(index)
            for x in range(child.count()):
                grandchild = child.itemAt(x).widget()
                if isinstance(grandchild, QLineEdit):
                    if grandchild.text() == "":
                        QMessageBox.warning(self, "Empty field",
                                            "Empty fields must be filled with correct values.")
                        return
                    if isinstance(grandchild.validator(), QDoubleValidator):
                        params.append(float(grandchild.text()))
                    else:
                        params.append(int(grandchild.text()))
        try:
            problem_name = self.problemList.currentItem().data(0)
        except AttributeError as e:
            # problem is not selected
            QMessageBox.warning(self, "Problem not chosen",
                                "Please, choose an problem for the algorithm to solve before going further.")
            return

        for p in self.problems:
            if str(p) == problem_name:
                self.problem = p
        self.canvas = PlotWidget(self)
        self.canvasToolBar = NavigationToolbar(self.canvas, self)
        self.canvasInfoPanel = QTextEdit()
        # todo custom font
        self.info = QLabel("Running...")
        self.mainHelpLayout.addWidget(self.info, alignment=Qt.AlignCenter)
        # todo automate linking chosenAlgorithm with correct algorithm from algorithm.py
        if self.chosenAlgorithm == "Bees Algorithm":
            self.algorithm = alg.BeesAlgorithm(self, self.problem, self.canvas, self.canvasInfoPanel)
        self.algorithm.setup_algorithm(*params)
        self.algorithm.started.connect(self.block_layout)
        self.algorithm.finished.connect(self.alg_finish)
        self.algorithm.stageChanged.connect(self.change_title)
        self.algorithm.start()

    def block_layout(self):
        self.setEnabled(False)

    def alg_finish(self):
        self.setEnabled(True)
        self.clearLayout(self.problemOptionLayout)
        self.problemOptionLayout.layout().deleteLater()
        self.clearLayout(self.problemLayout)
        self.problemLayout.layout().deleteLater()
        for i in range(self.parametersLayout.count()):
            layout = self.parametersLayout.takeAt(0)
            self.clearLayout(layout)
            layout.layout().deleteLater()
        self.clearLayout(self.parametersLayout)
        self.parametersLayout.layout().deleteLater()
        self.clearLayout(self.parametersFullLayout)
        self.parametersFullLayout.layout().deleteLater()
        self.clearLayout(self.mainHelpLayout)
        self.mainHelpLayout.layout().deleteLater()
        self.clearLayout(self.mainLayout)
        self.canvasToolLayout = QVBoxLayout()
        self.canvasToolLayout.addWidget(self.canvas)
        self.canvasToolLayout.addWidget(self.canvasToolBar)
        self.mainLayout.addLayout(self.canvasToolLayout)
        self.canvasButtonLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.canvasButtonLayout)
        self.nextButton = QPushButton("Next")
        self.nextButton.released.connect(self.moveStageUp)
        self.canvasButtonLayout.addWidget(self.nextButton)
        self.prevButton = QPushButton("Prev")
        self.prevButton.released.connect(self.moveStageDown)
        self.canvasButtonLayout.addWidget(self.prevButton)
        self.mainLayout.addWidget(self.canvasInfoPanel)
        self.algorithm.plot_stage()
        self.parent().setFixedSize(1224, 768)

    def change_title(self, stage_nr, max_stage):
        self.parent().setWindowTitle(f"Swarm algorithms - project - scene {stage_nr}/{max_stage}")

    # def additional_info(self, which, *args):
    #     if which == "table":
    #         self.additionalWidget = QTableWidget(10, 4)
    #         self.additionalWidget.setItem(0, 0, QTableWidgetItem("Kappa"))
    #         self.mainLayout.addWidget(self.additionalWidget)

    def makeProblemsList(self):
        """Read data from json file with information about problems, then fill list widget with data"""
        self.problems = []
        with open("src/problems.json", "r") as f:
            data = json.load(f)
            for function in data["functions"]:
                self.problemList.addItem(function["title"])
                self.problems.append(Problem(function))

    def moveStageUp(self):
        if self.algorithm.plot_stage(True) == 1:
            self.end_screen()

    def moveStageDown(self):
        self.algorithm.plot_stage(False)

    def end_screen(self):
        # todo make end screen ?
        print("KAPPA")

    def openAddMenu(self):
        if self.popup is not None and self.popup.isVisible():
            return
        self.popup = ProblemDialog(self)
        self.popup.show()

    def openEditMenu(self):
        if self.popup is not None and self.popup.isVisible():
            return
        problem = None
        try:
            problem_name = self.problemList.currentItem().data(0)
        except AttributeError as e:
            # problem is not selected
            return
        for p in self.problems:
            if str(p) == problem_name:
                problem = p
        self.popup = ProblemDialog(self, problem)
        self.popup.show()

    def openDelMenu(self):
        result = QMessageBox.information(self, "Delete element", "Are you sure you want to delete this element?",
                                         QMessageBox.Ok, QMessageBox.Cancel)
        if result == QMessageBox.Ok:
            item = self.problemList.takeItem(self.problemList.currentRow())
            with open("./src/problems.json", 'r') as f:
                data = json.load(f)
                for fun in self.problems:
                    if fun.title == item.data(0):
                        i = self.problems.index(fun)
                        self.problems.pop(i)
                        data["functions"].pop(i)
                        break

            with open("./src/problems.json", 'w') as f:
                json.dump(data, f, indent=4)

    def reload_problem_list(self):
        self.problemList.clear()
        self.problems = []
        self.makeProblemsList()
