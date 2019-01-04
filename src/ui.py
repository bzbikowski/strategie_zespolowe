import json
import os

from PySide2.QtCore import QUrl, QLocale
from PySide2.QtGui import QIntValidator, QDoubleValidator
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QLineEdit

import lib.algorithms as alg
from src.frame import PlotWidget
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

        self.setupUI()

    def setupUI(self):
        """Create first layout for algorithm list and html view"""
        self.mainLayout = QHBoxLayout(self)
        self.algorithmLayout = QVBoxLayout()

        self.algorithmTitle = QLabel("Wybierz algorytm")
        self.algorithmLayout.addWidget(self.algorithmTitle)

        self.algorithmSplitLayout = QHBoxLayout()
        self.algorithmLayout.addLayout(self.algorithmSplitLayout)

        self.algorithmList = QListWidget()
        self.algorithmList.clicked.connect(self.chooseAlgorithm)
        self.algorithmSplitLayout.addWidget(self.algorithmList)
        self.makeAlgorithmList()

        self.algorithmNext = QPushButton("Dalej", self)
        self.algorithmNext.released.connect(self.goToNextLayout)
        self.algorithmSplitLayout.addWidget(self.algorithmNext)

        self.webPageView = QWebEngineView()
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "help/default.html"))
        local_url = QUrl.fromLocalFile(file_path)
        self.webPageView.load(local_url)

        self.mainLayout.addLayout(self.algorithmLayout)
        self.mainLayout.addWidget(self.webPageView)

    def makeAlgorithmList(self):
        # todo make algorithm appear if schema and algorithm (maybe help) is ok
        for file in os.listdir("./src/schema"):
            self.algorithmList.addItem(file[:-5])

    def chooseAlgorithm(self, index):
        # print(index.row(), index.data())
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"help/{index.data()}.html"))
        local_url = QUrl.fromLocalFile(file_path)
        # todo check if file exists, if not display default and display info
        if not local_url.isEmpty():
            self.webPageView.load(local_url)
        else:
            pass

    def goToNextLayout(self):
        """Clear elements from first layout and make second layout for choosing parameters and problem"""
        # todo display warning if any algorithm is not selected
        self.chosenAlgorithm = self.algorithmList.currentItem().data(0)

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

        # todo make functional buttons for adding, editing problems
        self.addProblemButton = QPushButton("Dodaj")
        self.problemOptionLayout.addWidget(self.addProblemButton)

        self.editProblemButton = QPushButton("Edytuj")
        self.problemOptionLayout.addWidget(self.editProblemButton)

        self.delProblemButton = QPushButton("Usun")
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
            print(data['elements'][0])
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
                        # todo print warning
                        return
                    if isinstance(grandchild.validator(), QDoubleValidator):
                        params.append(float(grandchild.text()))
                    else:
                        params.append(int(grandchild.text()))

        # todo display warning if any problem is not selected
        problem_name = self.problemList.currentItem().data(0)
        for p in self.problems:
            if str(p) == problem_name:
                self.problem = p
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
        # todo make widget to display informations
        self.canvas = PlotWidget(self)
        self.mainLayout.addWidget(self.canvas)
        self.canvasButtonLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.canvasButtonLayout)
        self.nextButton = QPushButton("Next")
        self.nextButton.released.connect(self.moveStageUp)
        self.canvasButtonLayout.addWidget(self.nextButton)
        self.prevButton = QPushButton("Prev")
        self.prevButton.released.connect(self.moveStageDown)
        self.canvasButtonLayout.addWidget(self.prevButton)
        # todo make algorithm running in separate thread
        if self.chosenAlgorithm == "Bees Algorithm":
            self.algorithm = alg.BeesAlgorithm(self.problem, self.canvas)
        self.algorithm.start_algorithm(*params)
        self.algorithm.plot_stage()

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
        # todo make end screen
        print("KAPPA")
