import numpy as np
import matplotlib.pyplot as plt
from classes.line import Line

points = np.array([[1, 4], [2, 5], [7, 6], [-1, -1]])

test_1d =np.array([1,2,3,4])

test_1d_rev = np.array([[1],[2],[3],[4]])

print(Line(points))
print(Line(test_1d))
print(Line(test_1d_rev))