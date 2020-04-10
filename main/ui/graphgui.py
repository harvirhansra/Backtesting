import io
import sys
import time
import numpy as np

from contextlib import redirect_stdout
from PyQt5 import QtGui
from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtWidgets import QPushButton, QLabel, QPlainTextEdit

from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

sys.path.append('..')

from market.marketdata import get_data_from_csv
from trade.simple_strats import macd_crossing_singal_line

class BacktestingGraphs(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        self.layout = QtWidgets.QVBoxLayout(self._main)

        self.log = io.StringIO()

        # self._create_graph()
        self._create_log_box()
        self._start_button()


    def _create_graph(self):
        def _update_graph():
            self._dynamic_ax.clear()
            t = np.linspace(0, 10, 101)
            self._dynamic_ax.plot(t, np.sin(t + time.time()))
            self._dynamic_ax.figure.canvas.draw()

        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.layout.addWidget(dynamic_canvas)
        # self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(dynamic_canvas, self))
        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._timer = dynamic_canvas.new_timer(100, [(_update_graph, (), {})])
        self._timer.start()


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
        self.start_button.clicked.connect(self.start_bt)
        self.layout.addWidget(self.start_button)

    def start_bt(self):
            df = get_data_from_csv('../../resources/BTC_USD_2018-04-05_2020-01-25-CoinDesk.csv')
            with redirect_stdout(self.log):
                start = time.time()
                macd_crossing_singal_line(df, log=True, draw=False)
                exec_time = time.time() - start
                print(f'Backtesting ran for {exec_time} seconds')
                # self.print_timer.stop()
                self.print_text.setPlainText(self.log.getvalue())
                self.print_text.moveCursor(QtGui.QTextCursor.End)
    

if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = BacktestingGraphs()
    app.show()
    qapp.exec_()