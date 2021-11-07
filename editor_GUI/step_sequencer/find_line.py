import sys

import numpy as np
from typing import get_type_hints
import os
import time
import cv2
from classes.point import Point
from classes.points import Points
from classes.line import Line
from classes.rectangle import Rectangle, RectAttributes
from classes.roi_rectangle import ROIRectangle
from editor_GUI.ROIs.rotated_rect_crop import inside_rect, rect_bbx, crop_rotated_rectangle
import enum
from skimage.draw import line as sciline
from .step import Step

UNCONFIGURED = 0
CONFIGURED = 1
RAN_SUCCESS = 2
RAN_FAILED = 3

class LineSettings(enum.Enum):
    bestScore = 0
    firstEdge = 1
    lastEdge = 2

class EdgeSettings(enum.Enum):
    either = 0
    blackToWhite = 1
    whiteToBlack = 2

class DisplaySettings(enum.Enum):
    hideAll = 0
    resultGraphicOnly = 1
    showAll = 2


class FindLine(Step):
    type = "Edge Detection"
    name = "Find Line"

    def __init__(self, json=None):
        super().__init__(json)
        self.image = None
        self.scale_factor = 0.025
        self.roi_rect = None
        self.np_lines = None
        self.found_line = None

        # Line Find Settings
        self.angle_threshold = 0
        self.edge_setting = EdgeSettings.blackToWhite
        self.line_setting = LineSettings.lastEdge

        #   Visual Settings
        self.debug = False
        self.display_settings = DisplaySettings.hideAll

    def execute(self, commands, counter):
        #
        # Crops and rotates rectangle ROI selection,
        # returns resulting snippet image
        #

        # ensure image is valid
        try:
            self.image.shape
        except TypeError:
            print('In find_line.py, invalid image')
            sys.exit()
        # get image attributes
        imageWidth = self.image.shape[1]
        imageHeight = self.image.shape[0]
        imageChannel = self.image.shape[2]

        box_size = imageWidth * self.scale_factor

        if self.roi_rect is not None:
            # get rotated image snippet
            img2 = crop_rotated_rectangle(self.image, self.roi_rect.rectangle)

            # convert to grayscale and blur
            gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            kernel_size = 5
            blur_gray = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)

            # edge detection with Canny filter
            low_threshold = 50
            high_threshold = 150
            edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

            # Hough Line algo
            rho = 1  # distance resolution in pixels of the Hough grid
            theta = np.pi / 180  # angular resolution in radians of the Hough grid
            threshold = 15  # minimum number of votes (intersections in Hough grid cell)
            min_line_length = int(self.roi_rect.rectangle.attributes.height * 0.5)  # min number of pixels in a line
            max_line_gap = 20  # maximum gap in pixels between connectable line segments
            line_image = np.copy(img2) * 0  # creating a blank to draw lines on

            # Run Hough on edge detected image
            # Output "lines" is an array containing endpoints of detected line segments
            lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                                    min_line_length, max_line_gap)

            # create list of Line objects
            self.np_lines = [Line(x) for x in lines]
            # filter lines by angle settings
            filtered_lines = [x for i, x in enumerate(self.np_lines) if i not in self.edge_angle()]
            self.np_lines = filtered_lines[:]
            # filter lines by edge polarity setting
            filtered_lines = [x for i, x in enumerate(self.np_lines) if i not in self.edge_polarity()]
            self.np_lines = filtered_lines[:]
            # select line by edge selection
            if len(self.np_lines) > 0:
                self.found_line = self.edge_selection()

            # cv_line = line_to_plot.cv_format()
            # cv2.line(line_image, cv_line[0], cv_line[1], (0, 255, 0), 1)
            else:
                pass


    def edge_angle(self):
        # Filters through all results, eliminates candidates based on
        # angles being out of +/- angle threshold(degrees) relative to
        # left side of ROI, returns indices to delete
        del_index = []
        if len(self.np_lines) > 0:
            # delete any lines that are out of range
            for i, line in enumerate(self.np_lines):
                line_angle = np.rad2deg((line.get_angle())) + 90     # degrees
                if line_angle < - self.angle_threshold or line_angle > self.angle_threshold:
                    del_index.append(i)
        return del_index

    def edge_polarity(self, img):
        # Filters through all results, eliminates candidates based on
        # edge setting 0 = either, 1 = black to white, 2 = white to black
        # returns indices to delete

        del_index = []
        if self.edge_setting.value != EdgeSettings.either and len(self.np_lines) > 0:
            for i, line in enumerate(self.np_lines):
                # get normal vectors (l,r) about center point
                start, end = line.get_norm_vectors(scale=5)
                start = start.cv_format()
                end = end.cv_format()

                discrete_line = sciline(*start, *end)
                # combine results into array of row,col
                line_indicies = np.vstack((discrete_line[0], discrete_line[1])).T
                # sort arguments to always be descending x first
                line_indicies = line_indicies[line_indicies[:, 0].argsort()]

                # returns rows and cols, y and x are flipped
                pix_array = [img[y, x] for x, y in line_indicies]
                gradient = [int(pix_array[x + 1]) - int(pix_array[x]) for x in range(len(pix_array) - 1)]

                # if gradient is positve, indicates black to white transition
                if sum(gradient) / len(gradient) > 0:
                    # white to black, delete
                    if self.edge_setting.value == EdgeSettings.whiteToBlack:
                        del_index.append(i)
                        continue
                # white to black case
                else:
                    # black to white, delete
                    if self.edge_setting.value == EdgeSettings.blackToWhite:
                        del_index.append(i)
                        continue
        return del_index

    def edge_selection(self):
        # Returns index of line to use based on line_setting, scans from neg x to pos x
        # 0 = best score, 1 = first edge, 2 = last edge
        # returns indices to delete
        value = 0
        search_idx = 0
        if len(self.np_lines) > 0:
            if self.line_setting.value == LineSettings.bestScore:
                return 0

            elif self.line_setting.value == LineSettings.firstEdge:
                for i, line in enumerate(self.np_lines):
                    if line.center.x < value or i == 0:
                        value = line.center.x
                        search_idx = i
                return search_idx

            elif self.line_setting.value == LineSettings.lastEdge:
                for i, line in enumerate(self.np_lines):
                    if line.center.x > value or i == 0:
                        value = line.center.x
                        search_idx = i
                return search_idx
        else:
            return None

