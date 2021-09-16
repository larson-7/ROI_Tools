import sys
import json
from Command import Command
import CommandsParser as parser


class Routine(Command):
    type = "routine"

    def __init__(self, json_file):
        super().__init__(json_file)
        try:
            self.commands = json_file["commands"]
            self.commands = json_file.loads(self.commands)
        except KeyError:
            try:
                self.file = json_file["file"]
                with open(self.file) as json_file:
                    if json_file is None:
                        print("cannot find provided json file.")
                        sys.exit(1)
                    self.commands = json.load(json_file)
            except KeyError:
                print("Backend: Error: the routine's commands are missing, please provide them "
                      "through commands or file argument. "
                      "in:\n ", json_file)
                sys.exit(1)
        self.routine_commands = parser.parse(self.commands, parser.load_classes())

        # validate commands before any execution, this may reduce runtime unexpected behavior.
        valid = True
        for command in self.routine_commands:
            if not command.is_valid():
                valid = False
                print("the following command is not valid: ", command.print())

        # exit only if at least one command is not valid and after checking all commands and gave
        # feedback to user
        if not valid:
            sys.exit(0)

    def execute(self, commands, commands_counter):
        for command in self.routine_commands:
            command.execute(self.routine_commands, commands_counter)

    def is_valid(self):
        all_valid = True
        for command in self.routine_commands:
            if not command.is_valid():
                all_valid = False
                print("the following sub-command is not valid: ", command.print())
        return all_valid
