import sys

from PySide2.QtWidgets import QApplication

from lib.algorithms import BeesAlgorithm
from src.window import Window


def main():
    alg = BeesAlgorithm(fun1, 2,  [(-5.00, 5.00)])
    res, val = alg.start_algorithm(500)
    print(res, val)


def fun1(*args):
    return 50 - args[0] ** 2 - args[1] ** 2


if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    app = Window()
    app.resize(1024, 768)
    app.show()
    sys.exit(qApp.exec_())
