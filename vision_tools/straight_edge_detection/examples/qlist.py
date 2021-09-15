import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QListWidget, QMainWindow, QListView, QWidget,QGridLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem

tree_elements = {'Animals':{1:'Bison',2:'Panther',3:'Elephant'},'Birds':{1:'Duck',2:'Hawk',3:'Pigeon'},
                 'Fish':{1:'Shark',2:'Salmon',3:'Piranha'}}

list_elements = ['test', 'cat', 'dog']
icon_directory = 'images'
icon_filename = 'bug.png'
icon_filepath = os.path.join(icon_directory, icon_filename)


list_icon = QtGui.QImage("bug.png")
print(list_icon)

class ProgramList(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTableView Example")
        self.program_list = QListView()
        self.setWindowTitle("QTableView Example")
        self.model = QStandardItemModel(self.program_list)

        for list_element in list_elements:
            item = QStandardItem(list_element)
            self.model.appendRow(item)
        self.program_list.setModel(list_icon, self.model)

        self.layout = QGridLayout()
        self.layout.addWidget(self.program_list, 0, 0)
        self.setLayout(self.layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProgramList()
    window.show()
    app.exec_()



'''
TODO: http://pharma-sas.com/move-items-up-and-down-in-a-qlistview/
Steal from todo_complete, add status for each item and allow for creation and deletion, add sas up and down logic
'''
