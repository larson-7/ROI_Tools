# import the necessary packages
import sys
sys.path.append('/step_sequencer/Commands/Command')
from Command import Command, auto
import cv2
import pytesseract
import numpy as np
import sys

class DetectText(Command):
    type = "detect_text"
    pytesseract.pytesseract.tesseract_cmd = '/usr/local/Cellar/tesseract/4.1.1/bin/tesseract'

    def __init__(self, json):
        super().__init__(json)

        self.text_to_find = ''

        # required parameters
        try:
            self.region = tuple(json["search_region"])
        except KeyError:
            print("Backend: Error: missing 'search_region' parameter, closing application...")
            sys.exit(1)

        # try optional parameter(s)
        try:
            self.text_to_find = json["text_to_find"]
        except KeyError:
            print("Backend: Error: missing 'text_to_find' parameter, will find any text in region")


    def execute(self, commands, commands_counter):
        # take screenshot
        img = cv2.cvtColor(np.array(auto.screenshot(region=self.region)), cv2.COLOR_BGR2GRAY)
        # scale to 300 dpi from 220 rmpb 15"
        dpi_scale = 300 / 220
        new_img = cv2.resize(img, (0, 0), fx=dpi_scale, fy=dpi_scale)
        kernel = np.ones((1, 1), np.uint8)
        new_img = cv2.dilate(new_img, kernel, iterations=1)
        new_img = cv2.erode(new_img, kernel, iterations=1)
        new_img = cv2.threshold(cv2.bilateralFilter(new_img, 5, 75, 75), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        # apply thresholding
        # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # lower = np.array([0, 0, 120])
        # upper = np.array([157, 54, 255])
        # lower = np.array([0, 0, 218])
        # upper = np.array([157, 54, 255])
        # mask = cv2.inRange(hsv, lower, upper)

        # Create horizontal kernel and dilate to connect text characters
        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
        # dilate = cv2.dilate(img, kernel, iterations=5)

        # Bitwise dilated image with mask, invert, then OCR
        # result = 255 - cv2.bitwise_and(dilate, img)

        data = pytesseract.image_to_string(new_img, lang='eng', config='--psm 6')
        print('Detection text: {}'.format(data))

    def is_valid(self):
        return isinstance(self.region, tuple) and len(self.region) == 4

    def print(self):
        return ""
