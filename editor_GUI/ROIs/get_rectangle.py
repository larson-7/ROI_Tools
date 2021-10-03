import numpy as np
from typing import get_type_hints
import os
import cv2
from classes.point import Point
from classes.points import Points
from classes.rectangle import Rectangle, RectAttributes
from classes.roi_rectangle import ROIRectangle

if __name__ == "__main__":

    wName = "Place Rectangle"
    image_dir = '../../images'
    image_name = 'battery.JPG'
    image_filepath = os.path.join(image_dir, image_name)
    load_img = True

    if load_img:
        weld_img = cv2.imread(image_filepath)

        scale_percent = 30  # percent of original size
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
