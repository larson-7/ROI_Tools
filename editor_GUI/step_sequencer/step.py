import sys
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel,QGridLayout
import numpy as np

UNCONFIGURED = 0
CONFIGURED = 1
RAN_SUCCESS = 2
RAN_FAILED = 3

class Step:
    name = 'Default Step'
    # list to create track of all instantiated objects
    instances = []
    instance_count = 0
    height = 1920
    width = 1080
    display_image = np.ones((height, width), dtype=np.uint8)
    images = []
    for i in range(5):
        images.append(display_image.copy())
    # images = [display_image.copy() for x in range(5)]

    def __init__(self, json=None):

        if json:
            self.json = json
            # append instance of class
            Step.instances.append(json['type'])
            try:
                self.name = json['name']
            except KeyError:
                # tally up count of instances of said object
                for instance in self.instances:
                    if instance == json['type']:
                        self.instance_count += 1
                # name command with generic command name + instance count
                self.name = json['type'] + str(self.instance_count)

        self.status = UNCONFIGURED
        self.input_image_index = 0
        self.output_image_index = 0

    def execute(self, commands, counter):
        pass

    def print(self):
        return self.json

    def is_valid(self):
        pass

    def inputs(self):
        pass

    def outputs(self):
        pass

    def display_outputs(self):
        display = QWidget()
        label = QLabel('No Outputs')

        # grid layout settings
        layout = QGridLayout()
        layout.addWidget(label, 0, 0, 1, 1)
        display.setLayout(layout)
        return display

    def display_inputs(self):
        display = QWidget()
        label = QLabel('No Inputs')

        # grid layout settings
        layout = QGridLayout()
        layout.addWidget(label, 0, 0, 1, 1)
        display.setLayout(layout)
        return display
