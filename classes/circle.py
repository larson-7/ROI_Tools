import numpy as np
from classes.point import Point
from classes.points import to_point

class Circle(Point):
    @to_point
    def __init__(self, center: Point, diameter):
        self.center = center
        self.diameter = diameter

    @property
    def x(self):
        return self.center.x

    @x.setter
    def x(self, x):
        self.center.x = x

    @property
    def y(self):
        return self.center.y

    @y.setter
    def y(self, y):
        self.center.y = y
