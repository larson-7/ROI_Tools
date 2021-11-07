import math

import numpy as np
from matplotlib import pyplot as plt
from classes.rectangle import Rectangle
from classes.line import Line
from math import isclose
rect = np.array([[340.1042893,  106.41947853], [665.73452843,  47.0397904 ], [725.11421656, 372.67002953], [399.48397743, 432.04971766]])
rect = np.array([[443.89828813, -31.13778519], [792.1126566,   56.19922638], [710.12777388, 383.07455277], [361.91340541, 295.7375412 ]])
rect = np.array([[469.55772492, -16.73671388], [794.05327125,  74.21184525], [709.85163788, 374.63502168], [385.35609154, 283.68646255]])
def is_orthogonal(a, b, c):
    return isclose((b[0] - a[0]) * (b[0] - c[0]) + (b[1] - a[1]) * (b[1] - c[1]), 0, abs_tol=1e-3)
    # return (b[0] - a[0]) * (b[0] - c[0]) + (b[1] - a[1]) * (b[1] - c[1])

print(is_orthogonal(rect[3], rect[0], rect[1]))
print(is_orthogonal(rect[0], rect[1], rect[2]))
print(is_orthogonal(rect[1], rect[2], rect[3]))

x, y = rect.T
# plt.plot(x, y)
# plt.show()

# Test angle calculation, returining -180, should be zero
def get_angle(self):
    dx = self.points[0][0] - self.points[1][0]
    dy = self.points[0][1] - self.points[1][1]

    return math.atan((dy/dx))

points = Line(np.array([[74, 0], [74, 31]]))
print('get_angle: ', np.rad2deg(get_angle(points)))

