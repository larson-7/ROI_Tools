import numpy as np
from typing import get_type_hints


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

        obj = np.asarray(input_array).view(cls)
        return obj

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        """
        :return: 3rd dimension element. 0 if not defined
        """
        try:
            return self[2]
        except IndexError:
            return 0

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



    # def inside_points(self, point:Point):



if __name__ == "__main__":
    v1 = Point([2, 2])
    v2 = Point([1, 1])
    v3 = Point([1, 1])

    points = Points([v1, v2, v3])
    # scale_point = points.scale(points, [1, 1])
    # scale_point = points.translate(points, [2, 2])
    scale_point = points.rotate(points, np.deg2rad(90), [1, 1])

    print(scale_point)


