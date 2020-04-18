import io
import sys
import time
import numpy as np

from contextlib import redirect_stdout
from PyQt5 import QtGui
from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtWidgets import QPushButton, QLabel, QPlainTextEdit

from matplotlib.figure import Figure
from matplotlib.pyplot import annotate
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

sys.path.append('..')

from market.marketdata import get_data_from_csv
from trade.simple_strats import macd_crossing_singal_line, above_under_ma_std
from trade.calibration_strats import above_under_ma_std_calib

class BacktestingGraphs(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(1200, 700)
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        self.layout = QtWidgets.QVBoxLayout(self._main)

        self.log = io.StringIO()

        self._create_graph()
        self._create_log_box()
        self._start_button()


    def _create_graph(self):
        def _update_graph():
            self._dynamic_ax.clear()
            t = np.linspace(0, 10, 101)
            self._dynamic_ax.plot(t, np.sin(t + time.time()))
            self._dynamic_ax.figure.canvas.draw()

        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 8), facecolor='#404040'))
        self.layout.addWidget(dynamic_canvas)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(dynamic_canvas, self))
        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._format_graph()
        # self._timer = dynamic_canvas.new_timer(100, [(_update_graph, (), {})])
        # self._timer.start()


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
        print('Starting Backtesting')
        df = get_data_from_csv('../../resources/BTC_USD_2018-04-05_2020-01-25-CoinDesk.csv')
        # df = get_data_from_csv('../../resources/BTC_USD_2019-07-12_2019-12-30-CoinDesk.csv')
        # with redirect_stdout(self.log):
            # bt_result = above_under_ma_std(df, stds=1.5, lookback=14, log=True, draw=False)
        bt_result = above_under_ma_std_calib(df)
        self.print_text.setPlainText(self.log.getvalue())
        self.print_text.moveCursor(QtGui.QTextCursor.End)
        self._plot_graph(bt_result)
        self._dynamic_ax.figure.canvas.draw()

    def _format_graph(self):
        self._dynamic_ax.set_ylabel('price', color ='white')
        self._dynamic_ax.set_xlabel('date', color='white')
        self._dynamic_ax.tick_params(axis='x', colors='white')
        self._dynamic_ax.tick_params(axis='y', colors='white')
        self._dynamic_ax.set_facecolor('#404040')

    def _plot_graph(self, res):
        self._dynamic_ax.clear()
        self._dynamic_ax.plot(res.date, res.price, linewidth=1, color='#53a8b2')
        self._dynamic_ax.plot(res.date, res.metric1, linewidth=0.8, color='#e9de1c')
        self._dynamic_ax.plot(res.date, res.metric2, linewidth=0.8, color='#1ce926')
        self._dynamic_ax.plot(res.date, res.metric3, linewidth=0.8, color='#e91c1c')
        for date, price, action in zip(res.actiondate, res.actionprice, res.action):
            self._dynamic_ax.annotate(action, (date, price), color='white',
                                        xycoords='data', xytext=(0, 40), 
                                        textcoords='offset points',
                                        arrowprops=dict(arrowstyle="->",
                                                        connectionstyle="arc3",
                                                        color='white', lw=0.5))

        

if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = BacktestingGraphs()
    app.show()
    qapp.exec_()