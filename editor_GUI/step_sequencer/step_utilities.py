from .step import Step
from .load_image_from_file import LoadImageFromFile
import importlib.util
import os
import inspect
from collections import defaultdict

def discover_steps():
    # blank dictionary of all possible command references
    command_references = defaultdict(list)
    path = os.path.dirname(os.path.realpath(__file__))
    files = os.listdir(path)
    path_dot = path.replace("/", ".")
    path_dot = path_dot.strip('.')

    # get list of all .py files in directory except this script
    command_filenames = [x for x in files if x.endswith('.py') and x != os.path.basename(__file__) and x !=
                         '__init__.py']
    # bring the Command.py to the front of the list to be loaded in first
    command_filenames.insert(0, command_filenames.pop(command_filenames.index('step.py')))
    for cmd_file in command_filenames:
        # get rid of extension
        command_name = os.path.splitext(cmd_file)[0]
        # Original implementation
        module = importlib.import_module('.{0}'.format(command_name), 'step_sequencer')
        # iterate over attributes of each module and add classes only
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if inspect.isclass(attribute):
                try:
                    # try to get its type, in order to add it to the dictionary for instant access
                    command_type = getattr(attribute, 'type')
                    command_references[command_type].append(attribute)
                except AttributeError:
                    # class has no type, ignore it, since Command class has no type.
                    pass
    return dict(command_references)


if __name__ == "__main__":
    print(discover_steps())
