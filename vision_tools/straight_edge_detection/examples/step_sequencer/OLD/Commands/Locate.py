import sys
sys.path.append('/step_sequencer/Commands/Command')
from Command import Command, auto
import os
import cv2
import random


class Locate(Command):
    type = "locate"

    def __init__(self, json):
        super().__init__(json)
        self.template_position = [0,0]
        self.valid_result = False

        # required parameters
        try:
            self.template_path = json["template_path"]
        except KeyError:
            print("Backend: Error: template path is not found in:\n ", self.name)
            sys.exit(1)
        try:
            self.retries = json["retries"]
        except KeyError:
            self.retries = 1
        try:
            self.exit = json["exit"]
        except KeyError:
            self.exit = True

    def execute(self, commands, commands_counter):
        retry_count = 0
        self.valid_result = False
        while not self.valid_result and retry_count < self.retries:
            try:
                self.template_position = auto.locateCenterOnScreen(self.template_path, confidence=0.9)
                if self.template_position is not None:
                    self.valid_result = True
                    self.template_position = [item / 2 for item in self.template_position]
                    print('template found @ : {}'.format(self.template_position))
                else:
                    # print('{}: template match not found'.format(self.name))
                    retry_count += 1
                    auto.sleep(random.randint(1,3))
                    if (self.retries == 0 or retry_count >= self.retries) and self.exit:
                        sys.exit(1)
                    else:
                        print('retry count: {0} of {1}'.format(retry_count, self.retries))

            except auto.ImageNotFoundException:
                print('template image: {} not found'.format(os.path.split(self.template_path)[1]))
                break

    def is_valid(self):
        try:
            open(self.template_path, 'r')
            return True
        except IOError:
            print('Invalid Path: {}'.format(self.template_path))
            return False

