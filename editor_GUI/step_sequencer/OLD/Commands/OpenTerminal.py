import sys
sys.path.append('/step_sequencer/Commands/Command')
from Command import Command, auto


class OpenTerminal(Command):
    type = "open_terminal"

    def __init__(self):
        super.__init__('{"type" : "open_terminal"}')

    def execute(self, commands, commands_counter):
        auto.hotkey('altright', 'ctrlright', 't')

    def is_valid(self):
        return True
