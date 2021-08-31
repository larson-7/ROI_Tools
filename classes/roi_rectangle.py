import numpy as np
from classes.point import Point
from classes.points import Points, to_point
from classes.rectangle import Rectangle
from classes.circle import Circle

class ROI_Rectangle(Rectangle):

    @to_point
    def __init__(self, rectangle: Rectangle):
        box_size = 5
        self.rectangle = rectangle

        self.tl_selection = Rectangle(self.rectangle.tl, box_size, box_size, self.rectangle.rotation)
        self.tm_selection = Rectangle((self.rectangle.tr - self.rectangle.tl)/2
                                      , box_size, box_size, self.rectangle.rotation)
        self.tr_selection = Rectangle(self.rectangle.tr, box_size, box_size, self.rectangle.rotation)
        self.br_selection = Rectangle(self.rectangle.br, box_size, box_size, self.rectangle.rotation)
        self.bm_selection = Rectangle((self.rectangle.bl - self.rectangle.br)/2
                                      , box_size, box_size, self.rectangle.rotation)
        self.bl_selection = Rectangle(self.rectangle.bl, box_size, box_size, self.rectangle.rotation)
        self.rotate = Circle(self.tm_selection.center + [0, 3/2 * box_size], box_size)

