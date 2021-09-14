import sys
import os
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QListView, QTreeWidget
from PyQt5.QtGui import QColor, QPalette, QIcon
from QImageViewer import QImageViewer

class Color(QWidget):
    def __init__(self, list_items):
        super().__init__()
        layout = QGridLayout()
        list = QListView()
        layout.addWidget(listview, 0, 0, 2, 1)

