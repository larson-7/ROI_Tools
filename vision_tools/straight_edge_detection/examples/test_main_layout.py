import sys
import os
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QListView, QTreeWidget
from PyQt5.QtGui import QColor, QPalette, QIcon
from QImageViewer import QImageViewer

elements = {'Animals':{1:'Bison',2:'Panther',3:'Elephant'},'Birds':{1:'Duck',2:'Hawk',3:'Pigeon'},
            'Fish':{1:'Shark',2:'Salmon',3:'Piranha'}}
icon_directory = 'images'
icon_filename = 'bug.png'
icon_filepath = os.path.join(icon_directory, icon_filename)

# Placeholder widget for setting up layout
class Color(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


# Creating tab widgets
class MyTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabPosition(QTabWidget.North)
        for n, color in enumerate(['blue', 'purple']):
            self.addTab(Color(color), color)


# tag::model[]
class ProgramListModel(QAbstractListModel):
    def __init__(self):
        QAbstractListModel.__init__(self)
        self.items = []
        self.modelDict = {}

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self.items)):  return QtCore.QVariant()
        if role == Qt.DisplayRole:
            return self.items[index.row()]
        elif role == Qt.DecorationRole:
            return icon


class ListView(QListView):
    def __init__(self):
        super(ListView, self).__init__()
        self.model = ProgramListModel()
        self.model.modelDict = elements
        self.setModel(self.model)


class QListWidget(QWidget):
    def __init__(self):
        super().__init__()
        listview = ListView()
        lay = QVBoxLayout(self)
        lay.addWidget(listview)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        layout = QGridLayout()
        # 1
        listview = QListWidget()
        layout.addWidget(listview, 0, 0, 2, 1)
        # layout.addWidget(Color("red"), 0, 0, 2, 1)
        # 2
        layout.addWidget(Color("yellow"), 2, 0, 3, 1)
        # 3
        self.image = QImageViewer()
        # layout.addWidget(Color("green"), 0, 1, 5, 4)
        layout.addWidget(self.image, 0, 1, 5, 4)
        # 4
        tabs = MyTabWidget()
        layout.addWidget(tabs, 0, 5, 5, 1)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        for column in range(layout.columnCount()):
            layout.setColumnStretch(column, 1)
        for row in range(layout.rowCount()):
            layout.setRowStretch(row, 1)

    def loadImage(self, filepath=''):
        self.image.loadImageFromFile(filepath)

app = QApplication(sys.argv)
window = MainWindow()
wName = "Place Rectangle"
image_dir = 'images'
image_name = 'battery.JPG'
image_filepath = os.path.join(image_dir, image_name)
icon = QIcon(icon_filepath)
window.loadImage(image_filepath)
window.show()
app.exec_()
