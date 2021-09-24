from .step import Step
import cv2
import numpy as np
import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QTextEdit, QFileDialog, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore

UNCONFIGURED = 0
CONFIGURED = 1
RAN_SUCCESS = 2
RAN_FAILED = 3

class TextEdit(QTextEdit):
    clicked = pyqtSignal()
    changed = pyqtSignal()

    def __init__(self, step_object):
        super().__init__()
        self.clicked.connect(self.mouseReleaseEvent)
        self.changed.connect(self.file_browser)
        self.step_object = step_object

    def file_browser(self):
        file_types = "Image Files (*.jpeg *.jpg *.png)"
        file_browser = QFileDialog()
        file_name = file_browser.getOpenFileName(self, 'Open Image File', r"<Default dir>", file_types)
        return file_name[0]


    def mouseReleaseEvent(self, event):
        dialog_filepath = self.file_browser()
        if dialog_filepath != '':
            self.setText(dialog_filepath)
            self.step_object.filepath = dialog_filepath

    def textChanged(self):
        return self.toPlainText()


class LoadImageFromFile(Step):
    name = "Load Image From File"
    type = "Image Acquisition"
    filepath_parameter = "image_filepath"

    def __init__(self, json=None):
        super().__init__(json)
        # maybe not needed now
        self.image = None
        self.status = 0

        # required parameters
        try:
            self.filepath = json[self.filepath_parameter]
        except (KeyError, TypeError):
            self.filepath = None
            print("Backend: Warning: missing '{}' parameter".format(self.filepath_parameter))

    def execute(self, commands=None, counter=None):
        try:
            self.image = cv2.imread(self.filepath)
            self.status = RAN_SUCCESS
        except (FileExistsError, FileNotFoundError):
            self.status = RAN_FAILED

    def print(self):
        if self.image:
            h, w, bpp = np.shape(self.image)
            # print image properties.
            print('image properties - Width:{0}, Height:{1}'.format(h, w))

    def is_valid(self):
        print('filepath ', self.filepath)
        if self.filepath:
            # Split the extension from the path and normalise it to lowercase.
            ext = os.path.splitext(self.filepath)[-1].lower()
            if ext == ".png" or ext == ".jpg":
                self.status = CONFIGURED
                return True
            else:
                self.status = UNCONFIGURED
                return False
        else:
            self.status = UNCONFIGURED
            return False

    def display_inputs(self):
        input_widget = QWidget()
        file_path = TextEdit(self)
        file_path.setWindowTitle("Image Filepath")
        file_path.selectionChanged.connect(self.is_valid)
        if self.filepath:
            file_path.setText(self.filepath)
        # grid layout settings
        # layout = QGridLayout()
        layout = QVBoxLayout()
        layout.addWidget(QLabel('File Path'))
        layout.addWidget(file_path)
        input_widget.setLayout(layout)

        return input_widget


if __name__ == "__main__":
    app = QApplication(sys.argv)
    step = LoadImageFromFile()
    window = step.display_inputs()
    window.show()
    app.exec_()
