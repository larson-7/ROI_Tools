import sys
sys.path.append('/step_sequencer/Commands/Command')
import cv2
import numpy as np
import random

from Command import Command, auto


class LocateCv(Command):
    type = "locate_cv"

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


    def get_midpoint(self, start_point, end_point):
        if type(start_point) or type(end_point) != 'numpy.ndarray':
            start_point = np.array(start_point)
            end_point = np.array(end_point)
        return (start_point + end_point) / 2


    def return_data(self):
        #return useful data
        return self.template_position


    def execute(self, commands, commands_counter):
        assert(self.template_path != "")
        # Load Temp Image
        template = cv2.imread(self.template_path).astype(np.float32)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)

        # static window location, TODO: change this to a object detection
        screen_loc = (5, 28, 770 * 2, 556 * 2)
        retry_count = 0
        while not self.valid_result and retry_count < self.retries:
            # take screenshot
            image = np.array(auto.screenshot(region=screen_loc))
            # convert to grayscale
            image_gray = cv2.cvtColor(np.float32(image), cv2.COLOR_BGR2RGB)

            # Perform match operations.
            result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            (min_val, max_val, min_loc, max_loc) = cv2.minMaxLoc(result)
            threshold = 0.8

            self.valid_result = False
            if max_val > threshold:
                self.valid_result = True

                # determine the starting and ending (x, y)-coordinates of the
                # bounding box
                (startX, startY) = max_loc
                endX = startX + template.shape[1]
                endY = startY + template.shape[0]
                self.template_position = self.get_midpoint((startX, startY), (endX, endY))/2
                print("template_position: {}".format(self.template_position))

            else:
                print('{}: template match not found'.format(self.name))
                retry_count += 1
                auto.sleep(random.randint(1, 3))
                if (self.retries == 0 or retry_count >= self.retries) and self.exit:
                    sys.exit(1)
                else:
                    print('retry count: {0} of {1}'.format(retry_count, self.retries))

        # return current index and whether the detection was found
        return self.valid_result

    def is_valid(self):
        return True

