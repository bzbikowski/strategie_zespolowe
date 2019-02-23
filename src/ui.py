import json
import os
import sys

from PySide2.QtCore import QUrl, QLocale, Qt
from PySide2.QtGui import QIntValidator, QDoubleValidator
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QLineEdit, QTextEdit, \
    QMessageBox
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import lib.algorithms as alg
from src.frame import PlotWidget
from src.popup import ProblemDialog
from src.problem import Problem, ProblemTsp
from src.settings import TupleValidator


class Ui(QWidget):
    # todo make GUI more user friendly
    def __init__(self, parent):
        super(Ui, self).__init__()
        self.setParent(parent)
        self.mainLayout = None
        self.mapper = None
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
        self.problemList = None
        self.problemOptionLayout = None
        self.addProblemButton = None
        self.editProblemButton = None
        self.delProblemButton = None
        self.canvas = None
        self.canvasToolBar = None
        self.canvasInfoPanel = None
        self.infoLabel = None
        self.canvasToolLayout = None
        self.canvasButtonLayout = None
        self.nextButton = None
        self.prevButton = None

        self.algorithmMode = 0

        with open("./config.json", "r") as f:
            self.mapper = json.load(f)
            self.mapper = self.mapper["maps"]

        self.setup_ui()

    def setup_ui(self):
        """Create first layout for algorithm list and html view"""
        self.mainLayout = QHBoxLayout(self)
        self.algorithmLayout = QVBoxLayout()

        self.algorithmTitle = QLabel("Choose an algorithm")
        self.algorithmLayout.addWidget(self.algorithmTitle)

        self.algorithmSplitLayout = QHBoxLayout()
        self.algorithmLayout.addLayout(self.algorithmSplitLayout)

        self.algorithmList = QListWidget()
        self.algorithmList.clicked.connect(self.choose_algorithm)
        self.algorithmSplitLayout.addWidget(self.algorithmList)
        self.make_algorithm_list()

        self.algorithmNext = QPushButton("Next", self)
        self.algorithmNext.released.connect(self.go_to_next_layout)
        self.algorithmSplitLayout.addWidget(self.algorithmNext)

        self.webPageView = QWebEngineView()
        file_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "resources/help/default.html"))
        local_url = QUrl.fromLocalFile(file_path)
        self.webPageView.load(local_url)

        self.mainLayout.addLayout(self.algorithmLayout)
        self.mainLayout.addWidget(self.webPageView)

    def change_problem(self, nr):
        self.algorithmMode = nr
        # if nr == 0:
        #     pass
        # elif nr == 1:
        #     pass
        # else:
        #     pass
        self.reload_algorithm_list()

    def make_algorithm_list(self):
        for algorithm in self.mapper:
            with open(f"./resources/schema/{algorithm['schema']}.json") as f:
                data = json.load(f)
                if not self.check_if_schema_is_complete(data):
                    continue
                if self.algorithmMode == 0:
                    if data["type"] == "optimize":
                        self.algorithmList.addItem(algorithm['schema'])
                elif self.algorithmMode == 1:
                    if data["type"] == "tsp":
                        self.algorithmList.addItem(algorithm['schema'])

    @staticmethod
    def check_if_schema_is_complete(data):
        for elem in data["elements"]:
            if "name" not in elem or "type" not in elem or "default" not in elem:
                return False
            if elem["type"] not in ["int", "float", "tuple"]:
                return False
            if elem["type"] == "int":
                try:
                    int(elem["default"])
                except ValueError as e:
                    return False
            elif elem["type"] == "float":
                try:
                    float(elem["default"])
                except ValueError as e:
                    return False
        return True

    def choose_algorithm(self, index):
        file_path = None
        for algorithm in self.mapper:
            if algorithm["schema"] == index.data():
                file_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]),
                                                         f"resources/help/{algorithm['help']}.html"))
                break
        # todo check if file_path not null
        if os.path.exists(file_path):
            local_url = QUrl.fromLocalFile(file_path)
            self.webPageView.load(local_url)
        else:
            file_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "resources/help/none.html"))
            local_url = QUrl.fromLocalFile(file_path)
            self.webPageView.load(local_url)

    def go_to_next_layout(self):
        """Clear elements from first layout and make second layout for choosing parameters and problem"""
        try:
            self.chosenAlgorithm = self.algorithmList.currentItem().data(0)
        except AttributeError as e:
            # algorithm is not selected
            QMessageBox.warning(self, "Algorithm not chosen", "Please, choose an algorithm before going further.")
            return

        self.clear_layout(self.algorithmSplitLayout)
        self.algorithmSplitLayout.layout().deleteLater()
        self.clear_layout(self.algorithmLayout)
        self.algorithmLayout.layout().deleteLater()
        self.clear_layout(self.mainLayout)

        self.mainHelpLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.mainHelpLayout)

        self.parametersFullLayout = QHBoxLayout()
        self.mainHelpLayout.addLayout(self.parametersFullLayout)

        self.problemLayout = QVBoxLayout()
        self.parametersFullLayout.addLayout(self.problemLayout)

        self.problemList = QListWidget()
        self.problemLayout.addWidget(self.problemList)
        self.make_problems_list()

        self.problemOptionLayout = QHBoxLayout()
        self.problemLayout.addLayout(self.problemOptionLayout)

        self.addProblemButton = QPushButton("Add")
        self.addProblemButton.released.connect(self.open_add_menu)
        self.problemOptionLayout.addWidget(self.addProblemButton)

        self.editProblemButton = QPushButton("Edit")
        self.editProblemButton.released.connect(self.open_edit_menu)
        self.problemOptionLayout.addWidget(self.editProblemButton)

        self.delProblemButton = QPushButton("Delete")
        self.delProblemButton.released.connect(self.open_del_menu)
        self.problemOptionLayout.addWidget(self.delProblemButton)

        self.parametersLayout = QVBoxLayout()
        self.parametersFullLayout.addLayout(self.parametersLayout)

        self.make_parameters_layout()

        self.finalButton = QPushButton("Next")
        self.finalButton.released.connect(self.start_algorithm)
        self.mainHelpLayout.addWidget(self.finalButton)

    @staticmethod
    def clear_layout(layout):
        """Clear all widgets from given layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def make_parameters_layout(self):
        """Create layout for algorithm's parameters"""
        path = os.path.join(os.path.dirname(sys.argv[0]), f"resources/schema/{self.chosenAlgorithm}.json")
        data = None
        with open(path, "r") as f:
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
            elif element['type'] == 'tuple':
                text = QLineEdit(element['default'])
                text.setValidator(TupleValidator())
            layout.addWidget(label)
            layout.addWidget(text)
            self.parametersLayout.addLayout(layout)

    def start_algorithm(self):
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
                    validator = grandchild.validator()
                    if isinstance(validator, QDoubleValidator):
                        params.append(float(grandchild.text()))
                    elif isinstance(validator, TupleValidator):
                        params.append(self.convert_to_tuple(grandchild.text()))
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
        self.canvasInfoPanel.setStyleSheet("""
        font-size: 20px;
        """)
        self.infoLabel = QLabel("Running...")
        self.mainHelpLayout.addWidget(self.infoLabel, alignment=Qt.AlignCenter)

        for algorithm in self.mapper:
            if self.chosenAlgorithm == algorithm["schema"]:
                import inspect
                class_list = [m for m in inspect.getmembers(alg, inspect.isclass) if m[1].__module__ == alg.__name__]
                for cl in class_list:
                    if cl[0] == algorithm["algorithm"]:
                        self.algorithm = cl[1](self, self.problem, self.canvas, self.canvasInfoPanel)

        self.algorithm.setup_algorithm(*params)
        self.algorithm.started.connect(self.block_layout)
        self.algorithm.finished.connect(self.alg_finish)
        self.algorithm.stageChanged.connect(self.change_title)
        self.algorithm.start()
        # todo progress bar

    def block_layout(self):
        self.setEnabled(False)

    @staticmethod
    def convert_to_tuple(text):
        text = "".join(list(text)[1:-1])
        new = []
        params = text.split(',')
        for param in params:
            try:
                new.append(int(param))
            except ValueError:
                pass
        return new

    def alg_finish(self):
        self.setEnabled(True)
        self.clear_layout(self.problemOptionLayout)
        self.problemOptionLayout.layout().deleteLater()
        self.clear_layout(self.problemLayout)
        self.problemLayout.layout().deleteLater()
        for i in range(self.parametersLayout.count()):
            layout = self.parametersLayout.takeAt(0)
            self.clear_layout(layout)
            layout.layout().deleteLater()
        self.clear_layout(self.parametersLayout)
        self.parametersLayout.layout().deleteLater()
        self.clear_layout(self.parametersFullLayout)
        self.parametersFullLayout.layout().deleteLater()
        self.clear_layout(self.mainHelpLayout)
        self.mainHelpLayout.layout().deleteLater()
        self.clear_layout(self.mainLayout)
        self.canvasToolLayout = QVBoxLayout()
        self.canvasToolLayout.addWidget(self.canvas)
        self.canvasToolLayout.addWidget(self.canvasToolBar)
        self.mainLayout.addLayout(self.canvasToolLayout)
        self.canvasButtonLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.canvasButtonLayout)
        self.nextButton = QPushButton("Next")
        self.nextButton.released.connect(self.move_stage_up)
        self.canvasButtonLayout.addWidget(self.nextButton)
        self.prevButton = QPushButton("Prev")
        self.prevButton.released.connect(self.move_stage_down)
        self.canvasButtonLayout.addWidget(self.prevButton)
        self.mainLayout.addWidget(self.canvasInfoPanel)
        self.algorithm.plot_stage()
        self.parent().setFixedSize(1224, 768)

    def change_title(self, stage_nr, max_stage):
        self.parent().setWindowTitle(f"Swarm algorithms - project - scene {stage_nr}/{max_stage}")

    def make_problems_list(self):
        """Read data from json file with information about problems, then fill list widget with data"""
        self.problems = []
        path = os.path.join(os.path.dirname(sys.argv[0]), "resources/problems.json")
        with open(path, "r") as f:
            data = json.load(f)
            for function in data["functions"]:
                if self.algorithmMode == 0:
                    if function["type"] == "optimum":  # todo
                        self.problemList.addItem(function["title"])
                        self.problems.append(Problem(function))
                elif self.algorithmMode == 1:
                    if function["type"] == "tsp":
                        self.problemList.addItem(function["title"])
                        self.problems.append(ProblemTsp(function))

    def move_stage_up(self):
        self.algorithm.plot_stage(True)

    def move_stage_down(self):
        self.algorithm.plot_stage(False)

    def open_add_menu(self):
        if self.algorithmMode == 1:
            self.notimplemented()
            return
        if self.popup is not None and self.popup.isVisible():
            return
        self.popup = ProblemDialog(self)
        self.popup.show()

    def open_edit_menu(self):
        if self.algorithmMode == 1:
            self.notimplemented()
            return
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

    def open_del_menu(self):
        if self.algorithmMode == 1:
            self.notimplemented()
            return
        result = QMessageBox.information(self, "Delete element", "Are you sure you want to delete this element?",
                                         QMessageBox.Ok, QMessageBox.Cancel)
        if result == QMessageBox.Ok:
            item = self.problemList.takeItem(self.problemList.currentRow())
            path = os.path.join(os.path.dirname(sys.argv[0]), "resources/problems.json")
            with open(path, 'r') as f:
                data = json.load(f)
                for fun in self.problems:
                    if fun.title == item.data(0):
                        i = self.problems.index(fun)
                        self.problems.pop(i)
                        data["functions"].pop(i)
                        break

            with open(path, 'w') as f:
                json.dump(data, f, indent=4)

    def reload_problem_list(self):
        self.problemList.clear()
        self.problems = []
        self.make_problems_list()

    def reload_algorithm_list(self):
        self.algorithmList.clear()
        self.make_algorithm_list()

    def new_run(self):
        self.notimplemented()

    def notimplemented(self):
        # todo do a decorator
        _ = QMessageBox.information(self, "Not implemented", "This function is not yet implemented. ",
                                    QMessageBox.Ok)
        return
