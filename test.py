import numpy as np
from typing import get_type_hints
import os
import cv2
from classes.point import Point
from classes.points import Points
from classes.rectangle import Rectangle, RectAttributes
from classes.roi_rectangle import ROIRectangle

if __name__ == "__main__":

    v1 = Point([100, 100])
    v2 = Point([125, 100])
    v3 = Point([125, 125])
    v4 = Point([100, 125])
    points = Points([v1, v2, v3, v4])

    wName = "test display"
    imageWidth = 640
    imageHeight = 480
    cv2.namedWindow(wName)
    cv2.setWindowProperty(wName, cv2.WND_PROP_TOPMOST, 1)
    cv2.moveWindow(wName, 2000, 100)

    image = np.ones([imageHeight, imageWidth, 3], dtype=np.uint8)  # OR read an image using imread()
    image *= 255
    rectangle = Rectangle(points=points)
    # plot_rect(image, rectangle, (0, 255, 0))
    roi_rect = ROIRectangle(Rectangle(RectAttributes([100, 100], 20, 20)), image, wName)
    cv2.setMouseCallback(wName, roi_rect.dragrect)

    # keep looping until rectangle finalized
    while True:
        # display the image
        cv2.imshow(wName, roi_rect.image)
        key = cv2.waitKey(15) & 0xFF

        # if returnflag is True, break from the loop
        if roi_rect.return_flag:
            break

    # roi_rect.plot(image, (0, 0, 255))
    # cv2.imshow(wName, image)
    # key = cv2.waitKey(0) & 0xFF

    # test_rect = Rectangle(RectAttributes([100,100],10,10,0))
    # print('test rect', type(test_rect))
    # roi = ROIRectangle(test_rect)
