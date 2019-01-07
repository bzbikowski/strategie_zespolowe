import json

from PySide2.QtGui import QIntValidator, QCloseEvent
from PySide2.QtWidgets import QWidget, QGridLayout, QLineEdit, QLabel, QMessageBox, QPushButton


class ProblemDialog(QWidget):
    def __init__(self, problem=None):
        super(ProblemDialog, self).__init__()
        self.lastSize = 0
        self.setFixedSize(400, 400)
        self.mainLayout = QGridLayout(self)
        self.make_layout()

        if problem is not None:
            # edit
            pass
        else:
            # new
            pass

    def make_layout(self):
        self.titleLabel = QLabel("Title for algorithm")
        self.mainLayout.addWidget(self.titleLabel, 0, 0)
        self.titleField = QLineEdit()
        self.mainLayout.addWidget(self.titleField, 0, 1)

        self.funLabel = QLabel("Function")
        self.mainLayout.addWidget(self.funLabel, 1, 0)
        self.funField = QLineEdit()
        self.mainLayout.addWidget(self.funField, 1, 1)

        self.paramLabel = QLabel("Number of parameters")
        self.mainLayout.addWidget(self.paramLabel, 2, 0)
        self.paramField = QLineEdit()
        self.paramField.setValidator(QIntValidator())
        self.paramField.textChanged.connect(lambda: self.field_control(self.paramField.text()))
        self.mainLayout.addWidget(self.paramField, 2, 1)

        self.saveButton = QPushButton("Save", self)
        self.saveButton.released.connect(self.save)
        self.mainLayout.addWidget(self.saveButton, 3, 0, )
        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.released.connect(self.close)
        self.mainLayout.addWidget(self.cancelButton, 3, 1)

    def field_control(self, number):
        if number == "":
            return
        number = int(number)
        if number - self.lastSize < 0:
            for i in range(self.mainLayout.count() - 1, self.mainLayout.count() - 1 - 2 * (self.lastSize - number), -1):
                print(i)
                item = self.mainLayout.takeAt(i).widget()
                item.deleteLater()
        elif number - self.lastSize == 0:
            return
        else:
            for index in range(self.lastSize, number):
                print(index)
                label = QLabel(f"Arg{index}")
                field = QLineEdit()
                field.setPlaceholderText("Format: [min;max]")
                self.mainLayout.addWidget(label, index, 3)
                self.mainLayout.addWidget(field, index, 4)
        self.lastSize = number

    def closeEvent(self, event: QCloseEvent):
        blank = True
        for i in range(3):  # hardcoded
            item = self.mainLayout.itemAtPosition(i, 1).widget()
            if not item.text() == "":
                blank = False
        for i in range(self.lastSize):
            item = self.mainLayout.itemAtPosition(i, 3).widget()
            if not item.text() == "":
                blank = False
        # for i in range(self.mainLayout.count()):
        #     print(i)
        #     item = self.mainLayout.itemAtPosition(i, 1).widget()
        #     # if item.widget():
        #     if isinstance(item, QLineEdit):
        #         if not item.text() == "":
        #             blank = False
        if not blank:
            res = QMessageBox.information(self, "Leaving without saving",
                                          "Are you sure you want to discard this data?", QMessageBox.Yes,
                                          QMessageBox.Cancel)
            if res == QMessageBox.Cancel:
                return
        super(ProblemDialog, self).closeEvent(event)

    def save(self):
        # todo validate data
        # todo check if title already exists
        data = None
        with open("./src/problems.json", "r+") as f:
            data = json.load(f)
            for fun in data["functions"]:
                if fun["title"] == self.titleField.text():
                    pass
        # ...
        # todo parse arguments
        form = {"title": self.titleField.text(),
                "fun": self.funField.text(),
                "x_param": self.paramField.text(),
                "x_min": [],
                "x_max": []}
        data["functions"].append(form)
        with open("./src/problems.json", "w") as f:
            json.dump(data, f)
