from PySide2.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class Canvas(FigureCanvas):
    def __init__(self, parent=None, width=6, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super(Canvas, self).__init__(fig)
        self.axes = fig.add_subplot(111)
        self.calc_plot()
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def calc_plot(self):
        pass


class Plot_widget(Canvas):
    def __init__(self):
        super(Plot_widget, self).__init__()

    def calc_plot(self):
        # override this function with your own
        pass
# class Plot_result(Canvas):
#     def __init__(self, title, x_label, y_label, x_data, y_data, style, labels, legend):
#         self.title = title
#         self.x_axis_name = x_label
#         self.y_axis_name = y_label
#         self.x_data = x_data
#         self.y_data = y_data
#         self.style = style
#         self.labels = labels
#         super(Plot_result, self).__init__()
#         if legend:
#             self.axes.legend(loc="upper right")
#
#     def calc_plot(self):
# self.axes.set_title(self.title)
# self.axes.set_xlabel(self.x_axis_name)
# self.axes.set_ylabel(self.y_axis_name)
# for i in range(len(self.x_data)):
#     self.axes.plot(self.x_data[i], self.y_data[i], self.style[i], label=self.labels[i])
