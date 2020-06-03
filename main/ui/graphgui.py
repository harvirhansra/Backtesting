import io
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import QRunnable, QThreadPool, QTimer
from PyQt5.QtWidgets import QPushButton, QPlainTextEdit
from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)


class BacktestingGUI(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
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
        # self._create_std_graph()
        self._create_equity_graph(self.middle)
        # self._create_drawdown_graph(self.middle)
        self._create_log_box(self.bottom)
        self._start_button(self.bottom)

        self.threadpool = QThreadPool()
        # self.threadpool.setMaxThreadCount(2)

    def _create_price_graph(self, section):
        price_canvas = FigureCanvas(Figure(figsize=(25, 40), facecolor='#404040', dpi=80))
        section.addWidget(price_canvas)
        self.addToolBar(QtCore.Qt.BottomToolBarArea,
                        NavigationToolbar(price_canvas, self))
        self._price_ax = price_canvas.figure.subplots()
        # self._price2_ax = self._price_ax.twinx()
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

    def _create_std_graph(self, section):
        std_canvas = FigureCanvas(Figure(figsize=(5, 8), facecolor='#404040'))
        section.addWidget(std_canvas)
        self._std_ax = std_canvas.figure.subplots()
        self._format_std_graph()

    def _create_log_box(self, section):
        def _update_text():
            self.print_text.setPlainText(self.log.getvalue())
            self.print_text.moveCursor(QtGui.QTextCursor.End)

        self.print_text = QPlainTextEdit()
        self.print_text.setReadOnly(True)
        self.print_text.setMinimumHeight(80)
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
        # self._price2_ax.set_ylabel('std', color='white')
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

    def _format_std_graph(self):
        self._std_ax.set_ylabel('std', color='white')
        self._std_ax.set_xlabel('date', color='white')
        self._std_ax.tick_params(axis='x', colors='white')
        self._std_ax.tick_params(axis='y', colors='white')
        self._std_ax.set_facecolor('#404040')

    def plot_price_graph(self, dates, price, plays, metric1, metric2):
        self._price_ax.cla()
        self._price_ax.plot(dates, price, linewidth=1.5, color='#53a8b2')
        self._price_ax.plot(dates, metric1, linewidth=0.8, color='#e9de1c')
        self._price_ax.plot(dates, metric2, linewidth=0.8, color='#1ce926')
        # self._price_ax.plot(dates, metric3, linewidth=0.8, color='#e91c1c')
        # self._price2_ax.plot(res.date, res.metric4, linewidth=0.5, color='#ffbdd8')
        for date, price, action in plays:
            self._price_ax.annotate(action, (date, price), color='white',
                                    xycoords='data', xytext=(0, 40),
                                    textcoords='offset points',
                                    arrowprops=dict(arrowstyle="->",
                                                    connectionstyle="arc3",
                                                    color='white', lw=0.5))
        self._price_ax.figure.canvas.draw()

    def plot_equity_graph(self, dates, equity):
        self._equity_ax.cla()
        self._equity_ax.plot(dates, equity, linewidth=1.5, color='white')
        self._equity_ax.figure.canvas.draw()
    
    def plot_drawdown_graph(self, dates, drawdown):
        self._drawdown_ax.cla()
        self._drawdown_ax.plot(dates, drawdown, linewidth=1.5, color='white')
        self._drawdown_ax.figure.canvas.draw()

    def _plot_std_graph(self, res):
        self._std_ax.clear()
        self._std_ax.plot(res.date, res.metric4, linewidth=1.5, color='#53a8b2')


class Worker(QRunnable):

    def __init__(self, func):
        super(Worker, self).__init__()
        self.func = func
        
    def run(self):
        self.func()
