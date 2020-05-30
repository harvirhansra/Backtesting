import io
import sys
import time
import numpy as np

from PyQt5 import QtGui
from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtWidgets import QPushButton, QLabel, QPlainTextEdit
from contextlib import redirect_stdout
from matplotlib.figure import Figure
from matplotlib.pyplot import annotate
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)


class BacktestingGUI(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(1200, 700)
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        self.layout = QtWidgets.QVBoxLayout(self._main)

        self.log = io.StringIO()

        self._create_price_graph()
        # self._create_std_graph()
        self._create_log_box()
        self._start_button()

    def _create_price_graph(self):
        price_canvas = FigureCanvas(Figure(figsize=(50, 80), facecolor='#404040', dpi=80))
        self.layout.addWidget(price_canvas)
        self.addToolBar(QtCore.Qt.BottomToolBarArea,
                        NavigationToolbar(price_canvas, self))
        self._price_ax = price_canvas.figure.subplots()
        self._price2_ax = self._price_ax.twinx()
        self._format_price_graph()

    def _create_std_graph(self):
        std_canvas = FigureCanvas(Figure(figsize=(5, 8), facecolor='#404040'))
        self.layout.addWidget(std_canvas)
        # self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(std_canvas, self))
        self._std_ax = std_canvas.figure.subplots()
        self._format_std_graph()

    def _create_log_box(self):
        def _update_text():
            self.print_text.setPlainText(self.log.getvalue())
            self.print_text.moveCursor(QtGui.QTextCursor.End)

        self.print_text = QPlainTextEdit()
        self.print_text.setReadOnly(True)
        self.layout.addWidget(self.print_text)
        # self.print_timer = QTimer()
        # self.print_timer.timeout.connect(_update_text)
        # self.print_timer.start(1000)

    def _start_button(self):
        self.start_button = QPushButton('Start Backtesting')
        self.start_button.clicked.connect(self._start_bt)
        self.layout.addWidget(self.start_button)

    def _start_bt(self):
        self.run_function()
        self.print_text.setPlainText(self.log.getvalue())
        self.print_text.moveCursor(QtGui.QTextCursor.End)
        # self._std_ax.figure.canvas.draw()

    def _format_price_graph(self):
        self._price_ax.set_ylabel('price', color='white')
        self._price2_ax.set_ylabel('std', color='white')
        self._price_ax.set_xlabel('date', color='white')
        self._price_ax.tick_params(axis='x', colors='white')
        self._price_ax.tick_params(axis='y', colors='white', which='both')
        self._price_ax.set_facecolor('#404040')

    def _format_std_graph(self):
        self._std_ax.set_ylabel('std', color='white')
        self._std_ax.set_xlabel('date', color='white')
        self._std_ax.tick_params(axis='x', colors='white')
        self._std_ax.tick_params(axis='y', colors='white')
        self._std_ax.set_facecolor('#404040')

    def plot_price_graph(self, dates, price, plays, metric1, metric2, metric3):
        self._price_ax.clear()
        self._price_ax.plot(dates, price, linewidth=1.5, color='#53a8b2')
        self._price_ax.plot(dates, metric1, linewidth=0.8, color='#e9de1c')
        self._price_ax.plot(dates, metric2, linewidth=0.8, color='#1ce926')
        self._price_ax.plot(dates, metric3, linewidth=0.8, color='#e91c1c')
        # self._price2_ax.plot(res.date, res.metric4, linewidth=0.5, color='#ffbdd8')
        for date, price, action in plays:
            self._price_ax.annotate(action, (date, price), color='white',
                                    xycoords='data', xytext=(0, 40),
                                    textcoords='offset points',
                                    arrowprops=dict(arrowstyle="->",
                                                    connectionstyle="arc3",
                                                    color='white', lw=0.5))
        self._price_ax.figure.canvas.draw()

    def _plot_std_graph(self, res):
        self._std_ax.clear()
        self._std_ax.plot(res.date, res.metric4, linewidth=1.5, color='#53a8b2')


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = BacktestingGraphs()
    app.show()
    qapp.exec_()
