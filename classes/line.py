import numpy as np
from classes.point import Point
from classes.points import Points, init_args
import cv2


class Line:
    @init_args
    def __init__(self, points: np.ndarray = None, start_point: Point = None, end_point: Point = Point):
        self.points = Points(np.zeros((2, 2)))
        self.center = Point([0, 0])
        self.length = 0
        self.angle = 0

        if start_point is not None and end_point is  not None:
            self.points[0] = start_point
            self.points[1] = end_point
        else:
            # 2x2 numpy array
            if points.shape[0] == 2 and points.shape[1] == 2:
                self.points[0] = points[0]
                self.points[1] = points[1]
            # (4, ) numpy array
            elif len(points.shape) == 1 and points.shape[0] == 4:
                self.points[0] = points[:2]
                self.points[1] = points[2:4]
            # 1x4 numpy array
            elif points.shape[0] == 4 and points.shape[1] == 1:
                self.points[0] = points[:2, 0]
                self.points[1] = points[2:4, 0]
            # 1x4 numpy array
            elif points.shape[0] == 1 and points.shape[1] == 4:
                self.points[0] = points[0, :2]
                self.points[1] = points[0, 2:4]
            # if there are more than 2 points, do a best fit line
            elif points.shape[0] > 2 and points.shape[1] == 2:
                self.points = self.best_fit_line(points)

            else:
                raise TypeError('Need at least two points')
                exit()

        # Calc line attributes after either defining points or start and end point
        self.calc_attributes()

    def __str__(self):
        return 'Line: (Start Point {0}, Center Point {1}, End Point {2})'\
            .format(self.points[0], self.center, self.points[1])

    def get_center(self):
        return Point((self.points[0] + self.points[1]) / 2)

    def calc_attributes(self):
        self.center = self.get_center()
        self.length = np.linalg.norm(self.points[0] - self.points[1])
        self.angle = self.get_angle()

    def cv_format(self):
        return ((int(self.points[0][0]), int(self.points[0][1])), (int(self.points[1][0]), int(self.points[1][1])))

    def plot(self, image, color=(0, 255, 0), thickness=1):
        cv2.line(image, self.cv_format(), color, thickness)

    def best_fit_line(self, points):
        # sort points
        ind = np.lexsort((points[:, 1], points[:, 0]))
        # least squares best fit line
        x, y = points[ind].T
        A = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(A, y, rcond=None)[0]
        # new line
        new_points = np.vstack([x, m * x + c]).T
        return np.array([new_points[0], new_points[-1]])

    def get_norm_vectors(self, scale=1):
        # Get left and right unit vectors about the center point of line
        # A - B
        dx = self.points[1][0] - self.points[0][0]
        dy = self.points[1][1] - self.points[0][1]
        # resultant array
        r = np.array([dx, dy])
        # left normal result
        rnl = np.array([-r[1], r[0]])
        # right normal result
        rnr = np.array([r[1], -r[0]])
        # get magnitude
        norm = np.linalg.norm(rnl)

        return rnl * (scale / norm) + self.center, rnr * (scale / norm) + self.center

    def get_angle(self):
        dx = self.points[1][0] - self.points[0][0]
        dy = self.points[1][1] - self.points[0][1]
        return np.arctan(dy/dx)

    @property
    def start(self):
        return Point(self.points[0])

    @property
    def end(self):
        return Point(self.points[1])
