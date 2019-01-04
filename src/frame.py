from PySide2.QtCore import Qt
from PySide2.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotWidget(FigureCanvas):
    def __init__(self, parent=None, width=6, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(PlotWidget, self).__init__(self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def mouseReleaseEvent(self, event):
        super(PlotWidget, self).mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.parent().moveStageUp()
        elif event.button() == Qt.RightButton:
            self.parent().moveStageDown()
