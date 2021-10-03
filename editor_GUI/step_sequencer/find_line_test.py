import numpy as np
from typing import get_type_hints
import os
import cv2
from classes.point import Point
from classes.points import Points
from classes.rectangle import Rectangle, RectAttributes
from classes.roi_rectangle import ROIRectangle
from editor_GUI.ROIs.rotated_rect_crop import inside_rect, rect_bbx, crop_rotated_rectangle

if __name__ == "__main__":

    wName = "Place Rectangle"
    image_dir = '../../images'
    image_name = 'test2.png'
    image_filepath = os.path.join(image_dir, image_name)
    load_img = True

    if load_img:
        weld_img = cv2.imread(image_filepath)

        scale_percent = 130  # percent of original size
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
            print(roi_rect.rectangle)
            break

        # if returnflag is True, break from the loop
        if roi_rect.return_flag:
            break

img2 = crop_rotated_rectangle(image, roi_rect.rectangle)
cv2.namedWindow('output')

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
min_line_length = int(roi_rect.rectangle.attributes.height * 0.5)  # minimum number of pixels making up a line
max_line_gap = 20  # maximum gap in pixels between connectable line segments
line_image = np.copy(img2) * 0  # creating a blank to draw lines on

lines = cv2.HoughLines(edges, rho, theta, threshold)
print(lines)

# Run Hough on edge detected image
# Output "lines" is an array containing endpoints of detected line segments
lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                    min_line_length, max_line_gap)

for line in lines:
    for x1,y1,x2,y2 in line:
        cv2.line(line_image,(x1,y1),(x2,y2),(255,0,0),5)

# Draw the lines on the  image
lines_edges = cv2.addWeighted(img2, 0.8, line_image, 1, 0)

cv2.imshow('output', lines_edges)
key = cv2.waitKey(-1) & 0xFF


