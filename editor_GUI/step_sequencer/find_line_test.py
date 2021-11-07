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


def midpoint(x1, y1, x2, y2):
    return (int((x1 + x2)/2), int((y1 + y2)/2))

class LineSettings(enum.Enum):
    bestScore = 0
    firstEdge = 1
    lastEdge = 2

class EdgeSettings(enum.Enum):
    either = 0
    blackToWhite = 1
    whiteToBlack = 2


if __name__ == "__main__":

    wName = "Place Rectangle"
    image_dir = '../../images'
    image_name = 'test4.png'
    image_filepath = os.path.join(image_dir, image_name)
    load_img = True

    if load_img:
        weld_img = cv2.imread(image_filepath)

        scale_percent = 40 # percent of original size
        width = int(weld_img.shape[1] * scale_percent / 100)
        height = int(weld_img.shape[0] * scale_percent / 100)
        dim = (width, height)
        # resize image
        resized = cv2.resize(weld_img, dim, interpolation=cv2.INTER_AREA)
        image = resized
        imageWidth = image.shape[1]
        imageHeight = image.shape[0]
        imageChannel = image.shape[2]
    else:
        imageWidth = 480
        imageHeight = 600
        imageChannel = 3
        image = np.ones([imageHeight, imageWidth, imageChannel], dtype=np.uint8)  # OR read an image using imread()
        image *= 255

    scale_factor = 0.025
    box_size = imageWidth * scale_factor

    cv2.namedWindow(wName)
    cv2.setWindowProperty(wName, cv2.WND_PROP_TOPMOST, 1)
    # cv2.moveWindow(wName, 2000, 100)

    roi_rect = ROIRectangle(Rectangle(RectAttributes([100, 100], 200, 200)), image, wName, box_size=box_size,
                            thickness=box_size/5)
    cv2.setMouseCallback(wName, roi_rect.dragrect)
    # keep looping until rectangle finalized
    while True:
        if roi_rect.updateimg:
            # display the image
            cv2.imshow(wName, roi_rect.image)
            roi_rect.updateimg = False
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        if key == 13:
            break

        # if returnflag is True, break from the loop
        if roi_rect.return_flag:
            break

    # cv2.destroyWindow(wName)
    time.sleep(0.5)
    start_time = time.time()
    img2, cropped_ROI = crop_rotated_rectangle(image, roi_rect.rectangle)
    cv2.namedWindow('output')
    cv2.imshow('rotated rect', img2)

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
    #TODO : put this back to 0.50, should only be trying to find the line close to the size of the ROI
    min_line_length = int(roi_rect.rectangle.attributes.height * 0.25)  # minimum number of pixels making up a line
    max_line_gap = 20  # maximum gap in pixels between connectable line segments
    line_image = np.copy(img2) * 0  # creating a blank to draw lines on

    # lines = cv2.HoughLines(edges, rho, theta, threshold)

    # Run Hough on edge detected image
    # Output "lines" is an array containing endpoints of detected line segments
    lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                        min_line_length, max_line_gap)

    # create list of Line objects
    np_lines = [Line(x) for x in lines]
    # plot all lines in red
    for i, line in enumerate(np_lines):
        cv_line = line.cv_format()
        print(f'{i=}', f'{line=}')
        cv2.line(line_image, cv_line[0], cv_line[1], (0, 0, 255), 1)
        cv2.putText(line_image, 'Line: {}'.format(i), line.start.cv_format(), cv2.FONT_HERSHEY_SIMPLEX, .4, (0, 0, 255),
                    1, cv2.LINE_AA)

    # Draw the lines on the  image
    lines_edges = cv2.addWeighted(img2, 0.5, line_image, 1, 0)
    cv2.imshow('output', lines_edges)
    del_index = []
    # TODO Functionize all line threshold tools, allow for plotting or not and enable debugging or not
    if len(np_lines) > 0:
        # ###############
        # Edge Angle
        # ###############
        del_index.clear()
        angle_threshold = 5     # degrees +/-

        # delete any lines that are out of range
        for i, line in enumerate(np_lines):
            line_angle = np.rad2deg((line.get_angle())) - 90     # degrees
            if -angle_threshold < line_angle < angle_threshold:
                print('keep index {}'.format(i), line_angle)
                pass
            else:
                print('delete index {}'.format(i), line_angle)
                del_index.append(i)
        # create new array of in range values
        filtered_np_lines = [x for i, x in enumerate(np_lines) if i not in del_index]
        np_lines = filtered_np_lines[:]
        filtered_np_lines.clear()
        del_index.clear()

    # ###############
    # Edge Polarity
    # ###############
    edge_setting = EdgeSettings.whiteToBlack

    # if edge polarity is set to either, skip all polarity checks
    if edge_setting.value != 0:

        for i, line in enumerate(np_lines):
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
            pix_array = [gray[y, x] for x, y in line_indicies]
            gradient = [int(pix_array[x + 1]) - int(pix_array[x]) for x in range(len(pix_array) - 1)]

            # if gradient is positve, indicates black to white transition
            if sum(gradient)/len(gradient) > 0:
                # white to black, delete
                if edge_setting.value == 2:
                    del_index.append(i)
                    continue
            # white to black case
            else:
                # black to white, delete
                if edge_setting.value == 1:
                    del_index.append(i)
                    continue
            # plot normal search path
            cv2.line(line_image, start, end, (255, 0, 255), 1)
        # create new array of in range values
        filtered_np_lines = [x for i, x in enumerate(np_lines) if i not in del_index]
        np_lines = filtered_np_lines[:]

    if len(np_lines) > 0:
        # ###############
        # Edge Selection
        # ###############
        line_setting = LineSettings.lastEdge

        # best score
        if line_setting.value == 0:
            line_to_plot = np_lines[0]
        # first edge
        elif line_setting.value == 1:
            value = 0
            search_idx = 0
            for i, line in enumerate(np_lines):
                if line.center.x < value or i == 0:
                    value = line.center.x
                    search_idx = i
            line_to_plot = np_lines[search_idx]
        # last edge
        elif line_setting.value == 2:
            value = 0
            search_idx = 0
            for i, line in enumerate(np_lines):
                if line.center.x > value or i == 0:

                    search_idx = i
            line_to_plot = np_lines[search_idx]
            start, end = line_to_plot.cv_format()
        cv2.line(line_image, start, end, (0, 255, 0), 1)

        rotated = Points.rotate(line_to_plot.points, roi_rect.rectangle.attributes.rotation, cropped_ROI.attributes.center)
        translate = Points.translate(rotated, cropped_ROI.tl)
        # center_offset = (crop_center - line_to_plot.center)
        # translate_to_center = Points.translate(line_to_plot.points, center_offset)
        # rotated = Points.rotate(translate_to_center, roi_rect.rectangle.attributes.rotation, crop_center)
        # translate_to_center = Points.translate(rotated, -center_offset)
        # translate = Points.translate(translate_to_center, crop_center.tl)

        # translate = line_to_plot.points.translate(line_to_plot.points, roi_rect.rectangle.tl)
        # rotated = Points.rotate(translate, -roi_rect.rectangle.attributes.rotation, crop_center)
        translate = translate.astype(int)
        translate_start = tuple(translate[0])
        translate_end = tuple(translate[1])
        # plot selected line
        # cv_line = line_to_plot.cv_format()
        cv2.line(image, translate_start, translate_end, (0, 255, 0), 3)
        # cv2.putText(line_image, 'Line: {}'.format(i), line_to_plot.start.cv_format(), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
        #             (0, 255, 0), 1, cv2.LINE_AA)
        cv2.imshow(wName, image)

        # Draw the lines on the  image
        lines_edges = cv2.addWeighted(img2, 0.5, line_image, 1, 0)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f'{elapsed_time=}')
        cv2.imshow('output', lines_edges)

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == 13:
                break
        cv2.destroyWindow('output')
    else:
        print('No Lines Found, exiting ...')