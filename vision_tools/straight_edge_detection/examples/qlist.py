import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QListWidget, QMainWindow, QListView, QWidget, QGridLayout, QStyle, QPushButton
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import Qt

tree_elements = {'Animals':{1:'Bison',2:'Panther',3:'Elephant'},'Birds':{1:'Duck',2:'Hawk',3:'Pigeon'},
                 'Fish':{1:'Shark',2:'Salmon',3:'Piranha'}}

list_elements = ['test', 'cat', 'dog']
icon_directory = '../icons'
add_icon_fn = 'plus.png'
delete_icon_fn = 'minus.png'
move_up_icon_fn = 'arrow-090.png'
move_down_icon_fn = 'arrow-270.png'
run_step_icon_fn = 'control-stop.png'
run_script_icon_fn = 'control.png'

unconfigured_icon_fn = 'block--pencil.png'
configured_not_ran_icon_fn = 'block.png'
ran_passed_icon = 'block--arrow.png'
ran_failed_icon = 'block--exclamation.png'


class StepListModel(QtCore.QAbstractListModel):
    def __init__(self, step_list=None):
        super().__init__()
        self.step_list = step_list or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            status, text = self.step_list[index.row()]
            return text

        if role == Qt.DecorationRole:
            status, text = self.step_list[index.row()]
            # step is unconfigured
            if status == 0:
                return QIcon(os.path.join(icon_directory, unconfigured_icon_fn))
            # step is configured but not ran
            if status == 1:
                return QIcon(os.path.join(icon_directory, configured_not_ran_icon_fn))
            # step is configured and ran successfully
            if status == 2:
                return QIcon(os.path.join(icon_directory, ran_passed_icon))
            # step is configured and ran but failed
            if status == 3:
                return QIcon(os.path.join(icon_directory, ran_failed_icon))

    def rowCount(self, index):
        return len(self.step_list)


class ProgramList(QWidget):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.setWindowTitle("QTableView Example")
        self.program_list = QListView(objectName='programList')
        self.setWindowTitle("QTableView Example")
        # self.model = QStandardItemModel(self.program_list)
        self.model = StepListModel()
        self.current_index = 0

        # update model with list
        self.load()
        self.program_list.setModel(self.model)
        selection_model = self.program_list.selectionModel()
        selection_model.selectionChanged.connect(self.get_list_index)

        # grid layout settings
        self.layout = QGridLayout()
        self.layout.addWidget(self.program_list, 0, 0, 5, 4)
        self.setLayout(self.layout)

        # buttons
        self.add_step = QPushButton(objectName='add_step')
        self.add_step.setIcon(QIcon(os.path.join(icon_directory, add_icon_fn)))
        self.add_step.clicked.connect(self.add)
        self.layout.addWidget(self.add_step, 0, 4, 1, 1)


        self.delete_step = QPushButton(objectName='delete_step')
        self.delete_step.setIcon(QIcon(os.path.join(icon_directory, delete_icon_fn)))
        self.layout.addWidget(self.delete_step, 1, 4, 1, 1)

        self.move_up = QPushButton(objectName='move_up')
        self.move_up.setIcon(QIcon(os.path.join(icon_directory, move_up_icon_fn)))
        self.layout.addWidget(self.move_up, 2, 4, 1, 1)

        self.move_down = QPushButton(objectName='move_down')
        self.move_down.setIcon(QIcon(os.path.join(icon_directory, move_down_icon_fn)))
        self.layout.addWidget(self.move_down, 3, 4, 1, 1)

        self.run_step = QPushButton(objectName='run_step')
        self.run_step.setIcon(QIcon(os.path.join(icon_directory, run_step_icon_fn)))
        self.layout.addWidget(self.run_step, 4, 4, 1, 1)

        self.run_script = QPushButton(objectName='run_script')
        self.run_script.setIcon(QIcon(os.path.join(icon_directory, run_script_icon_fn)))
        self.layout.addWidget(self.run_script, 5, 4, 1, 1)

    def get_list_index(self):
        indices = self.program_list.selectedIndexes()
        if indices:
            return indices[0].row()
        else:
            return 0

    def add(self):
        """
        Add an item to our to-do list, getting the text from the QLineEdit .todoEdit
        and then clearing it.
        """
        index = self.get_list_index()
        print(self.get_list_index())
        text = 'test-{0}'.format(self.count)
        self.count += 1
        if text:  # Don't add empty strings.
            # Access the list via the model.
            self.model.step_list.insert(index, (False, text))
            # Trigger refresh.
            self.model.layoutChanged.emit()
            # Empty the input
            # self.save()

    def load(self):
        try:
            program_status = []
            for idx, list_element in enumerate(list_elements):
                program_status[idx] = (0, list_element)
            self.model.step_list = program_status
        except Exception:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)

    list_icon = QIcon(QApplication.style().standardIcon(QStyle.SP_ArrowBack))
    window = ProgramList()
    window.show()
    app.exec_()



'''
TODO: http://pharma-sas.com/move-items-up-and-down-in-a-qlistview/
Steal from todo_complete, add status for each item and allow for creation and deletion, add sas up and down logic
'''
