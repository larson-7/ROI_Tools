import sys
sys.path.append('/step_sequencer/Commands/Command')
from datetime import time
import random
from Command import Command, auto


class Sleep(Command):
    type = "sleep"

    def __init__(self, json):
        super().__init__(json)
        try:
            self.duration = json["duration"]
        except KeyError:
            print("Backend: Error: duration parameter is not found in:\n ", json)
            sys.exit(1)

    def execute(self, commands, commands_counter):

        if self.duration < 1:
            auto.sleep(random.random())
        else:
            auto.sleep(random.uniform(self.duration - 1, self.duration + 1))

    def is_valid(self):
        return isinstance(self.duration, float) or isinstance(self.duration, int)
