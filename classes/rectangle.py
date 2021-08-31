import numpy as np
from classes.point import Point
from classes.points import Points, init_args
import cv2
from typing import Union

class RectAttributes:
    @init_args
    def __init__(self, center: Point = Point([0, 0]), width=0, height=0, rotation=0):
        print('constructing attributes')
        self.center = center
        self.width = width
        self.height = height
        self.rotation = rotation

    def __repr__(self):
        return 'Attributes(Center {0}, Width {1}, Height {2}, Rotation {3}) '\
            .format(self.center, self.width, self.height, self.rotation)

#  TODO: May want to just have a rectangle be composed of a point instead of subclassing it.
class Rectangle(Points):

    def __new__(cls, rect_attributes: RectAttributes = None, points: Points = None):
        # construct from attributes
        if rect_attributes is not None:
            print('constructing from attributes')
            super().__new__(cls.rect_from_attributes(rect_attributes))
        else:
            # a default value if the rect was constructed another
            # way, or inversely construct a RectAttributes from points
            return points

    def __init__(self, rect_attributes: RectAttributes):
        print('in rect constructor')
        print(self)
        self.attributes = rect_attributes

    def __str__(self):
        return 'Points(Top Left {0}, Top Right {1}, Bottom Right {2}, Bottom Left {3})'\
            .format(self.points[0], self.points[1], self.points[2], self.points[3]) + '\n' + self.attributes.__repr__()

    def get_center(self):
        self.attributes.center[0] = (self.points[0][0] + self.points[2][0]) / 2
        self.attributes.center[1] = (self.points[0][1] + self.points[2][1]) / 2

    def calc_attributes(self):
        self.get_center()
        self.attributes.width = np.linalg.norm(self.points[0] - self.points[1])
        self.attributes.height = np.linalg.norm(self.points[0] - self.points[3])

    def update(self, center: Point = None, width=None, height=None, rotation=None):
        if center is not None:
            self.attributes.center = center
        if width is not None:
            self.attributes.width = width
        if height is not None:
            self.attributes.height = height
        if rotation is not None:
            self.attributes.rotation = rotation

        self.rect_from_attributes()

    def cv_format(self):
        return ((self.attributes.center.x, self.attributes.center.y), (self.attributes.width, self.attributes.height),
                np.rad2deg(self.attributes.rotation))

    def plot(self, image, color=(0, 255, 0), thickness=1):
        box = cv2.boxPoints(self.cv_format())
        box = np.int0(box)
        cv2.drawContours(image, [box], -1, color, thickness)

    @property
    def center(self):
        return self.attributes.center

    @center.setter
    @init_args
    def center(self, center: Point):
        self.update(center=center)

    @property
    def width(self):
        return self.attributes.width

    @width.setter
    def width(self, width):
        self.update(width=width)

    @property
    def height(self):
        return self.attributes.height

    @height.setter
    def height(self, height):
        self.update(height=height)

    @property
    def rotation(self):
        return self.attributes.rotation

    @rotation.setter
    def rotation(self, rotation):
        self.update(rotation=rotation)

    @property
    def tl(self):
        return Point(self.points[0])

    @property
    def tr(self):
        return Point(self.points[1])

    @property
    def br(self):
        return Point(self.points[2])

    @property
    def bl(self):
        return Point(self.points[3])

    @init_args
    @classmethod
    def rect_from_attributes(cls, attributes):
        points = np.zeros((4,2))
        """
            Set points first from attributes, then rotate all of them by rotation attribute
        """
        # Top Left
        points[0][0] = attributes.center.x - attributes.width/2
        points[0][1] = attributes.center.y - attributes.height/2

        # Top Right
        points[1][0] = attributes.attributes.center.x + attributes.width/2
        points[1][1] = attributes.attributes.center.y - attributes.height/2

        # Bottom Right
        points[2][0] = attributes.attributes.center.x + attributes.width/2
        points[2][1] = attributes.attributes.center.y + attributes.height/2

        # Bottom Left
        points[3][0] = attributes.attributes.center.x - attributes.width/2
        points[3][1] = attributes.attributes.center.y + attributes.height/2

        points = Points.rotate(points, attributes.rotation, attributes.center)
        return points

    def check_is_rectangle(self):
        @init_args
        def is_orthogonal(a: Point, b: Point, c: Point):
            return (b.x - a.x) * (b.x - c.x) + (b.y - a.y) * (b.y - c.y) == 0

        return is_orthogonal(self.points[3], self.points[0], self.points[1]) and \
               is_orthogonal(self.points[0], self.points[1], self.points[2]) and \
               is_orthogonal(self.points[1], self.points[2], self.points[3])