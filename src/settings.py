from PySide2.QtGui import QValidator


class TupleValidator(QValidator):
    # todo finish
    def __init__(self):
        super().__init__()

    def validate(self, arg__1: str, arg__2: int):
        return QValidator.Acceptable

    def fixup(self, arg__1: str):
        pass
