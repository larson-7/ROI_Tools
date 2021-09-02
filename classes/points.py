import numpy as np
from typing import get_type_hints
from classes.point import Point
import os


def _get_args_dict(fn, args, kwargs={}):
    args_names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
    return {**dict(zip(args_names, args)), **kwargs}


def init_args(method):
    def wrapper(*args):
        func_args = _get_args_dict(method, args)
        hints = get_type_hints(method)
        # ensure all inputted arguments match hinted types, if not construct object
        for hint in hints:
            if hint in func_args:
                if not isinstance(type(func_args[hint]), hints[hint]):
                    func_args[hint] = hints[hint](func_args[hint])
        args = func_args.values()
        result = method(*args)
        return result
    return wrapper


class Points(np.ndarray):
    def __new__(cls, list_of_points):

        if type(list_of_points) == 'numpy.ndarray':
            obj = list_of_points
        else:
            obj = np.vstack(list_of_points).view(cls)
        return obj

    @classmethod
    @init_args
    def translate(cls, points, offset: Point = Point([0, 0])):
        points = np.append(points, np.ones((points.shape[0], 1)), axis=1)
        a = np.array([[1, 0, offset.x],
                      [0, 1, offset.y],
                      [0, 0,     1   ]])

        result = points @ a.T
        return result[:, 0:2].view(cls)

    @classmethod
    @init_args
    def scale(cls, points, scale: Point = Point([1, 1])):
        points = np.append(points, np.ones((points.shape[0], 1)), axis=1)
        a = np.array([[scale[0],     0,     0],
                      [  0,       scale[1], 0],
                      [  0,         0,     1]])
        result = points @ a.T
        return result[:, 0:2].view(cls)

    @classmethod
    @init_args
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

    @classmethod
    @init_args
    def point_inside(cls, points, q_point: Point):
        """
        Based on the Point in Polygon Algo:
        https://towardsdatascience.com/is-the-point-inside-the-polygon-574b86472119
        Iterate through points and determine if result >0 for each line
        """
        result = 0

        for i in range(0, points.shape[0]):
            # eqn to find which side of line segment point lies
            if i < 3:
                test_expression = (q_point[1] - points[i][1]) * (points[i + 1][0] - points[i][0]) - \
                              (q_point[0] - points[i][0]) * (points[i + 1][1] - points[i][1])
            else:
                test_expression = (q_point[1] - points[i][1]) * (points[0][0] - points[i][0]) - \
                              (q_point[0] - points[i][0]) * (points[0][1] - points[i][1])
            if test_expression > 0:
                result += 1
            elif test_expression < 0:
                result -= 1
            else:
                return False

        # return true if all segments are consistent in either CCW or CW direction
        return abs(result) == points.shape[0]
