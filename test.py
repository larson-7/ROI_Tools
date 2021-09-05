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
    image_dir = 'images'
    image_name = 'battery.JPG'
    image_filepath = os.path.join(image_dir, image_name)
    weld_img = cv2.imread(image_filepath)

    scale_percent = 20  # percent of original size
    width = int(weld_img.shape[1] * scale_percent / 100)
    height = int(weld_img.shape[0] * scale_percent / 100)
    dim = (width, height)

    # resize image
    resized = cv2.resize(weld_img, dim, interpolation=cv2.INTER_AREA)
    image = weld_img

    imageWidth = image.shape[0]
    imageHeight = image.shape[1]
    imageChannel = image.shape[2]

    cv2.namedWindow(wName)
    cv2.setWindowProperty(wName, cv2.WND_PROP_TOPMOST, 1)
    cv2.moveWindow(wName, 2000, 100)



    # image = np.ones([imageHeight, imageWidth, imageChannel], dtype=np.uint8)  # OR read an image using imread()
    # image *= 255
    rectangle = Rectangle(points=points)
    roi_rect = ROIRectangle(Rectangle(RectAttributes([100, 100], 200, 200)), image, wName, box_size=50)
    cv2.setMouseCallback(wName, roi_rect.dragrect)
    # keep looping until rectangle finalized
    while True:
        if roi_rect.updateimg:
            # display the image
            cv2.imshow(wName, roi_rect.image)
            roi_rect.updateimg = False
        key = cv2.waitKey(1) & 0xFF

        # if returnflag is True, break from the loop
        if roi_rect.return_flag:
            break

    # roi_rect.plot(image, (0, 0, 255))
    # cv2.imshow(wName, image)
    # key = cv2.waitKey(0) & 0xFF

    # test_rect = Rectangle(RectAttributes([100,100],10,10,0))
    # print('test rect', type(test_rect))
    # roi = ROIRectangle(test_rect)
