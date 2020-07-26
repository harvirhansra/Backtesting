import io
import sys
import numpy as np

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRunnable, QThreadPool, QTimer
from PyQt5.QtWidgets import QPushButton, QPlainTextEdit
from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)


class BacktestingGUI(QtWidgets.QMainWindow):

    def __init__(self, strat_type):
        super().__init__()

        self.showFullScreen()

        self.strat_type = strat_type

        self.resize(1000, 500)
        self._main = QtWidgets.QWidget()

        self.layout = QtWidgets.QVBoxLayout()
        self._main.setLayout(self.layout)
        self.setCentralWidget(self._main)

        self.top = QtWidgets.QHBoxLayout()
        self.middle = QtWidgets.QHBoxLayout()
        self.bottom = QtWidgets.QVBoxLayout()

        self.layout.addLayout(self.top)
        self.layout.addLayout(self.middle)
        self.layout.addLayout(self.bottom)

        self.log = io.StringIO()

        self._create_price_graph(self.top)
        self._create_log_box(self.middle)
        self._create_equity_graph(self.middle)
        self._create_drawdown_graph(self.middle)
        self._start_button(self.bottom)

        self.threadpool = QThreadPool()
        # self.threadpool.setMaxThreadCount(2)

    def _create_price_graph(self, section):
        price_canvas = FigureCanvas(Figure(figsize=(25, 40), facecolor='#404040', dpi=80))
        section.addWidget(price_canvas)
        self.addToolBar(QtCore.Qt.BottomToolBarArea,
                        NavigationToolbar(price_canvas, self))
        self._price_ax = price_canvas.figure.subplots()
        if self.strat_type in ('MACD', 'RSI', 'MA+RSI'):
            self._price_ax2 = self._price_ax.twinx()
        self._format_price_graph()

    def _create_equity_graph(self, section):
        equity_canvas = FigureCanvas(Figure(figsize=(25, 40), facecolor='#404040', dpi=80))
        section.addWidget(equity_canvas)
        self._equity_ax = equity_canvas.figure.subplots()
        self._format_equity_graph()

    def _create_drawdown_graph(self, section):
        drawdown_canvas = FigureCanvas(Figure(figsize=(25, 40), facecolor='#404040', dpi=80))
        section.addWidget(drawdown_canvas)
        self._drawdown_ax = drawdown_canvas.figure.subplots()
        self._format_drawdown_graph()

    def _create_log_box(self, section):
        def _update_text():
            self.print_text.setPlainText(self.log.getvalue())
            self.print_text.moveCursor(QtGui.QTextCursor.End)

        self.print_text = QPlainTextEdit()
        self.print_text.setReadOnly(True)
        self.print_text.setMinimumHeight(80)
        self.print_text.setMinimumWidth(400)
        section.addWidget(self.print_text)
        self.print_timer = QTimer()
        self.print_timer.timeout.connect(_update_text)
        self.print_timer.start(1000)

    def _start_button(self, section):
        self.start_button = QPushButton('Start Backtesting')
        self.start_button.clicked.connect(self._start_bt)
        section.addWidget(self.start_button)

    def _start_bt(self):
        sys.stdout = self.log
        worker = Worker(self.run_func)
        self.threadpool.start(worker)

    def _format_price_graph(self):
        self._price_ax.set_ylabel('price', color='white')
        if self.strat_type == 'MACD':
            self._price_ax2.set_ylabel('MACD', color='white')
            self._price_ax2.tick_params(axis='x', colors='white')
            self._price_ax2.tick_params(axis='y', colors='white', which='both')
        elif self.strat_type == 'RSI':
            self._price_ax2.set_ylabel('RSI', color='white')
            self._price_ax2.tick_params(axis='x', colors='white')
            self._price_ax2.tick_params(axis='y', colors='white', which='both')
        elif self.strat_type == 'MA+RSI':
            self._price_ax2.set_ylabel('RSI', color='white')
            self._price_ax2.tick_params(axis='x', colors='white')
            self._price_ax2.tick_params(axis='y', colors='white', which='both')

        self._price_ax.set_xlabel('date', color='white')
        self._price_ax.tick_params(axis='x', colors='white')
        self._price_ax.tick_params(axis='y', colors='white', which='both')
        self._price_ax.set_facecolor('#404040')

    def _format_equity_graph(self):
        self._equity_ax.set_ylabel('equity', color='white')
        self._equity_ax.set_xlabel('date', color='white')
        self._equity_ax.tick_params(axis='x', colors='white')
        self._equity_ax.tick_params(axis='y', colors='white', which='both')
        self._equity_ax.set_facecolor('#404040')

    def _format_drawdown_graph(self):
        self._drawdown_ax.set_ylabel('drawdown', color='white')
        self._drawdown_ax.set_xlabel('date', color='white')
        self._drawdown_ax.tick_params(axis='x', colors='white')
        self._drawdown_ax.tick_params(axis='y', colors='white', which='both')
        self._drawdown_ax.set_facecolor('#404040')

    def plot_price_graph(self, dates, price, plays, metric1=None, metric2=None, metric3=None):
        self._price_ax.cla()
        self._price_ax.plot(dates, price, linewidth=1, color='#53a8b2', label='Price')
        if self.strat_type in ('MA',):
            self._price_ax.plot(dates, metric1, linewidth=0.8, color='#e9de1c', label='MA')
            self._price_ax.plot(dates, metric2, linewidth=0.8, color='#1ce926', label='MA+std')
            self._price_ax.plot(dates, metric3, linewidth=0.8, color='#e91c1c', label='MA-std')
        elif self.strat_type in ('MACD',):
            self._price_ax2.plot(dates, metric1, linewidth=0.8, color='#e9de1c', label='MACD')
            self._price_ax2.plot(dates, metric2, linewidth=0.8, color='#9d6fff', label='Signal Line')
        elif self.strat_type in ('RSI',):
            # self._price_ax2.plot(dates, metric1, linewidth=0.8, color='#e9de1c', label='RSI')
            self._price_ax2.plot(dates, np.full(len(metric1), 70), 'r--', color='grey', label='70')
            self._price_ax2.plot(dates, np.full(len(metric1), 30), 'r--', color='grey', label='30')
        elif self.strat_type in ('MA+RSI',):
            self._price_ax.plot(dates, metric1, linewidth=0.8, color='#e9de1c', label='MA50')
            self._price_ax.plot(dates, metric2, linewidth=0.8, color='#1ce926', label='MA10')
            self._price_ax2.plot(dates, metric3, linewidth=0.8, color='#7f32a8', label='RSI')

        self._price_ax2.legend()
        self._price_ax.legend()
        for date, price, action, _ in plays:
            self._price_ax.annotate(action, (date, price), color='white',
                                    xycoords='data', xytext=(0, 40),
                                    textcoords='offset points',
                                    arrowprops=dict(arrowstyle="->",
                                                    connectionstyle="arc3",
                                                    color='white', lw=0.5))
        self._price_ax.figure.canvas.draw()

    def plot_equity_graph(self, dates, equity):
        self._equity_ax.cla()
        self._equity_ax.plot(dates, equity, linewidth=1, color='white', label='Equity')
        self._equity_ax.legend()
        self._equity_ax.figure.canvas.draw()

    def plot_drawdown_graph(self, dates, drawdown):
        self._drawdown_ax.cla()
        self._drawdown_ax.plot(dates, drawdown, linewidth=0, color='white', label='Drawdown')
        self._drawdown_ax.legend()
        self._drawdown_ax.fill_between(dates, 0, drawdown, color='red')
        self._drawdown_ax.figure.canvas.draw()


class Worker(QRunnable):

    def __init__(self, func):
        super(Worker, self).__init__()
        self.func = func

    def run(self):
        self.func()
