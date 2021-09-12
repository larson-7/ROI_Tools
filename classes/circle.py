import numpy as np
from classes.point import Point
from classes.points import init_args
import cv2

class Circle:
    @init_args
    def __init__(self, center: Point = Point([0, 0]), diameter=0):
        self.center = center
        self.diameter = diameter


    def __repr__(self):
        return 'Circle - (center: {0}, diameter: {1})'.format(self.center, self.diameter)

    @property
    def x(self):
        return int(self.center.x)

    @x.setter
    def x(self, x):
        self.center.x = x

    @property
    def y(self):
        return int(self.center.y)

    @y.setter
    def y(self, y):
        self.center.y = y

    def point_inside(self, q_point: Point):
        magnitude = np.linalg.norm(self.center - q_point)
        if magnitude < self.diameter:
            return True
        else:
            return False


    def plot(self, image, color=(0, 255, 0), thickness=1):
        cv2.circle(image, (self.x, self.y), int(self.diameter/2), color, thickness)
