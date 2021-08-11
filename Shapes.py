import math
import numpy as np

class Fixture:
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.angle = angle


class Point:
    def __init__(self, x=0, y=0, fixture=Fixture(0,0)):
        self.x = x
        self.y = y
        self.fixture = fixture

    def __repr__(self):
        return 'Point: ({0},{1})'.format(self.x, self.y)

    def __add__(self, translation):
        if isinstance(translation, Point):
            return type(self)(self.x + translation.x, self.y + translation.y, self.fixture)
        else:
            print('new point created: {}'.format(translation))
            new_point = Point(*translation)
            return type(self)(self.x + new_point.x, self.y + new_point.y, self.fixture)

    def __abs__(self):
        return type(self)(abs(self.x), abs(self.y))

class Line:
    def __init__(self, point_1=Point(0, 0), point_2=Point(0, 0), fixture=Fixture(0, 0)):
        self.point_1 = point_1
        self.point_2 = point_2
        self.fixture = fixture




def rotate(p, origin=(0, 0), degrees=0):
    angle = np.deg2rad(degrees)
    R = np.array([[np.cos(angle), -np.sin(angle)],
                  [np.sin(angle),  np.cos(angle)]])
    o = np.atleast_2d(origin)
    p = np.atleast_2d(p)
    return np.squeeze((R @ (p.T-o.T) + o.T).T)


points=[(200, 300), (100, 300)]
origin=(100,100)

new_points = rotate(points, origin=origin, degrees=10)
print(new_points)