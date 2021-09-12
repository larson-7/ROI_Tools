import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QGridLayout
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from QButtons import App

class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Property Sheet - FindLine'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 400
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        mainMenu = self.menuBar()
        editMenu = mainMenu.addMenu('Edit')
        insertMenu = mainMenu.addMenu('Insert')
        helpMenu = mainMenu.addMenu('Help')
        self.statusBar().showMessage('Message in statusbar.')
        exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)

        layout = QGridLayout()

        layout.addWidget(App())
        layout.addWidget(Color('green'), 1, 0)
        layout.addWidget(Color('blue'), 1, 1)
        layout.addWidget(Color('purple'), 2, 1)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.show()

    def update_status_bar(self, message):
        self.statusBar().showMessage(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
