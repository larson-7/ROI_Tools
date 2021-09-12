import sys
from PyQt5 import QtCore, QtGui

class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)

        self.win_widget = WinWidget(self)
        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(widget)
        layout.addWidget(self.win_widget)

        self.setCentralWidget(widget)
        self.statusBar().showMessage('Ready')
        self.toolbar = self.addToolBar('Exit')

        exitAction = QtGui.QAction ('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(QtGui.qApp.quit)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')

        self.setGeometry(300, 300, 450, 250)
        self.setWindowTitle('Test')
        self.setWindowIcon (QtGui.QIcon('logo.png'))
        self.show()

    class WinWidget (QtGui.QWidget) :

    def __init__(self, parent):
        super (WinWidget , self).__init__(parent)
        self.controls()
        #self.__layout()

    def controls(self):

        self.qbtn = QtGui.QPushButton('Quit', self)
        self.qbtn.setFixedSize (100,25)
        self.qbtn.setToolTip ("quit")
        self.qbtn.clicked.connect(QtCore.QCoreApplication.instance().quit)
        self.qbtn.move(50, 50)

def main():
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
