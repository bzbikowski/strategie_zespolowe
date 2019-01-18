import json

from PySide2.QtGui import QIntValidator, QCloseEvent
from PySide2.QtWidgets import QWidget, QGridLayout, QLineEdit, QLabel, QMessageBox, QPushButton


class ProblemDialog(QWidget):
    def __init__(self, parent, problem=None):
        super(ProblemDialog, self).__init__()
        self.parent = parent
        self.lastSize = 0
        self.setFixedSize(400, 400)
        self.mainLayout = QGridLayout(self)
        self.make_layout()
        if problem is not None:
            self.previousTitle = None
            self.editing = True
            self.fill_data(problem)
        else:
            self.editing = False
        self.saved = True

    def make_layout(self):
        self.titleLabel = QLabel("Title for algorithm")
        self.mainLayout.addWidget(self.titleLabel, 0, 0)
        self.titleField = QLineEdit()
        self.titleField.textChanged.connect(self.check_unsaved)
        self.mainLayout.addWidget(self.titleField, 0, 1)

        self.funLabel = QLabel("Function")
        self.mainLayout.addWidget(self.funLabel, 1, 0)
        self.funField = QLineEdit()
        self.funField.textChanged.connect(self.check_unsaved)
        self.mainLayout.addWidget(self.funField, 1, 1)

        self.paramLabel = QLabel("Number of parameters")
        self.mainLayout.addWidget(self.paramLabel, 2, 0)
        self.paramField = QLineEdit()
        self.paramField.setValidator(QIntValidator())
        self.paramField.textChanged.connect(lambda: self.field_control(self.paramField.text()))
        self.paramField.textChanged.connect(self.check_unsaved)
        self.mainLayout.addWidget(self.paramField, 2, 1)

        self.saveButton = QPushButton("Save", self)
        self.saveButton.released.connect(self.save)
        self.mainLayout.addWidget(self.saveButton, 3, 0)
        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.released.connect(self.close)
        self.mainLayout.addWidget(self.cancelButton, 3, 1)

    def field_control(self, number):
        if number == "":
            return
        number = int(number)
        if number - self.lastSize < 0:
            for i in range(self.mainLayout.count() - 1, self.mainLayout.count() - 1 - 2 * (self.lastSize - number), -1):
                item = self.mainLayout.takeAt(i).widget()
                item.deleteLater()
        elif number - self.lastSize == 0:
            return
        else:
            for index in range(self.lastSize, number):
                print(index)
                label = QLabel(f"Arg{index}")
                field = QLineEdit()
                field.textChanged.connect(self.check_unsaved)
                field.setPlaceholderText("Format: min;max")
                self.mainLayout.addWidget(label, index, 2)
                self.mainLayout.addWidget(field, index, 3)
        self.lastSize = number

    def fill_data(self, problem):
        self.previousTitle = problem.title
        self.titleField.setText(problem.title)
        self.funField.setText(problem.fun)
        self.paramField.setText(str(problem.number_of_params))
        self.field_control(int(problem.number_of_params))
        for i in range(self.lastSize):
            item = self.mainLayout.itemAtPosition(i, 3).widget()
            item.setText(f"{problem.low[i]};{problem.high[i]}")

    def check_unsaved(self):
        self.saved = False

    def closeEvent(self, event: QCloseEvent):
        if not self.check_if_empty() and not self.saved:
            res = QMessageBox.information(self, "Leaving without saving",
                                          "Are you sure you want to leave? Any unsaved data will be discarded",
                                          QMessageBox.Yes, QMessageBox.Cancel)
            if res == QMessageBox.Cancel:
                return
        super(ProblemDialog, self).closeEvent(event)

    def check_if_empty(self):
        blank = True
        for i in range(3):  # hardcoded
            item = self.mainLayout.itemAtPosition(i, 1).widget()
            if not item.text() == "":
                blank = False
        for i in range(self.lastSize):
            item = self.mainLayout.itemAtPosition(i, 3).widget()
            if not item.text() == "":
                blank = False
        return blank

    def save(self):
        # check if all fields are not empty
        if self.check_if_empty():
            QMessageBox.warning(self, "Empty fields", "Empty fields must be filled with correct values.",
                                QMessageBox.Ok)
            return
        min_v, max_v = self.parse_arguments()
        if min_v is None and max_v is None:
            # error while parsing arguments
            # todo say especially which argument must be corrected
            QMessageBox.warning(self, "Parsing error",
                                "There is a problem with one of the arguments."
                                " Please, check if inputed data is correct and in the correct format",
                                QMessageBox.Ok)
            return

        data = None
        with open("./src/problems.json", "r") as f:
            data = json.load(f)
        if self.editing:
            index = -1
            for i, fun in enumerate(data["functions"]):
                if fun["title"] == self.previousTitle:
                    index = i
                    break
            data["functions"][index] = {
                "title": self.titleField.text(),
                "fun": self.funField.text(),
                "x_param": int(self.paramField.text()),
                "x_min": min_v,
                "x_max": max_v}
        else:
            for fun in data["functions"]:
                if fun["title"] == self.titleField.text():
                    QMessageBox.warning(self, "Duplicate title",
                                        "This name for the title already exists. Please, change it for other name.",
                                        QMessageBox.Ok)
                    return
            form = {"title": self.titleField.text(),
                    "fun": self.funField.text(),
                    "x_param": int(self.paramField.text()),
                    "x_min": min_v,
                    "x_max": max_v}
            data["functions"].append(form)

        with open("./src/problems.json", "w") as f:
            json.dump(data, f, indent=4)

        QMessageBox.information(self, "Save complete", "Data is now saved. ", QMessageBox.Ok)
        self.saved = True
        self.parent.reload_problem_list()

    def parse_arguments(self):
        min_vector = []
        max_vector = []
        for i in range(self.lastSize):
            data = self.mainLayout.itemAtPosition(i, 3).widget().text()
            n, x = data.split(";")
            try:
                min_vector.append(float(n))
                max_vector.append(float(x))
            except ValueError as e:
                # given values are not type of float
                return None, None

        return min_vector, max_vector
