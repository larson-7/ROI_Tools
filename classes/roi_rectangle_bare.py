import numpy as np
from classes.point import Point
from classes.points import Points, init_args
from classes.rectangle import Rectangle
from classes.circle import Circle


class ROIRectangle(Rectangle):

    @init_args
    def __init__(self, rectangle: Rectangle):
        # ROI geometry
        self.rectangle = rectangle
        self.tl_selection = None
        self.tm_selection = None
        self.tr_selection = None
        self.rm_selection = None
        self.br_selection = None
        self.bm_selection = None
        self.bl_selection = None
        self.lm_selection = None
        self.rotate_selection = None
        self.box_size = 5
        self.geometries = {}

        # calculate selection rectangles
        self.update()

    def update(self):
        self.tl_selection = Rectangle(rect_attributes=(self.rectangle.tl, self.box_size, self.box_size, self.rectangle.rotation))
        self.tm_selection = Rectangle(rect_attributes=((self.rectangle.tr - self.rectangle.tl)/2
                                      , self.box_size, self.box_size, self.rectangle.rotation))
        self.tr_selection = Rectangle(self.rectangle.tr, self.box_size, self.box_size, self.rectangle.rotation)
        self.rm_selection = Rectangle((self.rectangle.tr - self.rectangle.br)/2
                                      , self.box_size, self.box_size, self.rectangle.rotation)
        self.br_selection = Rectangle(self.rectangle.br, self.box_size, self.box_size, self.rectangle.rotation)
        self.bm_selection = Rectangle((self.rectangle.bl - self.rectangle.br)/2
                                      , self.box_size, self.box_size, self.rectangle.rotation)
        self.bl_selection = Rectangle(self.rectangle.bl, self.box_size, self.box_size, self.rectangle.rotation)
        self.lm_selection = Rectangle((self.rectangle.tl - self.rectangle.bl)/2
                                      , self.box_size, self.box_size, self.rectangle.rotation)
        self.rotate_selection = Circle(self.tm_selection.center + [0, 3/2 * self.box_size], self.box_size)

        # populate list of all geometries
        self.geometries.append(self.tl_selection)
        self.geometries.append(self.tm_selection)
        self.geometries.append(self.tr_selection)
        self.geometries.append(self.rm_selection)
        self.geometries.append(self.br_selection)
        self.geometries.append(self.bm_selection)
        self.geometries.append(self.bl_selection)
        self.geometries.append(self.lm_selection)
        self.geometries.append(self.rotate_selection)

    def plot(self, image, color=(0, 255, 0), thickness=1):
        for contour in self.geometries:
            contour.plot(image, color, thickness)
