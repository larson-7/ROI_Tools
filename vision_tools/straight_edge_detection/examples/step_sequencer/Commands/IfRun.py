import sys
sys.path.append('/step_sequencer/Commands/Command')
from Command import Command, auto
from Routine import Routine
import json

class IfJump(Command):
    type = "if_run"

    def __init__(self, json):
        super().__init__(json)
        try:
            self.result = json["result"]
            self.operator = json["operator"]
            self.result_value = json["result_value"]
            self.step_name = json["sub_routine"]
        except KeyError:
            print("Backend: Error: 'key' parameter is not found in:\n ", json)
            sys.exit(1)

    def execute(self, commands, commands_counter):
        result_found = False
        # big switch statement for logical operator and logic check
        for command in commands:
            command_to_find = self.result.split(".")

            if command.name == command_to_find[0]:
                compare = getattr(command, command_to_find[1])
                if self.operator == '==' or self.operator == '=':
                    status = compare == self.result_value
                elif self.operator == '>':
                    status = compare > self.result_value
                elif self.operator == '>=':
                    status = compare >= self.result_value
                elif self.operator == '<':
                    status = compare < self.result_value
                elif self.operator == '<=':
                    status = compare < self.result_value
                elif self.operator == '!=':
                    status = compare != self.result_value
                else:
                    print("in {0}: invalid operator:{1}".format(self.name, self.operator))
                result_found = True
                break

        if result_found:
            proceed = status
            # if logic passes, run desired sub routine
            if proceed:
                json_file = {'type':"routine", 'file': self.step_name}

                new_routine = Routine(json_file)
                new_routine.execute(commands, commands_counter)
            else:
                # failed to find the correct named object
                print("Object with name {0} not found from step {1}".format(command_to_find[0], command_to_find[1]))
        else:
            print("result not found with result name : {0} and attribute {1}".format(self.result_name, self.result_value))

    def is_valid(self):
        return isinstance(self.result, str) and isinstance(self.operator, str)\
               and isinstance(self.step_name, str)
