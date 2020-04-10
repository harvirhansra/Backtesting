import sys
import time

from PyQt5.QtCore import QTimer, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit

class BacktestingGUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self._main = QWidget()
        self.setCentralWidget(self._main)
        self.layout = QVBoxLayout(self._main)

        self._create_log_box()
        

    def _create_log_box(self):
        self.num = '1'
        self.print_text = QTextEdit()
        self.print_text.setReadOnly(True)
        self.layout.addWidget(self.print_text)
        self.print_timer = QTimer()
        self.print_timer.timeout.connect(self._update_text)
        self.print_timer.start(10)

    def _update_text(self):
        old = int(self.num)
        new = str(old+1)
        self.num = new
        self.print_text.append(new)

if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    app = BacktestingGUI()
    app.show()

    qapp.exec_()
    