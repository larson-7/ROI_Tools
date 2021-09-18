import sys
import importlib.util
import os
import sys
import inspect
abs_path = os.path.abspath(__file__)

def load_classes():
    # blank dictionary of all possible command references
    command_references = {}
    path = os.path.dirname(os.path.realpath(__file__))
    files = os.listdir(path)
    print(path)
    path_dot = path.replace("/", ".")
    path_dot = path_dot.strip('.')

    # get list of all .py files in directory except this script
    command_filenames = [x for x in files if x.endswith('.py') and x != os.path.basename(__file__) and x !=
                         '__init__.py']
    # bring the Command.py to the front of the list to be loaded in first
    command_filenames.insert(0, command_filenames.pop(command_filenames.index('Command.py')))
    for cmd_file in command_filenames:
        # get rid of extension
        command_name = os.path.splitext(cmd_file)[0]

        # Original implementation
        # module = importlib.import_module('Commands.{0}'.format(command_name))
        # module = importlib.import_module(command_name)

        # This was my workaround here for this method
        spec = importlib.util.spec_from_file_location(command_name, path + '/' + command_name + '.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # iterate over attributes of each module and add classes only
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if inspect.isclass(attribute):
                try:
                    # try to get its type, in order to add it to the dictionary for instant access
                    command_type = getattr(attribute, 'type')
                    command_references[command_type] = attribute
                except AttributeError:
                    # class has no type, ignore it, since Command class has no type.
                    pass
    return command_references


def parse(data, command_references):

    # list of all commands to run
    command_list = []

    # iterate through list of commands given from main
    for command in data:
        try:
            command_type = command["type"]
        except KeyError:
            print("Backend: Error: command type is not found in json item:\n ", command)
            sys.exit(1)

        # search through list of commands to instantiate object
        try:
            constructor = command_references[command_type]
            command_list.append(constructor(command))
        except KeyError:
            print( "Backend : Error: command type '{0}' has no implementation yet."
                   " perhaps there's a typo in type name".format(command_type))
            pass

    return command_list


if __name__ == '__main__':
    print(load_classes())
