from PyQt5.QtWidgets import QWidget, QTabWidget
from PyQt5.QtGui import QColor, QPalette
from editor_GUI.step_sequencer.step import Step


# Placeholder widget for setting up layout
class Color(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


# Creating tab widgets
class ProgramConfigTabs(QTabWidget):
    def __init__(self, available_classes, step=Step()):
        super().__init__()
        self.step = step
        self.blank_step = step
        self.setTabPosition(QTabWidget.North)
        self.available_classes = available_classes
        self.addTab(self.step.display_inputs(), 'Inputs')
        self.addTab(self.step.display_outputs(), 'Outputs')

    def update_tabs(self):
        self.removeTab(0)
        self.addTab(self.step.display_inputs(), 'Inputs')
        self.removeTab(0)
        self.addTab(self.step.display_outputs(), 'Outputs')
