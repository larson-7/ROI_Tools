import sys
sys.path.append('/step_sequencer/Commands/Command')
from Command import Command, auto

class LeftClick(Command):
    type = "left_click"

    def __init__(self, json):
        super().__init__(json)

    def execute(self, commands, commands_counter):
        auto.leftClick()

        # return current index
        return commands_counter, True

    def is_valid(self):
        return True





