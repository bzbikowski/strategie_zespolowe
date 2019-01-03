import numpy as np
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QSizePolicy
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotWidget(FigureCanvas):
    def __init__(self, parent=None, width=6, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(PlotWidget, self).__init__(self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot_scouts(self, data, problem, pair):
        self.fig.clf()
        ax = self.fig.add_subplot(111)

        N = 200
        x = np.linspace(-10.0, 10.0, N)
        y = np.linspace(-10.0, 10.0, N)

        X, Y = np.meshgrid(x, y)

        Z = np.zeros((N, N))
        for i in range(len(Z)):
            for j in range(len(Z[0])):
                Z[i][j] = problem.calculate(x[j], y[i])
        cs = ax.contourf(X, Y, Z, cmap=plt.get_cmap('plasma'))
        cbar = self.fig.colorbar(cs)
        for val, par in data['scouts_per_gen'][pair]:
            ax.plot(par[0], par[1], 'bo')
        ax.set_title('PyQt Matplotlib Example')
        self.draw()

    def mouseReleaseEvent(self, event):
        super(PlotWidget, self).mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.parent().moveStageUp()
