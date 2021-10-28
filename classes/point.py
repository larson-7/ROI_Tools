import numpy as np

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

    def cv_format(self):
        return int(self[0]), int(self[1])

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, x):
        self[0] = x

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, y):
        self[1] = y

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