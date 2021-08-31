import numpy as np
from typing import get_type_hints
import os
import cv2
from classes.point import Point
from classes.points import Points
from classes.rectangle import Rectangle
from classes.roi_rectangle_bare import ROIRectangle

if __name__ == "__main__":
    def plot_rect(img, rect, color=(255, 255, 0)):
        box = cv2.boxPoints(rect.cv_format())
        box = np.int0(box)
        cv2.drawContours(img, [box], -1, color, 1)

    # v1 = Point([100, 100])
    # v2 = Point([125, 100])
    # v3 = Point([125, 125])
    # v4 = Point([100, 125])
    # points = Points([v1, v2, v3, v4])
    #
    # wName = "test display"
    # imageWidth = 640
    # imageHeight = 480
    # cv2.namedWindow(wName)
    # image = np.ones([imageHeight, imageWidth, 3], dtype=np.uint8)  # OR read an image using imread()
    #
    # rectangle = Rectangle(points)
    # plot_rect(image, rectangle, (0, 255, 0))

    # rectangle.rotation = np.deg2rad(45)
    # print(rectangle)
    # roi_rect = ROIRectangle(rectangle)
    # cv2.imshow(wName, image)
    # key = cv2.waitKey(0) & 0xFF

    test_rect = Rectangle(rect_attributes=([100,100],10,10,0))
if __name__ == "__md__":
    v1 = Point([100, 100])
    points = Points([v1])