import sys
import os
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QListView, QTreeWidget
from QImageViewer import QImageViewer
from qlist import ProgramList
from qtree import ProgramTreeItems
from qtab import ProgramConfigTabs
from step_sequencer.step_utilities import discover_steps

# Load all available classes
available_steps = discover_steps()
print(available_steps)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vision Test")

        # step input/output configuration
        tabs = ProgramConfigTabs(available_steps)
        # image viewer
        self.image_view = QImageViewer()
        # active program list
        listview = ProgramList(tabs, available_steps, self.image_view)
        # available steps
        program_tree = ProgramTreeItems(listview, available_steps)

        # Grid layout
        layout = QGridLayout()
        # 1
        layout.addWidget(listview, 0, 0, 2, 2)
        # 2
        layout.addWidget(program_tree, 2, 0, 3, 2)
        # 3
        layout.addWidget(self.image_view, 0, 2, 5, 4)
        # 4
        layout.addWidget(tabs, 0, 6, 5, 1)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        for column in range(layout.columnCount()):
            layout.setColumnStretch(column, 1)
        for row in range(layout.rowCount()):
            layout.setRowStretch(row, 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    wName = "Place Rectangle"
    image_dir = 'images'
    image_name = 'battery.JPG'
    image_filepath = os.path.join(image_dir, image_name)
    # window.loadImage(image_filepath)
    window.show()
    app.exec_()
