import sys
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QTreeView, QWidget, QVBoxLayout
from PyQt5 import QtCore
from PyQt5.QtGui import QStandardItemModel

class FindLineInputs(QWidget):
    def __init__(self, find_line):
        super().__init__()
        self.find_line = find_line

        self.tree = QTreeView(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Name', 'Height', 'Weight'])
        self.tree.header().setDefaultSectionSize(180)
        self.tree.setModel(self.model)
        self.importData(data)
        self.tree.expandAll()