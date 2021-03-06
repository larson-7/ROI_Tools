import numpy as np
from typing import get_type_hints
import os
import cv2


def _get_args_dict(fn, args, kwargs={}):
    args_names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
    return {**dict(zip(args_names, args)), **kwargs}


def to_point(method):
    def wrapper(*args):
        # get dict of all arg names and values
        func_args = _get_args_dict(method, args)
        # get list all function parameters hinted types
        hints = get_type_hints(method)

        # ensure all inputted arguments match hinted types, if not construct object
        for hint in hints:
            if hint in func_args:
                if not isinstance(type(func_args[hint]), hints[hint]):
                    func_args[hint] = hints[hint](func_args[hint])
        # assign func_args dict values to args
        args = func_args.values()
        #call method
        result = method(*args)
        return result
    return wrapper


class Point(np.ndarray):
    """
    n-dimensional point used for locations.
    inherits +, -, * (as dot-product)
    > p1 = Point([1, 2])
    > p2 = Point([4, 5])
    > p1 + p2
    Point([5, 7])
    """
    def __new__(cls, input_array=(0, 0)):
        """
        :param cls:
        :param input_array: Defaults to 2d origin
        """

        obj = np.asarray(input_array, dtype='f').view(cls)
        return obj

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, x):
        self.point[0] = x

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, y):
        self.point[1] = y

    @property
    def z(self):
        """
        :return: 3rd dimension element. 0 if not defined
        """
        try:
            return self[2]
        except IndexError:
            return 0

    @z.setter
    def z(self, z):
        """
        :return: 3rd dimension element. 0 if not defined
        """
        try:
            self.point[2] = z
        except IndexError:
            raise IndexError('Out of index, no Z defined originally')

    def __eq__(self, other):
        return np.array_equal(self, other)

    def __ne__(self, other):
        return not np.array_equal(self, other)

    def __iter__(self):
        for x in np.nditer(self):
            yield x.item()

    def dist(self, other):
        """
        Both points must have the same dimensions
        :return: Euclidean distance
        """
        return np.linalg.norm(self - other)


class Points(np.ndarray):
    def __new__(cls, list_of_points):
        """
        :param cls:
        :param list_of_points: needs multiple points or ndarrays
        """
        if type(list_of_points) == 'numpy.ndarray':
            obj = list_of_points
        else:
            obj = np.vstack(list_of_points).view(cls)
        return obj

    @classmethod
    @to_point
    def translate(cls, points, offset: Point = Point([0, 0])):
        points = np.append(points, np.ones((points.shape[0], 1)), axis=1)
        a = np.array([[1, 0, offset.x],
                      [0, 1, offset.y],
                      [0, 0,     1   ]])

        result = points @ a.T
        return result[:, 0:2].view(cls)

    @classmethod
    @to_point
    def scale(cls, points, scale: Point = Point([1, 1])):
        points = np.append(points, np.ones((points.shape[0], 1)), axis=1)
        a = np.array([[scale[0],     0,     0],
                      [  0,       scale[1], 0],
                      [  0,         0,     1]])
        result = points @ a.T
        return result[:, 0:2].view(cls)

    @classmethod
    @to_point
    def rotate(cls, points, angle, origin: Point = Point([0, 0])):
        print(points)
        cos = np.cos(angle)
        sin = np.sin(angle)
        a = np.array([[cos, -sin, 0],
                      [sin, cos,  0],
                      [0,   0,    1]])
        if origin == [0, 0]:
            points = np.append(points, np.ones((points.shape[0], 1)), axis=1)
            result = points @ a.T
            return result[:, 0:2].view(cls)
        else:
            points = points.translate(points, -origin)
            points = points.rotate(points, angle, [0, 0])
            points = points.translate(points, origin)
            return points

    @classmethod
    @to_point
    def check_inside(cls, points, q_point: Point):
        """
        Based on the Point in Polygon Algo:
        https://towardsdatascience.com/is-the-point-inside-the-polygon-574b86472119
        Iterate through points and determine if result >0 for each line
        """
        result = 0

        for i in range(0, points.shape[0] - 1):
            # eqn to find which side of line segment point lies
            test_expression = (q_point[1] - points[i][1]) * (points[i + 1][0] - points[i][0]) - \
                              (q_point[0] - points[i][0]) * (points[i + 1][1] - points[i][1])

            if test_expression > 0:
                result += 1
            elif test_expression < 0:
                result -= 1
            else:
                return False

        # return true if all segments are consistent in either CCW or CW direction
        return abs(result) == points.shape[0]


class RectAttributes:
    def __init__(self, center: Point = Point([0, 0]), width=0, height=0, rotation=0):
        self.center = center
        self.width = width
        self.height = height
        self.rotation = rotation

    def __repr__(self):
        return 'Attributes(Center {0}, Width {1}, Height {2}, Rotation {3}) '\
            .format(self.center, self.width, self.height, self.rotation)


class Rectangle(Points):
    def __init__(self, points: Points = None, rect_attributes: RectAttributes = None):
        self.points = None

        # Construct with just points, check that the points form a rectangle first
        if rect_attributes is None and points is not None:
            self.points = points
            self.attributes = RectAttributes()

            if not self.check_is_rectangle():
                raise ValueError('Points do not form a rectangle')
                os.exit()
            else:
                self.calc_attributes()

        # Build rectangle from attributes
        elif RectAttributes is not None:
            self.attributes = rect_attributes
            self.construct_rect_from_attributes()

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

        self.construct_rect_from_attributes()

    def cv_format(self):
        return ((self.attributes.center.x, self.attributes.center.y), (self.attributes.width, self.attributes.height),
                self.attributes.rotation)

    @property
    def center(self):
        return self.attributes.center

    @center.setter
    @to_point
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

    @to_point
    def construct_rect_from_attributes(self):
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

        self.points = Points.rotate(self.points, self.attributes.rotation, self.attributes.center)

    def check_is_rectangle(self):
        @to_point
        def is_orthogonal(a: Point, b: Point, c: Point):
            return (b.x - a.x) * (b.x - c.x) + (b.y - a.y) * (b.y - c.y) == 0

        return is_orthogonal(self.points[3], self.points[0], self.points[1]) and \
               is_orthogonal(self.points[0], self.points[1], self.points[2]) and \
               is_orthogonal(self.points[1], self.points[2], self.points[3])


if __name__ == "__main__":
    def plot_rect(img, rect, color=(255, 255, 0)):
        box = cv2.boxPoints(rect.cv_format())
        box = np.int0(box)
        cv2.drawContours(img, [box], -1, color, 1)

    v1 = Point([100, 100])
    v2 = Point([200, 100])
    v3 = Point([200, 200])
    v4 = Point([100, 200])
    points = Points([v1, v2, v3, v4])

    wName = "test display"
    imageWidth = 640
    imageHeight = 480
    cv2.namedWindow(wName)
    image = np.ones([imageHeight, imageWidth, 3], dtype=np.uint8)  # OR read an image using imread()

    rectangle = Rectangle(points)
    print(rectangle)

    # plot_rect(image, rectangle, (0, 255, 0))
    #
    # rectangle.rotation = np.deg2rad(30)
    # plot_rect(image, rectangle, (255, 0, 255))
    #
    # cv2.imshow(wName, image)
    # key = cv2.waitKey(0) & 0xFF
