import numpy as np
from typing import get_type_hints
import os
import cv2
from classes.point import Point
from classes.points import Points
from classes.rectangle import Rectangle, RectAttributes
from classes.roi_rectangle import ROIRectangle

wName = "test display"
imageWidth = 640
imageHeight = 480
cv2.namedWindow(wName)
cv2.setWindowProperty(wName, cv2.WND_PROP_TOPMOST, 1)
cv2.moveWindow(wName, 2000, 100)

image = np.ones([imageHeight, imageWidth, 3], dtype=np.uint8)  # OR read an image using imread()
image *= 255
rectangle = Rectangle(RectAttributes([100,100], 100, 100))
print(rectangle)

roi_rect = ROIRectangle(rectangle, image, wName, box_size=8)
roi_rect.plot(image)

# display the image
cv2.imshow(wName, roi_rect.image)
key = cv2.waitKey(0) & 0xFF