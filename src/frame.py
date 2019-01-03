import time

import numpy as np
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QSizePolicy
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class Plot_widget(FigureCanvas):
    def __init__(self, parent=None, width=6, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super(Plot_widget, self).__init__(fig)
        self.axes = fig.add_subplot(111)
        self.cbar = None
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot_scouts(self, data, problem, pair):
        # ax = self.figure.add_subplot(111)
        self.axes.cla()
        if self.cbar is not None:
            self.cbar.remove()
        N = 200
        x = np.linspace(-10.0, 10.0, N)
        y = np.linspace(-10.0, 10.0, N)

        X, Y = np.meshgrid(x, y)

        Z = np.zeros((N, N))
        for i in range(len(Z)):
            for j in range(len(Z[0])):
                Z[i][j] = problem.calculate(x[j], y[i])
        cs = self.axes.contourf(X, Y, Z, cmap=plt.get_cmap('plasma'))
        self.cbar = self.figure.colorbar(cs)
        for val, par in data['scouts_per_gen'][pair]:
            self.axes.plot(par[0], par[1], 'bo')
        self.axes.set_title('PyQt Matplotlib Example')
        self.draw()

    def mouseReleaseEvent(self, event):
        super(Plot_widget, self).mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.parent().setStage(1)
