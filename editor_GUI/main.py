import sys
import os
from PyQt5.QtWidgets import QApplication, QGridLayout, QMainWindow, QWidget
from editor_GUI.widgets.QImageViewer import QImageViewer
from editor_GUI.widgets.program_list import ProgramList
from editor_GUI.widgets.available_program_tree import ProgramTreeItems
from editor_GUI.widgets.step_config_tabs import ProgramConfigTabs
from editor_GUI.step_sequencer.step_utilities import discover_steps

# Load all available classes
available_steps = discover_steps()
print(available_steps)
#TODO: Check all inputs anytime a value has changed and call isvalid routine
#TODO: Disallow the running of not valid steps
#TODO: Sniff out memory leak on run step with memory-profiler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vision Test")

        # step input/output configuration
        tabs = ProgramConfigTabs(available_steps)
        # image viewer
        self.image_view = QImageViewer()
        self.image_view.setMinimumSize(1080, 1080)
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
    image_dir = 'examples/images'
    image_name = 'battery.JPG'
    image_filepath = os.path.join(image_dir, image_name)
    # window.loadImage(image_filepath)
    window.show()
    app.exec_()
