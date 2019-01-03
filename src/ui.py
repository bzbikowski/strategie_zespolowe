import json
import os

from PySide2.QtCore import QUrl
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QPlainTextEdit

import lib.algorithms as alg
from src.frame import Plot_widget
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

        self.setupUI()

    def setupUI(self):
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
        # todo make default page
        self.webPageView.load(QUrl('http://google.com'))

        self.mainLayout.addLayout(self.algorithmLayout)
        self.mainLayout.addWidget(self.webPageView)

    def makeAlgorithmList(self):
        for file in os.listdir("./src/schema"):
            self.algorithmList.addItem(file[:-5])

    def chooseAlgorithm(self, index):
        # todo change web page
        print(index.row(), index.data())

    def goToNextLayout(self):
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
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def makeParametersLayout(self):
        data = None
        with open(f"src/schema/{self.chosenAlgorithm}.json", "r") as f:
            data = json.load(f)
            print(data['elements'][0])
        for element in data['elements']:
            layout = QHBoxLayout()
            label = QLabel(element['name'])
            text = None
            if element['type'] == 'plain_text':
                text = QPlainTextEdit(element['default'])
            else:
                pass
            layout.addWidget(label)
            layout.addWidget(text)
            self.parametersLayout.addLayout(layout)

    def startAlgorithm(self):
        # take all parameters and problem params
        params = []
        for index in range(self.parametersLayout.count()):
            child = self.parametersLayout.itemAt(index)
            for x in range(child.count()):
                grandchild = child.itemAt(x).widget()
                if isinstance(grandchild, QPlainTextEdit):
                    try:
                        params.append(int(grandchild.toPlainText()))
                    except Exception:
                        print("Popraw dane.")
                        return
        print(params)

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
        # todo make layout for graphs and map
        self.canvas = Plot_widget(self)
        self.mainLayout.addWidget(self.canvas)
        algorithm = None
        if self.chosenAlgorithm == "Bees Algorithm":
            algorithm = alg.BeesAlgorithm(self.problem)
        algorithm.start_algorithm(*params)
        self.alg_data = algorithm.final_data
        self.setStage(0)

    def makeProblemsList(self):
        self.problems = []
        with open("src/problems.json", "r") as f:
            data = json.load(f)
            for function in data["functions"]:
                self.problemList.addItem(function["title"])
                self.problems.append(Problem(function))

    def setStage(self, stage):
        self.canvas.plot_scouts(self.alg_data, self.problem, stage)
