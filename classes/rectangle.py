import numpy as np
from classes.point import Point
from classes.points import Points, init_args
import cv2



class RectAttributes:
    @init_args
    def __init__(self, center: Point = Point([0, 0]), width=0, height=0, rotation=0):
        self.center = center
        self.width = width
        self.height = height
        self.rotation = rotation

    def __repr__(self):
        return 'Attributes(Center {0}, Width {1}, Height {2}, Rotation {3}) '\
            .format(self.center, self.width, self.height, self.rotation)


class Rectangle:
    def __init__(self, rect_attributes: RectAttributes = None, points: Points = None):
        if rect_attributes is not None:
            self.points = Points(np.zeros((4, 2)))
            self.attributes = rect_attributes
            self.rect_from_attributes()
        else:
            self.points = points
            self.attributes = RectAttributes()
            if not self.check_is_rectangle():
                raise TypeError('points do not form a rectangle')
                exit()
            self.calc_attributes()

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
        cv2.drawContours(image, [box], 0, color, thickness)

    def rect_from_attributes(self):
        """
            Set points first from attributes, then rotate all of them by rotation attribute
        """
        # Top Left
        self.points[0][0] = self.attributes.center.x - self.width/2
        self.points[0][1] = self.attributes.center.y - self.height/2
        # Top Right
        self.points[1][0] = self.attributes.center.x + self.width/2
        self.points[1][1] = self.attributes.center.y - self.height/2
        # Bottom Right
        self.points[2][0] = self.attributes.center.x + self.width/2
        self.points[2][1] = self.attributes.center.y + self.height/2
        # Bottom Left
        self.points[3][0] = self.attributes.center.x - self.width/2
        self.points[3][1] = self.attributes.center.y + self.height/2
        # Rotate Points
        self.points = Points.rotate(self.points, self.attributes.rotation, self.attributes.center)

    def check_is_rectangle(self):
        @init_args
        def is_orthogonal(a: Point, b: Point, c: Point):
            return (b.x - a.x) * (b.x - c.x) + (b.y - a.y) * (b.y - c.y) == 0

        return is_orthogonal(self.points[3], self.points[0], self.points[1]) and \
               is_orthogonal(self.points[0], self.points[1], self.points[2]) and \
               is_orthogonal(self.points[1], self.points[2], self.points[3])

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

