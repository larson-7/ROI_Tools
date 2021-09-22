import sys
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel,QGridLayout

class Step:

    # list to create track of all instantiated objects
    instances = []
    instance_count = 0

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
