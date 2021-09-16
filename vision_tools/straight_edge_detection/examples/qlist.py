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

UNCONFIGURED = 0
CONFIGURED = 1
RAN_SUCCESS = 2
RAN_FAILED = 3

class Step:
    def __init__(self, status=0, text=''):
        self.status = status
        self.text = text


class StepListModel(QtCore.QAbstractListModel):
    def __init__(self, step_list=None):
        super().__init__()
        self.step_list = step_list or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.step_list[index.row()].text
            return text

        if role == Qt.DecorationRole:
            status = self.step_list[index.row()].status
            # step is unconfigured
            if status == UNCONFIGURED:
                return QIcon(os.path.join(icon_directory, unconfigured_icon_fn))
            # step is configured but not ran
            if status == CONFIGURED:
                return QIcon(os.path.join(icon_directory, configured_not_ran_icon_fn))
            # step is configured and ran successfully
            if status == RAN_SUCCESS:
                return QIcon(os.path.join(icon_directory, ran_passed_icon))
            # step is configured and ran but failed
            if status == RAN_FAILED:
                return QIcon(os.path.join(icon_directory, ran_failed_icon))

    def run(self, index):
        self.step_list[index].status = 2

    def reset(self, index):
        self.step_list[index].status = 0

    def status (self, index):
        if 0 <= index <= self.rowCount() - 1:
            return self.step_list[index].status
        else:
            return -1

    def rowCount(self, index=0):
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
        # selection_model.selectionChanged.connect(self.get_list_index)

        # self.program_list.clicked[QtCore.QModelIndex].connect(self.on_clicked)
        # When you receive the signal, you call QtGui.QStandardItemModel.itemFromIndex()
        # on the given model index to get a pointer to the item

        # grid layout settings
        self.layout = QGridLayout()
        self.layout.addWidget(self.program_list, 0, 0, 10, 10)
        self.setLayout(self.layout)

        # buttons
        self.add_step = QPushButton(objectName='add_step')
        self.add_step.setIcon(QIcon(os.path.join(icon_directory, add_icon_fn)))
        self.add_step.clicked.connect(self.add)
        self.layout.addWidget(self.add_step, 0, 10, 1, 1)

        self.delete_step = QPushButton(objectName='delete_step')
        self.delete_step.setIcon(QIcon(os.path.join(icon_directory, delete_icon_fn)))
        self.delete_step.clicked.connect(self.delete)
        self.layout.addWidget(self.delete_step, 1, 10, 1, 1)

        self.move_up = QPushButton(objectName='move_up')
        self.move_up.setIcon(QIcon(os.path.join(icon_directory, move_up_icon_fn)))
        self.move_up.clicked.connect(self.moveUp)
        self.layout.addWidget(self.move_up, 2, 10, 1, 1)

        self.move_down = QPushButton(objectName='move_down')
        self.move_down.setIcon(QIcon(os.path.join(icon_directory, move_down_icon_fn)))
        self.move_down.clicked.connect(self.moveDown)
        self.layout.addWidget(self.move_down, 3, 10, 1, 1)

        self.run_step = QPushButton(objectName='run_step')
        self.run_step.setIcon(QIcon(os.path.join(icon_directory, run_step_icon_fn)))
        self.run_step.clicked.connect(self.runStep)
        self.layout.addWidget(self.run_step, 4, 10, 1, 1)

        self.run_script = QPushButton(objectName='run_script')
        self.run_script.setIcon(QIcon(os.path.join(icon_directory, run_script_icon_fn)))
        self.run_script.clicked.connect(self.runScript)
        self.layout.addWidget(self.run_script, 5, 10, 1, 1)
    # https://doc.qt.io/archives/qt-4.8/qabstractitemview.html#clearSelection

    def add(self):
        """
        Add an item to our to-do list, getting the text from the QLineEdit .todoEdit
        and then clearing it.
        """
        index = self.program_list.currentIndex().row()
        text = 'test-{0}'.format(self.count)
        self.count += 1
        if text:  # Don't add empty strings.
            num_itmes = self.model.rowCount()
            if index == -1:
                if num_itmes > 0:
                    index = num_itmes + 1
                else:
                    index = 0
            else:
                index += 1

            self.model.step_list.insert(index, Step(0, text))
            # Trigger refresh.
            self.model.layoutChanged.emit()

            # Focus on new item added
            item = self.model.index(index)
            self.program_list.setCurrentIndex(item)

            # self.save()

    def delete(self):
        index = self.program_list.currentIndex().row()
        if index >= 0:
            # Remove the item and refresh.
            del self.model.step_list[index]
            self.model.layoutChanged.emit()
            # Clear the selection (as it is no longer valid).
            self.program_list.clearSelection()
            if index > 0:
                index -= 1
            item = self.model.index(index)
            self.program_list.setCurrentIndex(item)
            # self.save()

    def moveUp(self):
        index = self.program_list.currentIndex().row()
        if index > 0:
            self.model.step_list.insert(index - 1, self.model.step_list.pop(index))
            self.model.layoutChanged.emit()
            item = self.model.index(index - 1)
            self.program_list.setCurrentIndex(item)

    def moveDown(self):
        index = self.program_list.currentIndex().row()
        if index < self.model.rowCount() - 1:
            self.model.step_list.insert(index + 1, self.model.step_list.pop(index))
            self.model.layoutChanged.emit()
            item = self.model.index(index + 1)
            self.program_list.setCurrentIndex(item)

    def runStep(self):
        index = self.program_list.currentIndex().row()
        if 0 <= index <= self.model.rowCount() - 1:
            self.model.run(index)
            self.model.layoutChanged.emit()
            if index == self.model.rowCount() - 1 and self.model.status(index) == RAN_SUCCESS:
                index = 0
                for idx, step in enumerate(self.model.step_list):
                    self.model.reset(idx)
            else:
                index += 1

            item = self.model.index(index)
            self.program_list.setCurrentIndex(item)

    def runScript(self):
        # reset step_sequencer
        for idx, step in enumerate(self.model.step_list):
            self.model.reset(idx)
        # set index to zero and run all of the step_sequencer
        item = self.model.index(0)
        self.program_list.setCurrentIndex(item)
        end_index = self.model.rowCount()
        for index in range(end_index):
            self.model.run(index)
            self.model.layoutChanged.emit()
        item = self.model.index(end_index - 1)
        self.program_list.setCurrentIndex(item)

    def load(self):
        try:
            program_status = []
            for idx, list_element in enumerate(list_elements):
                program_status[idx] = Step(0, list_element)
            self.model.step_list = program_status
        except Exception:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProgramList()
    window.show()
    app.exec_()
