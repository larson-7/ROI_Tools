import numpy as np


class Points:

    def __init__(self, list_of_points):
        self.points = np.array(list_of_points)
        # self.points = np.vstack(list_of_points)

    def __str__(self):
        return np.array2string(self.points)

    def __add__



point1 = Points(([1,2], [2,4]))
print(point1)
